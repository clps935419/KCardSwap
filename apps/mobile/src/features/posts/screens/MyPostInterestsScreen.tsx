/**
 * M704: 作者端興趣清單與接受導流聊天
 * My Post Interests Screen
 * 
 * 功能：
 * - 顯示作者貼文收到的興趣清單
 * - 接受興趣請求（自動建立好友+聊天室）
 * - 拒絕興趣請求
 * - 導向聊天室
 * 
 * 使用 Gluestack UI 元件
 */

import React from 'react';
import { FlatList, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import {
  Box,
  Text,
  Button,
  ButtonText,
  Spinner,
  Pressable,
} from '@/src/shared/ui/components';
import {
  usePostInterests,
  useAcceptInterest,
  useRejectInterest,
} from '@/src/features/posts/hooks/usePosts';
import type { PostInterest } from '@/src/features/posts/types';

export function MyPostInterestsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ postId: string }>();
  const postId = params.postId;

  const { data: interests, isLoading, error, refetch } = usePostInterests(postId);
  const acceptMutation = useAcceptInterest();
  const rejectMutation = useRejectInterest();

  const handleAccept = async (interest: PostInterest) => {
    Alert.alert(
      '接受興趣',
      '接受後將自動建立好友關係並開啟聊天室，是否繼續？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '接受',
          onPress: async () => {
            try {
              const result = await acceptMutation.mutateAsync({
                postId,
                interestId: interest.id,
              });

              Alert.alert(
                '成功',
                result.friendship_created
                  ? '已建立好友關係並開啟聊天室'
                  : '聊天室已開啟（已是好友）',
                [
                  {
                    text: '前往聊天',
                    onPress: () => {
                      router.push(`/chat/${result.chat_room_id}`);
                    },
                  },
                  {
                    text: '稍後',
                    style: 'cancel',
                  },
                ]
              );
            } catch (error: any) {
              Alert.alert(
                '操作失敗',
                error.response?.data?.detail || error.message || '請稍後再試'
              );
            }
          },
        },
      ]
    );
  };

  const handleReject = async (interest: PostInterest) => {
    Alert.alert('拒絕興趣', '確定要拒絕此興趣請求嗎？', [
      { text: '取消', style: 'cancel' },
      {
        text: '拒絕',
        style: 'destructive',
        onPress: async () => {
          try {
            await rejectMutation.mutateAsync({
              postId,
              interestId: interest.id,
            });

            Alert.alert('已拒絕', '已拒絕該興趣請求');
          } catch (error: any) {
            Alert.alert(
              '操作失敗',
              error.response?.data?.detail || error.message || '請稍後再試'
            );
          }
        },
      },
    ]);
  };

  const renderInterestItem = ({ item: interest }: { item: PostInterest }) => {
    const isPending = interest.status === 'pending';
    const isAccepted = interest.status === 'accepted';
    const isRejected = interest.status === 'rejected';

    return (
      <Box className="p-4 mb-3 bg-white rounded-lg shadow-sm border border-gray-200">
        {/* 使用者資訊 (在實際實作中應該顯示使用者名稱) */}
        <Box className="flex-row items-center justify-between mb-3">
          <Box className="flex-1">
            <Text className="text-base font-bold text-gray-900">
              用戶 {interest.user_id.substring(0, 8)}...
            </Text>
            <Text className="text-xs text-gray-500">
              {new Date(interest.created_at).toLocaleDateString('zh-TW')} 表達興趣
            </Text>
          </Box>

          {/* 狀態標籤 */}
          <Box
            className={`px-3 py-1 rounded-full ${
              isPending
                ? 'bg-yellow-100'
                : isAccepted
                ? 'bg-green-100'
                : 'bg-gray-200'
            }`}
          >
            <Text
              className={`text-xs font-semibold ${
                isPending
                  ? 'text-yellow-700'
                  : isAccepted
                  ? 'text-green-700'
                  : 'text-gray-600'
              }`}
            >
              {isPending ? '待處理' : isAccepted ? '已接受' : '已拒絕'}
            </Text>
          </Box>
        </Box>

        {/* 操作按鈕 (只顯示在 pending 狀態) */}
        {isPending && (
          <Box className="flex-row gap-2">
            <Button
              size="md"
              variant="solid"
              action="positive"
              className="flex-1"
              onPress={() => handleAccept(interest)}
              disabled={acceptMutation.isPending || rejectMutation.isPending}
            >
              {acceptMutation.isPending && acceptMutation.variables?.interestId === interest.id ? (
                <Spinner size="small" color="white" />
              ) : (
                <ButtonText>接受</ButtonText>
              )}
            </Button>

            <Button
              size="md"
              variant="outline"
              action="negative"
              className="flex-1"
              onPress={() => handleReject(interest)}
              disabled={acceptMutation.isPending || rejectMutation.isPending}
            >
              {rejectMutation.isPending && rejectMutation.variables?.interestId === interest.id ? (
                <Spinner size="small" />
              ) : (
                <ButtonText>拒絕</ButtonText>
              )}
            </Button>
          </Box>
        )}

        {/* 已接受狀態提示 */}
        {isAccepted && (
          <Box className="mt-2">
            <Text className="text-sm text-green-700">
              ✓ 已建立好友關係並開啟聊天室
            </Text>
          </Box>
        )}
      </Box>
    );
  };

  const renderEmpty = () => (
    <Box className="items-center justify-center py-12 px-4">
      <Text className="text-lg text-gray-500 text-center mb-2">
        目前沒有興趣請求
      </Text>
      <Text className="text-sm text-gray-400 text-center">
        當有人對您的貼文表達興趣時，會顯示在這裡
      </Text>
    </Box>
  );

  if (isLoading) {
    return (
      <Box className="flex-1 items-center justify-center bg-gray-50">
        <Spinner size="large" />
        <Text className="mt-4 text-gray-600">載入中...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className="flex-1 items-center justify-center bg-gray-50 px-4">
        <Text className="text-lg text-red-600 text-center mb-4">
          載入失敗
        </Text>
        <Text className="text-sm text-gray-600 text-center mb-4">
          {error instanceof Error ? error.message : '請稍後再試'}
        </Text>
        <Button onPress={() => refetch()}>
          <ButtonText>重試</ButtonText>
        </Button>
      </Box>
    );
  }

  return (
    <Box className="flex-1 bg-gray-50">
      <FlatList
        data={interests || []}
        renderItem={renderInterestItem}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={{ padding: 16 }}
      />
    </Box>
  );
}
