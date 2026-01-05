/**
 * Create Trade Proposal Screen
 * M501: 發起交換提案頁
 * 
 * 功能：
 * - 選擇交換對象（好友）
 * - 選擇自己的卡片
 * - 選擇對方的卡片
 * - 發起交換提案
 * 
 * 注意：完整實作需要卡片選擇器元件，這裡提供基本結構
 */

import React, { useState } from 'react';
import { ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import {
  Box,
  Text,
  Heading,
  VStack,
  Button,
  ButtonText,
  Spinner,
} from '@/components/ui';
import { useCreateTrade } from '@/src/features/trade/hooks/useTrade';

export default function CreateTradeScreen() {
  const router = useRouter();
  const createTrade = useCreateTrade();

  // State
  const [responderId, setResponderId] = useState<string>('');
  const [initiatorCardIds, setInitiatorCardIds] = useState<string[]>([]);
  const [responderCardIds, setResponderCardIds] = useState<string[]>([]);

  // 處理建立交換
  const handleCreateTrade = async () => {
    // 驗證
    if (!responderId) {
      Alert.alert('錯誤', '請選擇交換對象');
      return;
    }
    if (initiatorCardIds.length === 0) {
      Alert.alert('錯誤', '請至少選擇一張您的卡片');
      return;
    }
    if (responderCardIds.length === 0) {
      Alert.alert('錯誤', '請至少選擇一張對方的卡片');
      return;
    }

    try {
      await createTrade.mutateAsync({
        body: {
          responder_id: responderId,
          initiator_card_ids: initiatorCardIds,
          responder_card_ids: responderCardIds,
        },
      });

      Alert.alert('成功', '交換提案已發送', [
        {
          text: '確定',
          onPress: () => router.push('/trade/history'),
        },
      ]);
    } catch (error: any) {
      Alert.alert('錯誤', error.message || '發送提案失敗');
    }
  };

  return (
    <Box className="flex-1 bg-gray-50">
      <ScrollView>
        {/* Header */}
        <Box className="bg-white px-6 py-4 border-b border-gray-200">
          <Heading className="text-2xl font-bold">發起交換提案</Heading>
        </Box>

        {/* Content */}
        <VStack className="p-6 space-y-6">
          {/* 步驟 1: 選擇交換對象 */}
          <Box className="bg-white p-6 rounded-lg">
            <Text className="text-lg font-bold mb-4">1. 選擇交換對象</Text>
            <Text className="text-gray-600 mb-4">
              請選擇一位好友進行交換
            </Text>
            {/* TODO: 實作好友選擇器 */}
            <Box className="bg-gray-100 p-4 rounded-lg">
              <Text className="text-gray-500 text-center">
                [好友選擇器]
              </Text>
            </Box>
          </Box>

          {/* 步驟 2: 選擇您的卡片 */}
          <Box className="bg-white p-6 rounded-lg">
            <Text className="text-lg font-bold mb-4">2. 選擇您的卡片</Text>
            <Text className="text-gray-600 mb-4">
              選擇您要交換出去的卡片
            </Text>
            {/* TODO: 實作卡片選擇器 */}
            <Box className="bg-gray-100 p-4 rounded-lg">
              <Text className="text-gray-500 text-center">
                [卡片選擇器]
              </Text>
              <Text className="text-gray-500 text-center mt-2">
                已選擇: {initiatorCardIds.length} 張
              </Text>
            </Box>
          </Box>

          {/* 步驟 3: 選擇對方的卡片 */}
          <Box className="bg-white p-6 rounded-lg">
            <Text className="text-lg font-bold mb-4">3. 選擇對方的卡片</Text>
            <Text className="text-gray-600 mb-4">
              選擇您想要的對方卡片
            </Text>
            {/* TODO: 實作卡片選擇器 */}
            <Box className="bg-gray-100 p-4 rounded-lg">
              <Text className="text-gray-500 text-center">
                [卡片選擇器]
              </Text>
              <Text className="text-gray-500 text-center mt-2">
                已選擇: {responderCardIds.length} 張
              </Text>
            </Box>
          </Box>

          {/* 提交按鈕 */}
          <Box className="pt-4">
            <Button
              onPress={handleCreateTrade}
              className="bg-blue-600"
              disabled={createTrade.isPending}
            >
              {createTrade.isPending ? (
                <Spinner color="white" />
              ) : (
                <ButtonText>發送交換提案</ButtonText>
              )}
            </Button>

            <Text className="text-gray-500 text-sm text-center mt-4">
              提案發送後，對方可以選擇接受或拒絕
            </Text>
          </Box>
        </VStack>
      </ScrollView>
    </Box>
  );
}
