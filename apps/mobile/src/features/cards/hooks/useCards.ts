/**
 * Cards Hooks
 * 使用 TanStack Query 管理卡片相關的資料狀態
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMyCards, deleteCard, getQuotaStatus } from '@/src/features/cards/api/cardsApi';
import { removeThumbnailFromCache } from '@/src/features/cards/services/thumbnailService';
import type { Card, CardStatus, QuotaStatus } from '@/src/features/cards/types';

// Query keys
export const cardsKeys = {
  all: ['cards'] as const,
  lists: () => [...cardsKeys.all, 'list'] as const,
  list: (status?: CardStatus) => [...cardsKeys.lists(), { status }] as const,
  quota: () => [...cardsKeys.all, 'quota'] as const,
};

/**
 * Hook: 查詢我的卡片列表
 * M204: 實作卡冊列表
 */
export function useMyCards(status?: CardStatus) {
  return useQuery({
    queryKey: cardsKeys.list(status),
    queryFn: () => getMyCards(status),
    staleTime: 30000, // 30 秒內資料視為新鮮
  });
}

/**
 * Hook: 刪除卡片
 * M205: 實作刪除卡片功能
 */
export function useDeleteCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (card: Card) => {
      // 刪除卡片
      await deleteCard(card.id);

      // 清除縮圖快取
      await removeThumbnailFromCache(card.id, card.image_url);
    },
    onSuccess: () => {
      // 刷新卡片列表
      queryClient.invalidateQueries({ queryKey: cardsKeys.lists() });
      // 刷新配額狀態
      queryClient.invalidateQueries({ queryKey: cardsKeys.quota() });
    },
  });
}

/**
 * Hook: 查詢配額狀態
 */
export function useQuotaStatus() {
  return useQuery({
    queryKey: cardsKeys.quota(),
    queryFn: getQuotaStatus,
    staleTime: 60000, // 1 分鐘內資料視為新鮮
  });
}

/**
 * Hook: 手動刷新卡片列表
 */
export function useRefreshCards() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: cardsKeys.lists() });
  };
}
