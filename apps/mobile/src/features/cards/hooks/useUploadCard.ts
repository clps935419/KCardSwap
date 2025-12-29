/**
 * Upload Card Hook
 * 完整的卡片上傳流程：
 * 1. 選取/拍照圖片 (M201)
 * 2. 取得 Signed URL (M202)
 * 3. 上傳到 GCS (M203)
 * 4. 產生縮圖並快取 (M203A)
 */

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getUploadUrlApiV1CardsUploadUrlPostMutation,
  confirmCardUploadApiV1CardsCardIdConfirmUploadPostMutation,
} from '@/src/features/cards/api/cardsApi';
import {
  pickImageFromCamera,
  pickImageFromGallery,
  validateImageSize,
} from '@/src/features/cards/services/imagePickerService';
import { uploadWithRetry, isSignedUrlExpired } from '@/src/features/cards/services/uploadService';
import { generateThumbnail, saveThumbnailToCache } from '@/src/features/cards/services/thumbnailService';
import type { ImagePickResult, CardRarity } from '@/src/features/cards/types';
import { cardsKeys } from '@/src/features/cards/hooks/useCards';

/**
 * 上傳進度狀態
 */
export interface UploadProgress {
  step: 'picking' | 'requesting' | 'uploading' | 'confirming' | 'thumbnail' | 'complete';
  progress: number; // 0-100
  message: string;
}

/**
 * 上傳選項
 */
export interface UploadCardOptions {
  idol?: string;
  idol_group?: string;
  album?: string;
  version?: string;
  rarity?: CardRarity;
}

/**
 * Hook: 上傳卡片
 * 整合 M201, M202, M203, M203A, M203B
 */
export function useUploadCard() {
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    step: 'picking',
    progress: 0,
    message: '準備中...',
  });

  // SDK mutations
  const getUploadUrlMutation = useMutation(getUploadUrlApiV1CardsUploadUrlPostMutation());
  const confirmUploadMutation = useMutation(
    confirmCardUploadApiV1CardsCardIdConfirmUploadPostMutation()
  );

  const mutation = useMutation({
    mutationFn: async ({
      imageResult,
      options,
    }: {
      imageResult: ImagePickResult;
      options?: UploadCardOptions;
    }) => {
      try {
        // Step 1: 驗證圖片大小
        const sizeValidation = validateImageSize(imageResult.fileSize);
        if (!sizeValidation.valid) {
          throw new Error(sizeValidation.error);
        }

        // Step 2: 取得 Signed URL (M202) - 使用 SDK mutation
        setUploadProgress({
          step: 'requesting',
          progress: 20,
          message: '取得上傳連結...',
        });

        const uploadUrlResponse = await getUploadUrlMutation.mutateAsync({
          body: {
            content_type: imageResult.type,
            file_size_bytes: imageResult.fileSize,
            idol: options?.idol,
            idol_group: options?.idol_group,
            album: options?.album,
            version: options?.version,
            rarity: options?.rarity,
          },
        });

        // 檢查 Signed URL 是否已過期
        if (isSignedUrlExpired(uploadUrlResponse.expires_at)) {
          throw new Error('上傳連結已過期，請重試');
        }

        // Step 3: 上傳到 GCS (M203)
        setUploadProgress({
          step: 'uploading',
          progress: 40,
          message: '上傳中...',
        });

        await uploadWithRetry({
          uri: imageResult.uri,
          uploadUrl: uploadUrlResponse.upload_url,
          method: uploadUrlResponse.method,
          headers: uploadUrlResponse.required_headers,
          onProgress: (progress) => {
            setUploadProgress({
              step: 'uploading',
              progress: 40 + progress * 0.3, // 40-70%
              message: `上傳中... ${progress.toFixed(0)}%`,
            });
          },
        });

        // Step 4: 確認上傳 (M203B) - 使用 SDK mutation
        setUploadProgress({
          step: 'confirming',
          progress: 75,
          message: '確認上傳...',
        });

        try {
          await confirmUploadMutation.mutateAsync({
            path: {
              card_id: uploadUrlResponse.card_id,
            },
          });
        } catch (error) {
          // 確認上傳失敗是致命錯誤，需要重新上傳
          console.error('確認上傳失敗', error);
          throw new Error(
            `確認上傳失敗：${(error as Error).message}。請重新上傳。`
          );
        }

        // Step 5: 產生縮圖並快取 (M203A)
        setUploadProgress({
          step: 'thumbnail',
          progress: 85,
          message: '產生縮圖...',
        });

        try {
          const thumbnailUri = await generateThumbnail(imageResult.uri);
          await saveThumbnailToCache(
            uploadUrlResponse.card_id,
            uploadUrlResponse.image_url,
            thumbnailUri
          );
        } catch (error) {
          // 縮圖產生失敗不影響上傳流程
          console.error('縮圖產生失敗', error);
        }

        // Step 6: 完成
        setUploadProgress({
          step: 'complete',
          progress: 100,
          message: '上傳完成！',
        });

        return uploadUrlResponse;
      } catch (error) {
        console.error('上傳卡片失敗', error);
        throw error;
      }
    },
    onSuccess: () => {
      // 刷新卡片列表
      queryClient.invalidateQueries({ queryKey: cardsKeys.lists() });
      // 刷新配額狀態
      queryClient.invalidateQueries({ queryKey: cardsKeys.quota() });
    },
  });

  /**
   * 從相機拍照並上傳
   */
  const uploadFromCamera = async (options?: UploadCardOptions) => {
    setUploadProgress({
      step: 'picking',
      progress: 10,
      message: '開啟相機...',
    });

    const imageResult = await pickImageFromCamera();
    if (!imageResult) {
      // 使用者取消
      return null;
    }

    return mutation.mutateAsync({ imageResult, options });
  };

  /**
   * 從相簿選取並上傳
   */
  const uploadFromGallery = async (options?: UploadCardOptions) => {
    setUploadProgress({
      step: 'picking',
      progress: 10,
      message: '選取圖片...',
    });

    const imageResult = await pickImageFromGallery();
    if (!imageResult) {
      // 使用者取消
      return null;
    }

    return mutation.mutateAsync({ imageResult, options });
  };

  return {
    uploadFromCamera,
    uploadFromGallery,
    uploadProgress,
    isUploading: mutation.isPending,
    error: mutation.error,
    reset: mutation.reset,
  };
}
