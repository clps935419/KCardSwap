/**
 * M703: 貼文詳情與「有興趣」
 * Post Detail Screen
 * 
 * 功能：
 * - 顯示貼文完整內容
 * - 表達「有興趣」
 * - 查看貼文狀態
 * 
 * 使用 Gluestack UI 元件
 */

import React from 'react';
import { ScrollView, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import {
  Box,
  Text,
  Button,
  ButtonText,
  Spinner,
  Pressable,
} from '@/src/shared/ui/components';
import { useExpressInterest } from '@/src/features/posts/hooks/usePosts';
// Note: In real implementation, we need a hook to fetch single post
// For now, we'll use a placeholder

export function PostDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ id: string }>();
  const postId = params.id;

  const expressInterestMutation = useExpressInterest();

  // TODO: Add useFetchPost hook to fetch single post details
  // const { data: post, isLoading, error } = useFetchPost(postId);
  
  // Placeholder data for demonstration
  const isLoading = false;
  const error = null;
  const post = {
    id: postId,
    owner_id: 'owner-123',
    city_code: 'TPE',
    title: '徵求 BTS Jungkook 小卡',
    content: '我想用我的 IU 小卡交換 BTS Jungkook 的小卡。我有多個版本，歡迎聊聊交換細節。',
    idol: 'Jungkook',
    idol_group: 'BTS',
    status: 'open' as const,
    expires_at: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  const handleExpressInterest = async () => {
    if (!postId) return;

    try {
      await expressInterestMutation.mutateAsync(postId);
      
      Alert.alert(
        '成功',
        '已送出興趣請求！作者將會收到通知，並可選擇接受或拒絕。',
        [
          {
            text: '確定',
            onPress: () => router.back(),
          },
        ]
      );
    } catch (error: any) {
      let errorMessage = '請稍後再試';
      
      if (error.response?.status === 409) {
        errorMessage = '您已經表達過興趣了';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Alert.alert('操作失敗', errorMessage);
    }
  };

  if (isLoading) {
    return (
      <Box className="flex-1 items-center justify-center bg-gray-50">
        <Spinner size="large" />
        <Text className="mt-4 text-gray-600">載入中...</Text>
      </Box>
    );
  }

  if (error || !post) {
    return (
      <Box className="flex-1 items-center justify-center bg-gray-50 px-4">
        <Text className="text-lg text-red-600 text-center mb-4">
          載入失敗
        </Text>
        <Text className="text-sm text-gray-600 text-center mb-4">
          {error instanceof Error ? error.message : '找不到此貼文'}
        </Text>
        <Button onPress={() => router.back()}>
          <ButtonText>返回</ButtonText>
        </Button>
      </Box>
    );
  }

  const isExpired = new Date(post.expires_at) < new Date();
  const isClosed = post.status === 'closed';
  const canExpressInterest = !isExpired && !isClosed && post.status === 'open';

  return (
    <Box className="flex-1 bg-gray-50">
      <ScrollView className="flex-1 px-4 py-6">
        {/* 貼文標題 */}
        <Text className="text-2xl font-bold text-gray-900 mb-4">
          {post.title}
        </Text>

        {/* 貼文狀態 */}
        <Box className="flex-row items-center gap-2 mb-4">
          <Box
            className={`px-3 py-1 rounded-full ${
              isClosed || isExpired ? 'bg-gray-200' : 'bg-green-100'
            }`}
          >
            <Text
              className={`text-xs font-semibold ${
                isClosed || isExpired ? 'text-gray-600' : 'text-green-700'
              }`}
            >
              {isClosed ? '已關閉' : isExpired ? '已到期' : '開放中'}
            </Text>
          </Box>
        </Box>

        {/* 偶像/團體標籤 */}
        {(post.idol || post.idol_group) && (
          <Box className="flex-row flex-wrap gap-2 mb-4">
            {post.idol && (
              <Box className="px-3 py-1 bg-blue-100 rounded-full">
                <Text className="text-sm text-blue-700 font-semibold">
                  {post.idol}
                </Text>
              </Box>
            )}
            {post.idol_group && (
              <Box className="px-3 py-1 bg-purple-100 rounded-full">
                <Text className="text-sm text-purple-700 font-semibold">
                  {post.idol_group}
                </Text>
              </Box>
            )}
          </Box>
        )}

        {/* 貼文內容 */}
        <Box className="mb-6 p-4 bg-white rounded-lg shadow-sm">
          <Text className="text-base text-gray-800 leading-6">
            {post.content}
          </Text>
        </Box>

        {/* 貼文資訊 */}
        <Box className="mb-6 p-4 bg-gray-100 rounded-lg">
          <Text className="text-xs text-gray-600 mb-1">
            📍 城市: {post.city_code}
          </Text>
          <Text className="text-xs text-gray-600 mb-1">
            📅 發布時間: {new Date(post.created_at).toLocaleDateString('zh-TW')}
          </Text>
          <Text className="text-xs text-gray-600">
            ⏰ 到期時間: {new Date(post.expires_at).toLocaleDateString('zh-TW')}
          </Text>
        </Box>

        {/* 提示訊息 */}
        {!canExpressInterest && (
          <Box className="mb-4 p-3 bg-yellow-50 rounded-lg">
            <Text className="text-sm text-yellow-800">
              {isClosed
                ? '此貼文已關閉，無法表達興趣'
                : isExpired
                ? '此貼文已到期，無法表達興趣'
                : '此貼文目前無法表達興趣'}
            </Text>
          </Box>
        )}

        {/* 表達興趣按鈕 */}
        {canExpressInterest && (
          <Button
            size="lg"
            variant="solid"
            action="primary"
            className="w-full mb-3"
            onPress={handleExpressInterest}
            disabled={expressInterestMutation.isPending}
          >
            {expressInterestMutation.isPending ? (
              <Spinner color="white" />
            ) : (
              <ButtonText>我有興趣 ❤️</ButtonText>
            )}
          </Button>
        )}

        {/* 返回按鈕 */}
        <Button
          size="lg"
          variant="outline"
          action="secondary"
          className="w-full"
          onPress={() => router.back()}
        >
          <ButtonText>返回列表</ButtonText>
        </Button>
      </ScrollView>
    </Box>
  );
}
