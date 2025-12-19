/**
 * My Cards Screen
 * M204: 我的卡冊列表
 * 
 * 功能：
 * - 顯示使用者的所有卡片
 * - 支援狀態篩選
 * - 支援刪除卡片
 * - 顯示配額狀態
 * 
 * 使用 Gluestack UI 元件
 */

import React, { useState } from 'react';
import { FlatList, RefreshControl, Alert } from 'react-native';
import { Box, Text, Pressable, Spinner, Button, ButtonText } from '@/src/shared/ui/components';
import { useMyCards, useDeleteCard, useQuotaStatus } from '@/src/features/cards/hooks/useCards';
import { CardItem } from '@/src/features/cards/components/CardItem';
import type { Card, CardStatus } from '@/src/features/cards/types';

const STATUS_FILTERS: { label: string; value: CardStatus | 'all' }[] = [
  { label: '全部', value: 'all' },
  { label: '可交換', value: 'available' },
  { label: '交易中', value: 'trading' },
  { label: '已交換', value: 'traded' },
];

export function MyCardsScreen() {
  const [selectedStatus, setSelectedStatus] = useState<CardStatus | 'all'>('all');

  const statusFilter = selectedStatus === 'all' ? undefined : selectedStatus;
  const { data: cards, isLoading, error, refetch, isRefetching } = useMyCards(statusFilter);
  const { data: quota } = useQuotaStatus();
  const deleteCardMutation = useDeleteCard();

  const handleDeleteCard = (card: Card) => {
    // 防止刪除交易中的卡片
    if (card.status !== 'available') {
      Alert.alert('無法刪除', '只能刪除可交換狀態的卡片');
      return;
    }

    Alert.alert('刪除卡片', `確定要刪除「${card.idol}」的卡片嗎？`, [
      { text: '取消', style: 'cancel' },
      {
        text: '刪除',
        style: 'destructive',
        onPress: () => {
          deleteCardMutation.mutate(card, {
            onError: (error: any) => {
              Alert.alert('刪除失敗', error.message || '請稍後再試');
            },
          });
        },
      },
    ]);
  };

  const renderHeader = () => (
    <Box>
      {/* 配額狀態 */}
      {quota && (
        <Box className="p-4 bg-gray-50 border-b border-gray-200">
          <Text className="text-sm font-bold text-gray-900 mb-2">今日上傳限制</Text>
          <Box className="flex-row justify-between mb-1">
            <Text className="text-xs text-gray-700">
              已上傳：{quota.daily_uploads.used} / {quota.daily_uploads.limit}
            </Text>
            <Text
              className={`text-xs font-semibold ${
                quota.daily_uploads.remaining === 0 ? 'text-red-500' : 'text-green-500'
              }`}
            >
              剩餘：{quota.daily_uploads.remaining}
            </Text>
          </Box>
          <Box className="flex-row justify-between">
            <Text className="text-xs text-gray-700">
              容量：{(quota.storage.used_bytes / 1024 / 1024).toFixed(2)} MB /{' '}
              {(quota.storage.limit_bytes / 1024 / 1024 / 1024).toFixed(2)} GB
            </Text>
          </Box>
        </Box>
      )}

      {/* 狀態篩選 */}
      <Box className="flex-row px-4 pt-4 pb-2 gap-2 bg-white">
        {STATUS_FILTERS.map((filter) => (
          <Pressable
            key={filter.value}
            className={`px-4 py-2 rounded-full ${
              selectedStatus === filter.value ? 'bg-blue-500' : 'bg-gray-200'
            }`}
            onPress={() => setSelectedStatus(filter.value)}
          >
            <Text
              className={`text-sm ${
                selectedStatus === filter.value
                  ? 'text-white font-semibold'
                  : 'text-gray-700'
              }`}
            >
              {filter.label}
            </Text>
          </Pressable>
        ))}
      </Box>
    </Box>
  );

  const renderEmpty = () => {
    if (isLoading) {
      return null;
    }

    return (
      <Box className="flex-1 justify-center items-center py-16">
        <Text className="text-6xl mb-4">📦</Text>
        <Text className="text-lg font-bold text-gray-900 mb-2">尚無卡片</Text>
        <Text className="text-sm text-gray-500 text-center">
          上傳您的第一張小卡開始收藏吧！
        </Text>
      </Box>
    );
  };

  const renderError = () => (
    <Box className="flex-1 justify-center items-center p-8">
      <Text className="text-6xl mb-4">⚠️</Text>
      <Text className="text-lg font-bold text-gray-900 mb-2">載入失敗</Text>
      <Text className="text-sm text-gray-500 text-center mb-6">
        {(error as Error)?.message || '請稍後再試'}
      </Text>
      <Button onPress={() => refetch()} className="bg-blue-500">
        <ButtonText>重試</ButtonText>
      </Button>
    </Box>
  );

  if (error && !cards) {
    return <Box className="flex-1 bg-gray-50">{renderError()}</Box>;
  }

  return (
    <Box className="flex-1 bg-gray-50">
      <FlatList
        data={cards || []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <CardItem card={item} onDelete={handleDeleteCard} />
        )}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
        }
        contentContainerStyle={cards?.length === 0 ? { flexGrow: 1 } : undefined}
      />

      {/* 載入中遮罩 */}
      {isLoading && (
        <Box className="absolute inset-0 bg-black/30 justify-center items-center">
          <Spinner size="large" />
          <Text className="mt-3 text-base text-white font-semibold">載入中...</Text>
        </Box>
      )}

      {/* 刪除中遮罩 */}
      {deleteCardMutation.isPending && (
        <Box className="absolute inset-0 bg-black/30 justify-center items-center">
          <Spinner size="large" color="$red500" />
          <Text className="mt-3 text-base text-white font-semibold">刪除中...</Text>
        </Box>
      )}
    </Box>
  );
}
