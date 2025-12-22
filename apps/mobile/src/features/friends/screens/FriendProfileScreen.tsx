/**
 * Friend Profile Screen
 * 
 * Displays friend's profile with options to:
 * - Send message
 * - Block user
 * - View rating
 */

import React from 'react';
import { Alert, ScrollView, ActivityIndicator } from 'react-native';
import { Box } from '@/components/ui/box';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { HStack } from '@/components/ui/hstack';
import { Button, ButtonText } from '@/components/ui/button';
import { Heading } from '@/components/ui/heading';
import { useBlockUser } from '../hooks/useFriends';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { getAverageRatingApiV1RatingsUserUserIdAverageGetOptions } from '@/src/shared/api/generated/@tanstack/react-query.gen';

export default function FriendProfileScreen() {
  const router = useRouter();
  const { userId } = useLocalSearchParams<{ userId: string }>();
  const { mutate: blockUser, isPending: isBlocking } = useBlockUser();

  // Fetch user's average rating
  const { data: ratingData, isLoading: isLoadingRating } = useQuery({
    ...getAverageRatingApiV1RatingsUserUserIdAverageGetOptions({
      path: { user_id: userId || '' },
    }),
    enabled: !!userId,
  });

  const handleSendMessage = () => {
    // Navigate to chat (will be implemented in M402)
    Alert.alert('提示', '聊天功能即將推出');
  };

  const handleBlockUser = () => {
    Alert.alert('封鎖使用者', '確定要封鎖這位使用者嗎？封鎖後將無法互相發送訊息或交換小卡。', [
      {
        text: '取消',
        style: 'cancel',
      },
      {
        text: '封鎖',
        style: 'destructive',
        onPress: () => {
          if (!userId) return;

          blockUser(
            {
              body: {
                user_id: userId,
              },
            },
            {
              onSuccess: () => {
                Alert.alert('已封鎖', '已成功封鎖該使用者', [
                  {
                    text: '確定',
                    onPress: () => router.back(),
                  },
                ]);
              },
              onError: (error: any) => {
                const message = error?.message || '封鎖失敗，請稍後再試';
                Alert.alert('錯誤', message);
              },
            }
          );
        },
      },
    ]);
  };

  const renderRatingStars = (score: number, count: number) => {
    const fullStars = Math.floor(score);
    const hasHalfStar = score % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <HStack className="items-center space-x-1">
        {Array(fullStars)
          .fill(0)
          .map((_, i) => (
            <Text key={`full-${i}`} className="text-yellow-500 text-xl">
              ⭐
            </Text>
          ))}
        {hasHalfStar && <Text className="text-yellow-500 text-xl">⭐</Text>}
        {Array(emptyStars)
          .fill(0)
          .map((_, i) => (
            <Text key={`empty-${i}`} className="text-gray-300 text-xl">
              ☆
            </Text>
          ))}
        <Text className="text-sm text-gray-600 ml-2">
          {score.toFixed(1)} ({count} 評分)
        </Text>
      </HStack>
    );
  };

  if (!userId) {
    return (
      <Box className="flex-1 bg-white items-center justify-center">
        <Text className="text-red-500">無效的使用者 ID</Text>
      </Box>
    );
  }

  return (
    <ScrollView className="flex-1 bg-white">
      <Box className="p-4">
        <VStack className="space-y-6">
          {/* Profile header */}
          <VStack className="items-center space-y-4 py-6">
            {/* Avatar */}
            <Box className="w-24 h-24 bg-gray-300 rounded-full items-center justify-center">
              <Text className="text-white font-bold text-3xl">U</Text>
            </Box>

            <VStack className="items-center space-y-2">
              <Heading size="xl">使用者 {userId.slice(0, 8)}</Heading>
              <Text className="text-gray-600 text-center">
                ID: {userId}
              </Text>
            </VStack>
          </VStack>

          {/* Rating section */}
          <Box className="p-4 bg-gray-50 rounded-lg">
            <Text className="font-semibold text-gray-700 mb-3">使用者評分</Text>
            {isLoadingRating ? (
              <ActivityIndicator size="small" />
            ) : ratingData && ratingData.average_score > 0 ? (
              renderRatingStars(ratingData.average_score, ratingData.total_ratings)
            ) : (
              <Text className="text-gray-500 text-sm">尚無評分</Text>
            )}
          </Box>

          {/* Action buttons */}
          <VStack className="space-y-3 mt-4">
            <Button onPress={handleSendMessage} variant="solid">
              <ButtonText>💬 發送訊息</ButtonText>
            </Button>

            <Button
              onPress={handleBlockUser}
              variant="outline"
              isDisabled={isBlocking}
              className="border-red-500"
            >
              <ButtonText className="text-red-500">
                {isBlocking ? '封鎖中...' : '🚫 封鎖使用者'}
              </ButtonText>
            </Button>
          </VStack>

          {/* Info section */}
          <Box className="mt-4 p-4 bg-yellow-50 rounded-lg">
            <Text className="text-sm text-yellow-800 font-medium mb-2">
              ⚠️ 關於封鎖
            </Text>
            <Text className="text-xs text-yellow-700">
              封鎖後，你們將無法：{'\n'}
              • 互相發送訊息{'\n'}
              • 看到彼此的小卡{'\n'}
              • 發起交換提案{'\n'}
              {'\n'}
              可以在「已封鎖」頁面中解除封鎖
            </Text>
          </Box>
        </VStack>
      </Box>
    </ScrollView>
  );
}
