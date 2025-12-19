/**
 * Upload Card Screen
 * M201-M203A: 完整的卡片上傳流程
 * 
 * 功能：
 * - 選擇圖片來源（相機/相簿）
 * - 填寫卡片資訊
 * - 顯示上傳進度
 * - 錯誤處理（配額、檔案大小、網路等）
 * 
 * 使用 Gluestack UI 元件
 */

import React, { useState } from 'react';
import { ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import {
  Box,
  Text,
  Input,
  Pressable,
  Spinner,
  Button,
  ButtonText,
  Heading,
} from '@/src/shared/ui/components';
import { useUploadCard } from '@/src/features/cards/hooks/useUploadCard';
import type { CardRarity, LimitExceededError } from '@/src/features/cards/types';

const RARITY_OPTIONS: { label: string; value: CardRarity }[] = [
  { label: '普通', value: 'common' },
  { label: '稀有', value: 'rare' },
  { label: '史詩', value: 'epic' },
  { label: '傳說', value: 'legendary' },
];

export function UploadCardScreen() {
  const router = useRouter();
  const { uploadFromCamera, uploadFromGallery, uploadProgress, isUploading, error } =
    useUploadCard();

  const [idol, setIdol] = useState('');
  const [idolGroup, setIdolGroup] = useState('');
  const [album, setAlbum] = useState('');
  const [version, setVersion] = useState('');
  const [rarity, setRarity] = useState<CardRarity>('common');
  const [lastUploadSource, setLastUploadSource] = useState<'camera' | 'gallery' | null>(null);

  const handleUpload = async (source: 'camera' | 'gallery') => {
    setLastUploadSource(source);
    
    try {
      const uploadFn = source === 'camera' ? uploadFromCamera : uploadFromGallery;

      const result = await uploadFn({
        idol: idol || undefined,
        idol_group: idolGroup || undefined,
        album: album || undefined,
        version: version || undefined,
        rarity,
      });

      if (result) {
        Alert.alert('上傳成功', '卡片已成功上傳！', [
          {
            text: '確定',
            onPress: () => router.back(),
          },
        ]);
      }
    } catch (err: any) {
      // 處理不同類型的錯誤
      handleUploadError(err);
    }
  };

  const handleUploadError = (err: any) => {
    const error = err as LimitExceededError;

    // 配額超過錯誤
    if (error.code === 'LIMIT_EXCEEDED') {
      const limitType = error.limit_type;
      let message = '上傳失敗';

      if (limitType === 'daily') {
        message = `今日上傳次數已達上限（${error.limit}張/日）。明天再來吧！`;
      } else if (limitType === 'storage') {
        message = `儲存空間已滿（${((error.limit || 0) / 1024 / 1024 / 1024).toFixed(2)}GB）。請刪除部分卡片後再試。`;
      } else if (limitType === 'size') {
        message = `檔案大小超過限制（最大 10MB）。`;
      }

      Alert.alert('配額限制', message);
      return;
    }

    // 權限錯誤
    if (error.message?.includes('權限')) {
      Alert.alert('權限不足', error.message);
      return;
    }

    // Signed URL 相關錯誤
    if (error.message?.includes('過期') || error.statusCode === 403) {
      Alert.alert('上傳失敗', '上傳連結已過期，請重試', [
        { 
          text: '重試', 
          onPress: () => lastUploadSource && handleUpload(lastUploadSource)
        },
      ]);
      return;
    }

    // 網路錯誤
    if (error.message?.includes('網路')) {
      Alert.alert('網路錯誤', '請檢查網路連線後重試', [
        { 
          text: '重試', 
          onPress: () => lastUploadSource && handleUpload(lastUploadSource)
        },
      ]);
      return;
    }

    // 一般錯誤
    Alert.alert('上傳失敗', error.message || '請稍後再試');
  };

  return (
    <ScrollView className="flex-1 bg-gray-50">
      <Box className="p-4">
        <Heading size="xl" className="text-gray-900 mb-6">
          上傳小卡
        </Heading>

        {/* 卡片資訊表單 */}
        <Box className="bg-white rounded-xl p-4 mb-4">
          <Box className="mb-4">
            <Text className="text-sm font-semibold text-gray-900 mb-2">偶像名稱</Text>
            <Input
              value={idol}
              onChangeText={setIdol}
              placeholder="例：IU"
              isDisabled={isUploading}
              className="bg-white"
            />
          </Box>

          <Box className="mb-4">
            <Text className="text-sm font-semibold text-gray-900 mb-2">
              團體/公司（選填）
            </Text>
            <Input
              value={idolGroup}
              onChangeText={setIdolGroup}
              placeholder="例：EDAM Entertainment"
              isDisabled={isUploading}
              className="bg-white"
            />
          </Box>

          <Box className="mb-4">
            <Text className="text-sm font-semibold text-gray-900 mb-2">
              專輯名稱（選填）
            </Text>
            <Input
              value={album}
              onChangeText={setAlbum}
              placeholder="例：Love Poem"
              isDisabled={isUploading}
              className="bg-white"
            />
          </Box>

          <Box className="mb-4">
            <Text className="text-sm font-semibold text-gray-900 mb-2">版本（選填）</Text>
            <Input
              value={version}
              onChangeText={setVersion}
              placeholder="例：限定版"
              isDisabled={isUploading}
              className="bg-white"
            />
          </Box>

          <Box>
            <Text className="text-sm font-semibold text-gray-900 mb-2">稀有度</Text>
            <Box className="flex-row gap-2">
              {RARITY_OPTIONS.map((option) => (
                <Pressable
                  key={option.value}
                  className={`flex-1 py-3 rounded-lg items-center ${
                    rarity === option.value ? 'bg-blue-500' : 'bg-gray-100'
                  }`}
                  onPress={() => setRarity(option.value)}
                  isDisabled={isUploading}
                >
                  <Text
                    className={`text-sm ${
                      rarity === option.value
                        ? 'text-white font-semibold'
                        : 'text-gray-700'
                    }`}
                  >
                    {option.label}
                  </Text>
                </Pressable>
              ))}
            </Box>
          </Box>
        </Box>

        {/* 上傳進度 */}
        {isUploading && (
          <Box className="bg-white rounded-xl p-6 mb-4 items-center">
            <Spinner size="large" />
            <Text className="text-base text-gray-900 mt-4 mb-3">
              {uploadProgress.message}
            </Text>
            <Box className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <Box
                className="h-full bg-blue-500"
                style={{ width: `${uploadProgress.progress}%` }}
              />
            </Box>
            <Text className="text-sm text-gray-600 mt-2">
              {uploadProgress.progress.toFixed(0)}%
            </Text>
          </Box>
        )}

        {/* 錯誤訊息 */}
        {error && !isUploading && (
          <Box className="bg-red-50 rounded-lg p-4 mb-4">
            <Text className="text-sm text-red-700">
              ❌ {(error as Error).message}
            </Text>
          </Box>
        )}

        {/* 上傳按鈕 */}
        <Box className="flex-row gap-3 mb-4">
          <Button
            onPress={() => handleUpload('camera')}
            isDisabled={isUploading}
            className="flex-1 bg-green-500"
          >
            <Text className="text-3xl mb-2">📷</Text>
            <ButtonText>拍照上傳</ButtonText>
          </Button>

          <Button
            onPress={() => handleUpload('gallery')}
            isDisabled={isUploading}
            className="flex-1 bg-blue-500"
          >
            <Text className="text-3xl mb-2">🖼️</Text>
            <ButtonText>相簿選取</ButtonText>
          </Button>
        </Box>

        {/* 使用說明 */}
        <Box className="bg-amber-50 rounded-xl p-4">
          <Text className="text-base font-bold text-amber-900 mb-3">
            📌 上傳說明
          </Text>
          <Text className="text-sm text-amber-900 mb-1">
            • 支援 JPEG 和 PNG 格式
          </Text>
          <Text className="text-sm text-amber-900 mb-1">
            • 單檔最大 10MB
          </Text>
          <Text className="text-sm text-amber-900 mb-1">
            • 免費用戶：每日 2 張，總容量 1GB
          </Text>
          <Text className="text-sm text-amber-900">
            • 建議比例：3:4（標準卡片比例）
          </Text>
        </Box>
      </Box>
    </ScrollView>
  );
}
