/**
 * Image Picker Service
 * M201: 圖片選取與壓縮
 * 
 * 支援「拍照」與「相簿選取」兩種來源
 * 自動壓縮至 ≤10MB
 * 支援 JPEG/PNG 格式
 */

import * as ImagePicker from 'expo-image-picker';
import * as ImageManipulator from 'expo-image-manipulator';
import type { ImagePickResult } from '../types';

// 最大檔案大小：10MB
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

// 支援的格式
const SUPPORTED_FORMATS = ['image/jpeg', 'image/png'] as const;

/**
 * 請求相機權限
 */
async function requestCameraPermission(): Promise<boolean> {
  const { status } = await ImagePicker.requestCameraPermissionsAsync();
  return status === 'granted';
}

/**
 * 請求相簿權限
 */
async function requestMediaLibraryPermission(): Promise<boolean> {
  const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
  return status === 'granted';
}

/**
 * 取得圖片檔案大小（估算）
 */
function estimateImageSize(width: number, height: number, quality: number = 0.8): number {
  // 粗略估算 JPEG 檔案大小：width × height × 3(RGB) × quality / 壓縮率
  return Math.ceil((width * height * 3 * quality) / 10);
}

/**
 * 壓縮圖片至指定大小以下
 */
async function compressImage(
  uri: string,
  targetSize: number = MAX_FILE_SIZE_BYTES
): Promise<ImageManipulator.ImageResult> {
  let quality = 0.8;
  let result = await ImageManipulator.manipulateAsync(uri, [], { compress: quality });

  // 如果估算大小超過目標，逐步降低品質或縮小尺寸
  let attempts = 0;
  const maxAttempts = 5;

  while (estimateImageSize(result.width, result.height, quality) > targetSize && attempts < maxAttempts) {
    attempts++;

    if (quality > 0.3) {
      // 先降低品質
      quality -= 0.15;
    } else {
      // 品質已經很低，開始縮小尺寸
      const scale = 0.8;
      result = await ImageManipulator.manipulateAsync(
        uri,
        [
          {
            resize: {
              width: Math.floor(result.width * scale),
              height: Math.floor(result.height * scale),
            },
          },
        ],
        { compress: quality }
      );
    }

    result = await ImageManipulator.manipulateAsync(uri, [], { compress: quality });
  }

  return result;
}

/**
 * 從相機拍照
 * M201: 支援拍照來源
 */
export async function pickImageFromCamera(): Promise<ImagePickResult | null> {
  // 檢查權限
  const hasPermission = await requestCameraPermission();
  if (!hasPermission) {
    throw new Error('相機權限被拒絕。請至設定中開啟相機權限。');
  }

  // 啟動相機
  const result = await ImagePicker.launchCameraAsync({
    mediaTypes: 'images',
    allowsEditing: true,
    aspect: [3, 4], // 標準卡片比例
    quality: 0.8,
  });

  // 使用者取消不視為錯誤
  if (result.canceled) {
    return null;
  }

  const asset = result.assets[0];

  // 壓縮圖片
  const compressed = await compressImage(asset.uri);

  return {
    uri: compressed.uri,
    width: compressed.width,
    height: compressed.height,
    type: 'image/jpeg', // 拍照預設為 JPEG
    fileSize: estimateImageSize(compressed.width, compressed.height, 0.8),
  };
}

/**
 * 從相簿選取
 * M201: 支援相簿選取來源
 */
export async function pickImageFromGallery(): Promise<ImagePickResult | null> {
  // 檢查權限
  const hasPermission = await requestMediaLibraryPermission();
  if (!hasPermission) {
    throw new Error('相簿權限被拒絕。請至設定中開啟相簿存取權限。');
  }

  // 開啟相簿
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: 'images',
    allowsEditing: true,
    aspect: [3, 4],
    quality: 0.8,
  });

  // 使用者取消不視為錯誤
  if (result.canceled) {
    return null;
  }

  const asset = result.assets[0];

  // 檢查格式
  const mimeType = asset.mimeType || 'image/jpeg';
  if (!SUPPORTED_FORMATS.includes(mimeType as any)) {
    throw new Error(`不支援的圖片格式：${mimeType}。僅支援 JPEG 和 PNG。`);
  }

  // 壓縮圖片
  const compressed = await compressImage(asset.uri);

  return {
    uri: compressed.uri,
    width: compressed.width,
    height: compressed.height,
    type: mimeType as 'image/jpeg' | 'image/png',
    fileSize: estimateImageSize(compressed.width, compressed.height, 0.8),
  };
}

/**
 * 驗證圖片大小
 */
export function validateImageSize(fileSize: number): { valid: boolean; error?: string } {
  if (fileSize > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: `圖片檔案過大（${(fileSize / 1024 / 1024).toFixed(2)}MB）。最大限制為 10MB。`,
    };
  }
  return { valid: true };
}
