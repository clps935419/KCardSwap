/**
 * My Cards Screen
 * M204: 我的卡冊列表
 * 
 * 功能：
 * - 顯示使用者的所有卡片
 * - 支援狀態篩選
 * - 支援刪除卡片
 * - 顯示配額狀態
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import { useMyCards, useDeleteCard, useQuotaStatus } from '../hooks/useCards';
import { CardItem } from '../components/CardItem';
import type { Card, CardStatus } from '../types';

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
    <View style={styles.header}>
      {/* 配額狀態 */}
      {quota && (
        <View style={styles.quotaContainer}>
          <Text style={styles.quotaTitle}>今日上傳限制</Text>
          <View style={styles.quotaRow}>
            <Text style={styles.quotaText}>
              已上傳：{quota.daily_uploads.used} / {quota.daily_uploads.limit}
            </Text>
            <Text
              style={[
                styles.quotaRemaining,
                quota.daily_uploads.remaining === 0 && styles.quotaExceeded,
              ]}
            >
              剩餘：{quota.daily_uploads.remaining}
            </Text>
          </View>
          <View style={styles.quotaRow}>
            <Text style={styles.quotaText}>
              容量：{(quota.storage.used_bytes / 1024 / 1024).toFixed(2)} MB /{' '}
              {(quota.storage.limit_bytes / 1024 / 1024 / 1024).toFixed(2)} GB
            </Text>
          </View>
        </View>
      )}

      {/* 狀態篩選 */}
      <View style={styles.filterContainer}>
        {STATUS_FILTERS.map((filter) => (
          <TouchableOpacity
            key={filter.value}
            style={[styles.filterButton, selectedStatus === filter.value && styles.filterButtonActive]}
            onPress={() => setSelectedStatus(filter.value)}
          >
            <Text
              style={[styles.filterText, selectedStatus === filter.value && styles.filterTextActive]}
            >
              {filter.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderEmpty = () => {
    if (isLoading) {
      return null;
    }

    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>📦</Text>
        <Text style={styles.emptyTitle}>尚無卡片</Text>
        <Text style={styles.emptyText}>上傳您的第一張小卡開始收藏吧！</Text>
      </View>
    );
  };

  const renderError = () => (
    <View style={styles.errorContainer}>
      <Text style={styles.errorIcon}>⚠️</Text>
      <Text style={styles.errorTitle}>載入失敗</Text>
      <Text style={styles.errorText}>{(error as Error)?.message || '請稍後再試'}</Text>
      <TouchableOpacity style={styles.retryButton} onPress={() => refetch()}>
        <Text style={styles.retryButtonText}>重試</Text>
      </TouchableOpacity>
    </View>
  );

  if (error && !cards) {
    return <View style={styles.container}>{renderError()}</View>;
  }

  return (
    <View style={styles.container}>
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
        contentContainerStyle={cards?.length === 0 ? styles.emptyList : undefined}
      />

      {/* 載入中遮罩 */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>載入中...</Text>
        </View>
      )}

      {/* 刪除中遮罩 */}
      {deleteCardMutation.isPending && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#FF5252" />
          <Text style={styles.loadingText}>刪除中...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    paddingBottom: 16,
    marginBottom: 8,
  },
  quotaContainer: {
    padding: 16,
    backgroundColor: '#f9f9f9',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  quotaTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  quotaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  quotaText: {
    fontSize: 12,
    color: '#666',
  },
  quotaRemaining: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '600',
  },
  quotaExceeded: {
    color: '#FF5252',
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingTop: 16,
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
  },
  filterButtonActive: {
    backgroundColor: '#007AFF',
  },
  filterText: {
    fontSize: 14,
    color: '#666',
  },
  filterTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  emptyList: {
    flexGrow: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  errorText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#007AFF',
  },
  retryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#fff',
    fontWeight: '600',
  },
});
