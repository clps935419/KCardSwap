/**
 * Cards API Client
 * 卡片相關的 API 請求
 */

import { apiClient } from '@/src/shared/api/client';
import type {
  Card,
  CardStatus,
  UploadUrlRequest,
  UploadUrlResponse,
  QuotaStatus,
} from '@/src/features/cards/types';

/**
 * 取得上傳 Signed URL
 * M202: 呼叫後端 API 取得 GCS Signed URL
 */
export async function getUploadUrl(request: UploadUrlRequest): Promise<UploadUrlResponse> {
  const response = await apiClient.post<{ data: UploadUrlResponse }>('/cards/upload-url', request);
  return response.data.data;
}

/**
 * 查詢我的卡片列表
 * M204: 取得使用者的所有卡片
 */
export async function getMyCards(status?: CardStatus): Promise<Card[]> {
  const params = status ? { status } : {};
  const response = await apiClient.get<{ data: { items: Card[] } }>('/cards/me', { params });
  return response.data.data.items;
}

/**
 * 刪除卡片
 * M205: 刪除指定的卡片（包含 GCS 清理）
 */
export async function deleteCard(cardId: string): Promise<void> {
  await apiClient.delete(`/cards/${cardId}`);
}

/**
 * 檢查配額狀態
 * 查詢當前上傳配額使用情況
 */
export async function getQuotaStatus(): Promise<QuotaStatus> {
  const response = await apiClient.get<{ data: QuotaStatus }>('/cards/quota/status');
  return response.data.data;
}
