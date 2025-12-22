/**
 * Trade Types
 * 交換相關的類型定義
 */

// 從生成的 SDK 導入類型
export type {
  CreateTradeRequest,
  TradeResponse,
  TradeItemResponse,
  TradeHistoryResponse,
} from '@/src/shared/api/generated/types.gen';

// Trade status 類型
export type TradeStatus =
  | 'draft'
  | 'proposed'
  | 'accepted'
  | 'completed'
  | 'rejected'
  | 'canceled';

// 交換卡片選擇
export interface TradeCardSelection {
  initiatorCards: string[]; // 發起者的卡片 IDs
  responderCards: string[]; // 回應者的卡片 IDs
}

// 本地交換狀態（用於 UI 顯示）
export interface TradeUIState {
  canAccept: boolean; // 是否可以接受
  canReject: boolean; // 是否可以拒絕
  canCancel: boolean; // 是否可以取消
  canConfirm: boolean; // 是否可以確認完成
  showRating: boolean; // 是否顯示評分入口
  isInitiator: boolean; // 是否是發起者
  isResponder: boolean; // 是否是回應者
  hasConfirmed: boolean; // 當前用戶是否已確認
  otherConfirmed: boolean; // 對方是否已確認
}
