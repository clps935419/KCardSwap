/**
 * Cards Hooks
 * 使用 TanStack Query 管理卡片相關的資料狀態
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getMyCardsOptions,
  getMyCardsQueryKey,
  deleteCardApiV1CardsCardIdDeleteMutation,
  getQuotaStatusApiV1CardsQuotaStatusGetOptions,
  getQuotaStatusApiV1CardsQuotaStatusGetQueryKey,
} from '@/src/features/cards/api/cardsApi';
import { deleteCardApiV1CardsCardIdDelete } from '@/src/shared/api/sdk';
import { removeThumbnailFromCache } from '@/src/features/cards/services/thumbnailService';
import type { Card, CardStatus, QuotaStatus } from '@/src/features/cards/types';

// Query keys (using SDK generated keys)
export const cardsKeys = {
  all: ['cards'] as const,
  lists: () => [...cardsKeys.all, 'list'] as const,
  list: (status?: CardStatus) => [...cardsKeys.lists(), { status }] as const,
  quota: () => getQuotaStatusApiV1CardsQuotaStatusGetQueryKey(),
};

/**
 * Hook: 查詢我的卡片列表
 * M204: 實作卡冊列表
 */
export function useMyCards(status?: CardStatus) {
  const result = useQuery({
    ...getMyCardsOptions(),
    queryKey: cardsKeys.list(status),
  });

  // Extract cards from envelope format
  // Note: CardListResponseWrapper.data is already CardResponse[]
  return {
    ...result,
    data: result.data?.data || [],
  };
}

/**
 * Hook: 刪除卡片
 * M205: 實作刪除卡片功能
 */
export function useDeleteCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (card: Card) => {
      // Call delete API via SDK
      const response = await deleteCardApiV1CardsCardIdDelete({
        path: { card_id: card.id },
      });

      // Clean up thumbnail cache
      await removeThumbnailFromCache(card.id, card.image_url);

      return response;
    },
    onSuccess: () => {
      // Refresh card list
      queryClient.invalidateQueries({ queryKey: cardsKeys.lists() });
      // Refresh quota status
      queryClient.invalidateQueries({ queryKey: cardsKeys.quota() });
    },
  });
}

/**
 * Hook: 查詢配額狀態
 */
export function useQuotaStatus() {
  const result = useQuery({
    ...getQuotaStatusApiV1CardsQuotaStatusGetOptions(),
    queryKey: cardsKeys.quota(),
    staleTime: 60000, // 1 分鐘內資料視為新鮮
  });

  // Extract quota from envelope format
  return {
    ...result,
    data: result.data?.data as QuotaStatus | undefined,
  };
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
