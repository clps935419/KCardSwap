/**
 * UserProfileScreen
 * 
 * Instagram-style user profile view:
 * - Top: Profile header with user info
 * - Bottom: Card grid with user's gallery cards
 */

import React from 'react';
import { Alert, ScrollView } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Box, Text, Spinner, Button, ButtonText } from '@/src/shared/ui/components';
import {
  getUserProfileApiV1ProfileUserIdGetOptions,
  getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions,
} from '@/src/shared/api/generated/@tanstack/react-query.gen';
import { ProfileHeader, CardGrid } from '@/src/features/profile/components';
import { useBlockUser } from '@/src/features/friends/hooks/useFriends';
import type { GalleryCardResponse } from '@/src/shared/api/sdk';

export default function UserProfileScreen() {
  const router = useRouter();
  const { userId } = useLocalSearchParams<{ userId: string }>();
  const { mutate: blockUser, isPending: isBlocking } = useBlockUser();

  // Fetch user profile
  const {
    data: profileData,
    isLoading: isLoadingProfile,
    error: profileError,
  } = useQuery({
    ...getUserProfileApiV1ProfileUserIdGetOptions({
      path: { user_id: userId || '' },
    }),
    enabled: !!userId,
  });

  // Fetch user's gallery cards
  const {
    data: cardsData,
    isLoading: isLoadingCards,
    error: cardsError,
  } = useQuery({
    ...getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions({
      path: { user_id: userId || '' },
    }),
    enabled: !!userId,
  });

  const handleCardPress = (card: GalleryCardResponse) => {
    // Navigate to card detail (to be implemented)
    Alert.alert('小卡詳情', `${card.idol_name} - ${card.title || '無標題'}`);
  };

  const handleSendMessage = () => {
    // Navigate to chat (will be implemented in M402)
    Alert.alert('提示', '聊天功能即將推出');
  };

  const handleBlockUser = () => {
    Alert.alert(
      '封鎖使用者',
      '確定要封鎖這位使用者嗎？封鎖後將無法互相發送訊息或交換小卡。',
      [
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
      ]
    );
  };

  if (!userId) {
    return (
      <Box className="flex-1 bg-white items-center justify-center">
        <Text className="text-red-500">無效的使用者 ID</Text>
      </Box>
    );
  }

  if (isLoadingProfile) {
    return (
      <Box className="flex-1 bg-white items-center justify-center">
        <Spinner size="large" />
        <Text className="mt-4 text-gray-600">載入個人資料中...</Text>
      </Box>
    );
  }

  if (profileError || !profileData?.data) {
    const errorMessage =
      profileError && typeof profileError === 'object' && 'message' in profileError
        ? String((profileError as any).message)
        : '找不到使用者';

    return (
      <Box className="flex-1 bg-white items-center justify-center p-4">
        <Text className="text-red-500 text-center mb-4">
          載入個人資料失敗
        </Text>
        <Text className="text-gray-600 text-center">{errorMessage}</Text>
      </Box>
    );
  }

  const profile = profileData.data;
  const cards = cardsData?.items || [];

  return (
    <Box className="flex-1 bg-white">
      <ScrollView>
        {/* Profile Header (IG-style) */}
        <ProfileHeader profile={profile} isOwnProfile={false} />

        {/* Action Buttons */}
        <Box className="px-4 py-4 border-b border-gray-200">
          <Box className="flex-row gap-3">
            <Button
              onPress={handleSendMessage}
              variant="solid"
              className="flex-1 bg-blue-500"
            >
              <ButtonText>💬 發送訊息</ButtonText>
            </Button>

            <Button
              onPress={handleBlockUser}
              variant="outline"
              disabled={isBlocking}
              className="border-red-500"
            >
              <ButtonText className="text-red-500">
                {isBlocking ? '...' : '🚫'}
              </ButtonText>
            </Button>
          </Box>
        </Box>

        {/* Gallery Cards Grid */}
        <Box className="flex-1 pt-2">
          <Box className="px-4 py-3 border-b border-gray-100">
            <Text className="font-bold text-gray-700">相簿 📸</Text>
          </Box>
          <CardGrid
            cards={cards}
            onCardPress={handleCardPress}
            isLoading={isLoadingCards}
          />
        </Box>
      </ScrollView>
    </Box>
  );
}
