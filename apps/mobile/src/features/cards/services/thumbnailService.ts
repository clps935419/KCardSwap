/**
 * Thumbnail Service
 * M203A: 產生 200x200 WebP 縮圖並本機快取
 * 
 * 縮圖僅供列表快速載入，不上傳到後端
 */

import * as ImageManipulator from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';
import * as Crypto from 'expo-crypto';
import { Platform } from 'react-native';

// 縮圖尺寸
const THUMBNAIL_SIZE = 200;

/**
 * 取得縮圖快取目錄
 * 根據平台和可用的 API 選擇適當的目錄
 */
function getThumbnailCacheDirectory(): string {
  // 使用 any 來繞過 TypeScript 檢查，因為不同版本的 expo-file-system API 不同
  const fs = FileSystem as any;
  
  // 嘗試使用 documentDirectory（較新版本）
  if (fs.documentDirectory) {
    return `${fs.documentDirectory}thumbnails/`;
  }
  
  // 嘗試使用 cacheDirectory（舊版本）
  if (fs.cacheDirectory) {
    return `${fs.cacheDirectory}thumbnails/`;
  }
  
  // Fallback: 使用臨時目錄
  console.warn('FileSystem directory constants not found, using fallback');
  return Platform.OS === 'ios' 
    ? 'file:///tmp/thumbnails/' 
    : 'file:///data/local/tmp/thumbnails/';
}

const THUMBNAIL_CACHE_DIR = getThumbnailCacheDirectory();

/**
 * 初始化縮圖快取目錄
 */
async function ensureThumbnailDirectory(): Promise<void> {
  const dirInfo = await FileSystem.getInfoAsync(THUMBNAIL_CACHE_DIR);
  if (!dirInfo.exists) {
    await FileSystem.makeDirectoryAsync(THUMBNAIL_CACHE_DIR, { intermediates: true });
  }
}

/**
 * 產生縮圖快取鍵（使用 card_id 或 image_url 的雜湊）
 */
async function generateThumbnailKey(cardId: string, imageUrl: string): Promise<string> {
  // 優先使用 cardId，否則使用 imageUrl 的雜湊
  const key = cardId || (await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, imageUrl));
  return `${key}.webp`;
}

/**
 * 取得縮圖檔案路徑
 */
function getThumbnailPath(key: string): string {
  return `${THUMBNAIL_CACHE_DIR}${key}`;
}

/**
 * 產生縮圖
 * M203A: 核心功能 - 產生 200x200 WebP 縮圖
 */
export async function generateThumbnail(imageUri: string): Promise<string> {
  await ensureThumbnailDirectory();

  try {
    // 產生縮圖（等比例縮放並裁切成正方形）
    const result = await ImageManipulator.manipulateAsync(
      imageUri,
      [
        {
          resize: {
            width: THUMBNAIL_SIZE,
            height: THUMBNAIL_SIZE,
          },
        },
      ],
      {
        compress: 0.7,
        format: ImageManipulator.SaveFormat.WEBP,
      }
    );

    return result.uri;
  } catch (error) {
    // WebP 不支援時，fallback 到 JPEG
    console.warn('WebP 不支援，使用 JPEG fallback', error);

    const result = await ImageManipulator.manipulateAsync(
      imageUri,
      [
        {
          resize: {
            width: THUMBNAIL_SIZE,
            height: THUMBNAIL_SIZE,
          },
        },
      ],
      {
        compress: 0.7,
        format: ImageManipulator.SaveFormat.JPEG,
      }
    );

    return result.uri;
  }
}

/**
 * 儲存縮圖到快取
 * M203A: 快取縮圖到本機
 */
export async function saveThumbnailToCache(
  cardId: string,
  imageUrl: string,
  thumbnailUri: string
): Promise<string> {
  await ensureThumbnailDirectory();

  const key = await generateThumbnailKey(cardId, imageUrl);
  const cachePath = getThumbnailPath(key);

  // 複製縮圖到快取目錄
  await FileSystem.copyAsync({
    from: thumbnailUri,
    to: cachePath,
  });

  return cachePath;
}

/**
 * 從快取載入縮圖
 * M203A: 從本機快取讀取縮圖
 */
export async function getThumbnailFromCache(
  cardId: string,
  imageUrl: string
): Promise<string | null> {
  const key = await generateThumbnailKey(cardId, imageUrl);
  const cachePath = getThumbnailPath(key);

  const fileInfo = await FileSystem.getInfoAsync(cachePath);

  if (fileInfo.exists) {
    return cachePath;
  }

  return null;
}

/**
 * 移除快取的縮圖
 * M205: 刪除卡片時需清除縮圖快取
 */
export async function removeThumbnailFromCache(cardId: string, imageUrl: string): Promise<void> {
  const key = await generateThumbnailKey(cardId, imageUrl);
  const cachePath = getThumbnailPath(key);

  try {
    const fileInfo = await FileSystem.getInfoAsync(cachePath);
    if (fileInfo.exists) {
      await FileSystem.deleteAsync(cachePath);
    }
  } catch (error) {
    console.error('移除縮圖快取失敗', error);
  }
}

/**
 * 清除所有縮圖快取
 */
export async function clearAllThumbnailCache(): Promise<void> {
  try {
    const dirInfo = await FileSystem.getInfoAsync(THUMBNAIL_CACHE_DIR);
    if (dirInfo.exists) {
      await FileSystem.deleteAsync(THUMBNAIL_CACHE_DIR, { idempotent: true });
      await ensureThumbnailDirectory();
    }
  } catch (error) {
    console.error('清除縮圖快取失敗', error);
  }
}

/**
 * 取得快取統計
 */
export async function getThumbnailCacheStats(): Promise<{
  count: number;
  totalSize: number;
}> {
  try {
    const dirInfo = await FileSystem.getInfoAsync(THUMBNAIL_CACHE_DIR);
    if (!dirInfo.exists) {
      return { count: 0, totalSize: 0 };
    }

    const files = await FileSystem.readDirectoryAsync(THUMBNAIL_CACHE_DIR);
    let totalSize = 0;

    for (const file of files) {
      const filePath = `${THUMBNAIL_CACHE_DIR}${file}`;
      const fileInfo = await FileSystem.getInfoAsync(filePath);
      if (fileInfo.exists && 'size' in fileInfo) {
        totalSize += fileInfo.size;
      }
    }

    return {
      count: files.length,
      totalSize,
    };
  } catch (error) {
    console.error('取得快取統計失敗', error);
    return { count: 0, totalSize: 0 };
  }
}
