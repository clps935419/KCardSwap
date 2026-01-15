/**
 * Trade History Screen
 * M503: 交換歷史列表
 * 
 * 功能：
 * - 顯示所有交換歷史（作為發起者或回應者）
 * - 按建立時間排序（最新在前）
 * - 點擊進入交換詳情頁
 * - Pull-to-refresh 重新載入
 * - 顯示交換狀態與對方資訊
 */

import React from 'react';
import { FlatList, RefreshControl, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import {
  Box,
  Text,
  Heading,
  VStack,
  HStack,
  Pressable,
  Spinner,
} from '@/src/shared/ui/components';
import { useTradeHistory } from '@/src/features/trade/hooks/useTrade';
import { useAuthStore } from '@/src/shared/state/authStore';
import type { TradeResponse } from '@/src/features/trade/types';

// 狀態顯示文字與顏色
const STATUS_CONFIG = {
  draft: { label: '草稿', color: '$gray500' },
  proposed: { label: '已提案', color: '$blue500' },
  accepted: { label: '已接受', color: '$green500' },
  completed: { label: '已完成', color: '$green600' },
  rejected: { label: '已拒絕', color: '$red500' },
  canceled: { label: '已取消', color: '$gray600' },
};

export default function TradeHistoryScreen() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const { data, isLoading, error, refetch, isRefetching } = useTradeHistory();

  // 處理點擊交換項目
  const handleTradePress = (trade: TradeResponse) => {
    router.push(`/trade/${trade.id}`);
  };

  // 渲染單一交換項目
  const renderTradeItem = ({ item }: { item: TradeResponse }) => {
    const isInitiator = item.initiator_id === user?.id;
    const otherUserId = isInitiator ? item.responder_id : item.initiator_id;
    const statusConfig = STATUS_CONFIG[item.status as keyof typeof STATUS_CONFIG];

    return (
      <Pressable
        onPress={() => handleTradePress(item)}
        className="mb-3"
      >
        <Box className="bg-white p-4 rounded-lg border border-gray-200">
          <HStack className="justify-between items-center mb-2">
            <VStack className="flex-1">
              <Text className="text-sm text-gray-600">
                {isInitiator ? '與對方交換' : '對方提出交換'}
              </Text>
              <Text className="text-xs text-gray-500 mt-1">
                交換 ID: {item.id.substring(0, 8)}...
              </Text>
            </VStack>
            <Box
              className="px-3 py-1 rounded-full"
              style={{ backgroundColor: statusConfig?.color || '$gray500' }}
            >
              <Text className="text-white text-xs font-medium">
                {statusConfig?.label || item.status}
              </Text>
            </Box>
          </HStack>

          {item.items && item.items.length > 0 && (
            <HStack className="mt-3 items-center">
              <Text className="text-sm text-gray-600">
                {isInitiator ? '我的' : '對方的'} {item.items.filter(i => i.owner_side === 'initiator').length} 張
              </Text>
              <Text className="text-sm text-gray-400 mx-2">⇄</Text>
              <Text className="text-sm text-gray-600">
                {isInitiator ? '對方的' : '我的'} {item.items.filter(i => i.owner_side === 'responder').length} 張
              </Text>
            </HStack>
          )}

          <Text className="text-xs text-gray-400 mt-2">
            {new Date(item.created_at).toLocaleString('zh-TW')}
          </Text>

          {/* M504: 完成後顯示評分入口 */}
          {item.status === 'completed' && (
            <Box className="mt-3 pt-3 border-t border-gray-100">
              <Text className="text-sm text-blue-600">
                → 去評分
              </Text>
            </Box>
          )}
        </Box>
      </Pressable>
    );
  };

  // 渲染空狀態
  const renderEmptyState = () => (
    <Box className="flex-1 justify-center items-center py-20">
      <Text className="text-gray-400 text-base">尚無交換記錄</Text>
      <Text className="text-gray-400 text-sm mt-2">
        開始與朋友交換小卡吧！
      </Text>
    </Box>
  );

  // 渲染錯誤狀態
  if (error) {
    return (
      <Box className="flex-1 justify-center items-center p-6">
        <Text className="text-red-500 text-center mb-4">
          載入交換歷史失敗
        </Text>
        <Text className="text-gray-500 text-sm text-center mb-4">
          {error.message || '發生未知錯誤'}
        </Text>
        <Pressable
          onPress={() => refetch()}
          className="bg-blue-500 px-6 py-3 rounded-lg"
        >
          <Text className="text-white font-medium">重試</Text>
        </Pressable>
      </Box>
    );
  }

  return (
    <Box className="flex-1 bg-gray-50">
      {/* Header */}
      <Box className="bg-white px-6 py-4 border-b border-gray-200">
        <Heading className="text-2xl font-bold">交換歷史</Heading>
      </Box>

      {/* Content */}
      {isLoading && !data ? (
        <Box className="flex-1 justify-center items-center">
          <Spinner size="large" />
          <Text className="text-gray-500 mt-4">載入中...</Text>
        </Box>
      ) : (
        <FlatList
          data={data?.trades || []}
          renderItem={renderTradeItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{
            padding: 16,
            paddingBottom: 32,
          }}
          ListEmptyComponent={renderEmptyState}
          refreshControl={
            <RefreshControl
              refreshing={isRefetching}
              onRefresh={refetch}
              tintColor="#3B82F6"
            />
          }
        />
      )}
    </Box>
  );
}
