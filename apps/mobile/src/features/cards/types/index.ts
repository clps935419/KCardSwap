/**
 * Card Types
 * 定義卡片相關的類型與介面
 */

/**
 * 卡片狀態
 */
export type CardStatus = 'available' | 'trading' | 'traded';

/**
 * 卡片稀有度
 */
export type CardRarity = 'common' | 'rare' | 'epic' | 'legendary';

/**
 * 卡片實體
 */
export interface Card {
  id: string;
  owner_id: string;
  idol: string;
  idol_group?: string;
  album?: string;
  version?: string;
  rarity: CardRarity;
  status: CardStatus;
  image_url: string;
  thumbnail_url?: string; // 本機縮圖路徑 (僅前端使用)
  size_bytes: number;
  created_at: string;
  updated_at: string;
}

/**
 * 上傳 URL 請求
 */
export interface UploadUrlRequest {
  content_type: 'image/jpeg' | 'image/png';
  file_size_bytes: number;
  idol?: string;
  idol_group?: string;
  album?: string;
  version?: string;
  rarity?: CardRarity;
}

/**
 * 上傳 URL 回應
 */
export interface UploadUrlResponse {
  upload_url: string;
  method: 'PUT' | 'POST';
  required_headers: Record<string, string>;
  image_url: string;
  expires_at: string;
  card_id: string;
}

/**
 * 配額狀態
 */
export interface QuotaStatus {
  daily_uploads: {
    used: number;
    limit: number;
    remaining: number;
  };
  storage: {
    used_bytes: number;
    limit_bytes: number;
    remaining_bytes: number;
  };
}

/**
 * 圖片選取結果
 */
export interface ImagePickResult {
  uri: string;
  width: number;
  height: number;
  type: 'image/jpeg' | 'image/png';
  fileSize: number;
  base64?: string;
}

/**
 * 縮圖快取鍵
 */
export interface ThumbnailCacheKey {
  cardId: string;
  imageUrl: string;
}

/**
 * API 錯誤類型
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

/**
 * 限制超過錯誤詳情
 */
export interface LimitExceededError extends ApiError {
  code: 'LIMIT_EXCEEDED';
  limit_type?: 'daily' | 'storage' | 'size';
  current_usage?: number;
  limit?: number;
  statusCode?: number;
}
