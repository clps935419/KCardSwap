/**
 * Trade Detail Screen
 * M502: 提案詳情與狀態更新 UI
 * M504: Trade 完成後導流評分
 * 
 * 功能：
 * - 顯示交換詳情（雙方卡片、狀態）
 * - 接受/拒絕提案（僅回應者）
 * - 確認完成交換（雙方獨立確認）
 * - 取消交換
 * - 完成後顯示「去評分」入口
 */

import React, { useState } from 'react';
import { ScrollView, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import {
  Box,
  Text,
  Heading,
  VStack,
  HStack,
  Button,
  ButtonText,
  Spinner,
} from '@/src/shared/ui/components';
import {
  useAcceptTrade,
  useRejectTrade,
  useCancelTrade,
  useCompleteTrade,
  getTradeUIState,
} from '@/src/features/trade/hooks/useTrade';
import { useAuthStore } from '@/src/shared/state/authStore';

// 注意：實際應用中需要一個 useTradeDetail hook 來獲取單一交換詳情
// 這裡先使用 trade history 中的資料作為示例

export default function TradeDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const user = useAuthStore((state) => state.user);
  
  const acceptTrade = useAcceptTrade();
  const rejectTrade = useRejectTrade();
  const cancelTrade = useCancelTrade();
  const completeTrade = useCompleteTrade();

  // TODO: 實際應該有 useTradeDetail(id) hook
  // 這裡暫時返回 loading 狀態作為示例
  const [isLoading] = useState(true);
  const [trade] = useState<any>(null);

  if (isLoading || !trade) {
    return (
      <Box className="flex-1 justify-center items-center">
        <Spinner size="large" />
        <Text className="text-gray-500 mt-4">載入中...</Text>
      </Box>
    );
  }

  const uiState = getTradeUIState(trade, user?.id || '');

  // 處理接受提案
  const handleAccept = () => {
    Alert.alert('確認接受', '確定要接受此交換提案嗎？', [
      { text: '取消', style: 'cancel' },
      {
        text: '接受',
        onPress: async () => {
          try {
            await acceptTrade.mutateAsync(id);
            Alert.alert('成功', '已接受交換提案');
          } catch (error: any) {
            Alert.alert('錯誤', error.message || '接受失敗');
          }
        },
      },
    ]);
  };

  // 處理拒絕提案
  const handleReject = () => {
    Alert.alert('確認拒絕', '確定要拒絕此交換提案嗎？', [
      { text: '取消', style: 'cancel' },
      {
        text: '拒絕',
        style: 'destructive',
        onPress: async () => {
          try {
            await rejectTrade.mutateAsync(id);
            Alert.alert('已拒絕', '已拒絕交換提案');
            router.back();
          } catch (error: any) {
            Alert.alert('錯誤', error.message || '拒絕失敗');
          }
        },
      },
    ]);
  };

  // 處理取消交換
  const handleCancel = () => {
    Alert.alert('確認取消', '確定要取消此交換嗎？', [
      { text: '取消', style: 'cancel' },
      {
        text: '確定取消',
        style: 'destructive',
        onPress: async () => {
          try {
            await cancelTrade.mutateAsync(id);
            Alert.alert('已取消', '已取消交換');
            router.back();
          } catch (error: any) {
            Alert.alert('錯誤', error.message || '取消失敗');
          }
        },
      },
    ]);
  };

  // 處理確認完成
  const handleComplete = () => {
    Alert.alert(
      '確認完成交換',
      '請確認您已完成實體小卡的交換\n\n雙方都確認後，交換才會正式完成',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '確認完成',
          onPress: async () => {
            try {
              await completeTrade.mutateAsync(id);
              Alert.alert('成功', '已確認完成交換');
            } catch (error: any) {
              Alert.alert('錯誤', error.message || '確認失敗');
            }
          },
        },
      ]
    );
  };

  // M504: 導向評分頁面
  const handleGoToRating = () => {
    const otherUserId = uiState.isInitiator
      ? trade.responder_id
      : trade.initiator_id;
    router.push(`/rating/create?userId=${otherUserId}&tradeId=${id}`);
  };

  return (
    <Box className="flex-1 bg-gray-50">
      <ScrollView>
        {/* Header */}
        <Box className="bg-white px-6 py-4 border-b border-gray-200">
          <Heading className="text-2xl font-bold">交換詳情</Heading>
        </Box>

        {/* Status */}
        <Box className="bg-white p-6 mb-3">
          <Text className="text-gray-600 mb-2">狀態</Text>
          <Text className="text-xl font-bold">{trade.status}</Text>
        </Box>

        {/* Cards Info */}
        <Box className="bg-white p-6 mb-3">
          <Text className="text-gray-600 mb-4">交換內容</Text>
          {/* TODO: 顯示卡片列表 */}
        </Box>

        {/* Confirmation Status */}
        {trade.status === 'accepted' && (
          <Box className="bg-white p-6 mb-3">
            <Text className="text-gray-600 mb-3">確認狀態</Text>
            <VStack className="space-y-2">
              <HStack className="justify-between">
                <Text>發起者確認</Text>
                <Text className={trade.initiator_confirmed_at ? 'text-green-600' : 'text-gray-400'}>
                  {trade.initiator_confirmed_at ? '✓ 已確認' : '⏳ 待確認'}
                </Text>
              </HStack>
              <HStack className="justify-between">
                <Text>回應者確認</Text>
                <Text className={trade.responder_confirmed_at ? 'text-green-600' : 'text-gray-400'}>
                  {trade.responder_confirmed_at ? '✓ 已確認' : '⏳ 待確認'}
                </Text>
              </HStack>
            </VStack>
          </Box>
        )}

        {/* Actions */}
        <Box className="p-6">
          <VStack className="space-y-3">
            {uiState.canAccept && (
              <Button
                onPress={handleAccept}
                className="bg-green-600"
                disabled={acceptTrade.isPending}
              >
                <ButtonText>接受提案</ButtonText>
              </Button>
            )}
            
            {uiState.canReject && (
              <Button
                onPress={handleReject}
                className="bg-red-600"
                disabled={rejectTrade.isPending}
              >
                <ButtonText>拒絕提案</ButtonText>
              </Button>
            )}
            
            {uiState.canConfirm && (
              <Button
                onPress={handleComplete}
                className="bg-blue-600"
                disabled={completeTrade.isPending}
              >
                <ButtonText>
                  {uiState.otherConfirmed ? '確認完成交換' : '我已完成交換'}
                </ButtonText>
              </Button>
            )}
            
            {uiState.canCancel && (
              <Button
                onPress={handleCancel}
                variant="outline"
                disabled={cancelTrade.isPending}
              >
                <ButtonText>取消交換</ButtonText>
              </Button>
            )}

            {/* M504: 完成後顯示評分入口 */}
            {uiState.showRating && (
              <Button
                onPress={handleGoToRating}
                className="bg-yellow-500"
              >
                <ButtonText>去評分</ButtonText>
              </Button>
            )}
          </VStack>
        </Box>
      </ScrollView>
    </Box>
  );
}
