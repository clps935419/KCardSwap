/**
 * Trade Hooks
 * 使用 TanStack Query 與生成的 SDK 管理交換相關的資料狀態
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/src/shared/state/authStore';
import type {
  CreateTradeRequest,
  TradeResponse,
  TradeHistoryResponse,
} from '@/src/features/trade/types';

// 從生成的 SDK 導入 options/mutations
import {
  getTradeHistoryApiV1TradesHistoryGetOptions,
  createTradeApiV1TradesPostMutation,
  acceptTradeApiV1TradesTradeIdAcceptPostMutation,
  rejectTradeApiV1TradesTradeIdRejectPostMutation,
  cancelTradeApiV1TradesTradeIdCancelPostMutation,
  completeTradeApiV1TradesTradeIdCompletePostMutation,
} from '@/src/shared/api/generated/@tanstack/react-query.gen';

// Query keys
export const tradeKeys = {
  all: ['trades'] as const,
  lists: () => [...tradeKeys.all, 'list'] as const,
  history: (limit?: number, offset?: number) =>
    [...tradeKeys.lists(), 'history', { limit, offset }] as const,
  detail: (id: string) => [...tradeKeys.all, 'detail', id] as const,
};

/**
 * Hook: 查詢交換歷史
 * M503: 實作交換歷史列表
 */
export function useTradeHistory(limit: number = 50, offset: number = 0) {
  return useQuery({
    ...getTradeHistoryApiV1TradesHistoryGetOptions({
      query: { limit, offset },
    }),
    queryKey: tradeKeys.history(limit, offset),
  });
}

/**
 * Hook: 建立交換提案
 * M501: 實作發起交換提案
 */
export function useCreateTrade() {
  const queryClient = useQueryClient();

  return useMutation({
    ...createTradeApiV1TradesPostMutation(),
    onSuccess: () => {
      // 刷新交換歷史列表
      queryClient.invalidateQueries({ queryKey: tradeKeys.lists() });
    },
  });
}

/**
 * Hook: 接受交換提案
 * M502: 實作接受提案動作
 */
export function useAcceptTrade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tradeId: string) => {
      const result = await acceptTradeApiV1TradesTradeIdAcceptPostMutation();
      return result.mutationFn({ path: { trade_id: tradeId } });
    },
    onSuccess: (data) => {
      // 刷新交換詳情
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: tradeKeys.detail(data.id) });
      }
      // 刷新交換列表
      queryClient.invalidateQueries({ queryKey: tradeKeys.lists() });
    },
  });
}

/**
 * Hook: 拒絕交換提案
 * M502: 實作拒絕提案動作
 */
export function useRejectTrade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tradeId: string) => {
      const result = await rejectTradeApiV1TradesTradeIdRejectPostMutation();
      return result.mutationFn({ path: { trade_id: tradeId } });
    },
    onSuccess: (data) => {
      // 刷新交換詳情
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: tradeKeys.detail(data.id) });
      }
      // 刷新交換列表
      queryClient.invalidateQueries({ queryKey: tradeKeys.lists() });
    },
  });
}

/**
 * Hook: 取消交換
 * M502: 實作取消交換動作
 */
export function useCancelTrade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tradeId: string) => {
      const result = await cancelTradeApiV1TradesTradeIdCancelPostMutation();
      return result.mutationFn({ path: { trade_id: tradeId } });
    },
    onSuccess: (data) => {
      // 刷新交換詳情
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: tradeKeys.detail(data.id) });
      }
      // 刷新交換列表
      queryClient.invalidateQueries({ queryKey: tradeKeys.lists() });
    },
  });
}

/**
 * Hook: 確認完成交換
 * M502: 實作確認完成動作
 */
export function useCompleteTrade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tradeId: string) => {
      const result = await completeTradeApiV1TradesTradeIdCompletePostMutation();
      return result.mutationFn({ path: { trade_id: tradeId } });
    },
    onSuccess: (data) => {
      // 刷新交換詳情
      if (data.id) {
        queryClient.invalidateQueries({ queryKey: tradeKeys.detail(data.id) });
      }
      // 刷新交換列表
      queryClient.invalidateQueries({ queryKey: tradeKeys.lists() });
    },
  });
}

/**
 * Helper: 計算交換的 UI 狀態
 * 用於判斷當前用戶可以進行哪些操作
 */
export function getTradeUIState(
  trade: TradeResponse,
  currentUserId: string
): {
  canAccept: boolean;
  canReject: boolean;
  canCancel: boolean;
  canConfirm: boolean;
  showRating: boolean;
  isInitiator: boolean;
  isResponder: boolean;
  hasConfirmed: boolean;
  otherConfirmed: boolean;
} {
  const isInitiator = trade.initiator_id === currentUserId;
  const isResponder = trade.responder_id === currentUserId;

  // 確認狀態
  const initiatorConfirmed = !!trade.initiator_confirmed_at;
  const responderConfirmed = !!trade.responder_confirmed_at;
  const hasConfirmed = isInitiator ? initiatorConfirmed : responderConfirmed;
  const otherConfirmed = isInitiator ? responderConfirmed : initiatorConfirmed;

  return {
    canAccept: trade.status === 'proposed' && isResponder,
    canReject: trade.status === 'proposed' && isResponder,
    canCancel: ['draft', 'proposed', 'accepted'].includes(trade.status),
    canConfirm: trade.status === 'accepted' && !hasConfirmed,
    showRating: trade.status === 'completed',
    isInitiator,
    isResponder,
    hasConfirmed,
    otherConfirmed,
  };
}
