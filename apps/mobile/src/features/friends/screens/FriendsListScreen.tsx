/**
 * Friends List Screen
 * 
 * Displays list of friends with tabs for different statuses:
 * - All: Accepted friends
 * - Pending: Friend requests waiting for response
 * - Blocked: Blocked users
 */

import React, { useState } from 'react';
import { FlatList, RefreshControl, ActivityIndicator } from 'react-native';
import { Box } from '@/src/shared/ui/components/box';
import { Text } from '@/src/shared/ui/components/text';
import { Pressable } from '@/src/shared/ui/components/pressable';
import { HStack } from '@/src/shared/ui/components/hstack';
import { VStack } from '@/src/shared/ui/components/vstack';
import { Button, ButtonText } from '@/src/shared/ui/components/button';
import { Heading } from '@/src/shared/ui/components/heading';
import { useFriendsList, useUnblockUser } from '../hooks/useFriends';
import type { FriendsTab, FriendshipStatus } from '../types';
import { useRouter } from 'expo-router';
import { Alert } from 'react-native';

export default function FriendsListScreen() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<FriendsTab>('all');
  const { mutate: unblockUser, isPending: isUnblocking } = useUnblockUser();

  // Map tab to API status filter
  const statusFilter: FriendshipStatus | undefined =
    activeTab === 'all' ? 'accepted' : activeTab === 'pending' ? 'pending' : 'blocked';

  const { data: friends, isLoading, refetch, isRefetching } = useFriendsList(statusFilter);

  const handleAddFriend = () => {
    router.push('/friends/add');
  };

  const handleFriendPress = (userId: string) => {
    router.push(`/friends/${userId}`);
  };

  const handleUnblockUser = (userId: string, nickname?: string) => {
    Alert.alert(
      '解除封鎖',
      `確定要解除封鎖 ${nickname || '這位使用者'} 嗎？解除後你們將可以重新互動。`,
      [
        {
          text: '取消',
          style: 'cancel',
        },
        {
          text: '解除封鎖',
          onPress: () => {
            unblockUser(
              {
                body: {
                  user_id: userId,
                },
              },
              {
                onSuccess: () => {
                  Alert.alert('已解除封鎖', '已成功解除封鎖該使用者');
                },
                onError: (error: unknown) => {
                  const message =
                    error && typeof error === 'object' && 'message' in error
                      ? String((error as { message: unknown }).message)
                      : '解除封鎖失敗，請稍後再試';
                  Alert.alert('錯誤', message);
                },
              }
            );
          },
        },
      ]
    );
  };

  const renderTabButton = (tab: FriendsTab, label: string) => (
    <Pressable
      onPress={() => setActiveTab(tab)}
      className={`flex-1 py-3 border-b-2 ${
        activeTab === tab ? 'border-primary-500' : 'border-gray-200'
      }`}
    >
      <Text
        className={`text-center font-medium ${
          activeTab === tab ? 'text-primary-600' : 'text-gray-500'
        }`}
      >
        {label}
      </Text>
    </Pressable>
  );

  const renderFriendItem = ({ item }: { item: any }) => (
    <Box className="bg-white p-4 mb-2 rounded-lg shadow-sm">
      <HStack className="items-center space-x-3">
        {/* Avatar placeholder */}
        <Box className="w-12 h-12 bg-gray-300 rounded-full items-center justify-center">
          <Text className="text-white font-bold text-lg">
            {item.nickname?.[0]?.toUpperCase() || 'U'}
          </Text>
        </Box>

        {/* Friend info */}
        <VStack className="flex-1">
          <Text className="font-semibold text-gray-900">
            {/* Display nickname or fallback to User ID. user_id is used for blocked users, friend_id for others */}
            {item.nickname || `User ${item.user_id?.slice(0, 8) || item.friend_id?.slice(0, 8)}`}
          </Text>
          {item.bio && (
            <Text className="text-sm text-gray-600" numberOfLines={1}>
              {item.bio}
            </Text>
          )}
          {activeTab === 'pending' && (
            <Text className="text-xs text-orange-500 mt-1">等待回應</Text>
          )}
          {activeTab === 'blocked' && (
            <Text className="text-xs text-red-500 mt-1">已封鎖</Text>
          )}
        </VStack>

        {/* Action buttons */}
        {activeTab === 'blocked' ? (
          <Button
            onPress={() => handleUnblockUser(item.user_id, item.nickname)}
            size="sm"
            variant="outline"
            disabled={isUnblocking}
          >
            <ButtonText className="text-sm">
              {isUnblocking ? '處理中...' : '解除封鎖'}
            </ButtonText>
          </Button>
        ) : activeTab === 'all' ? (
          <Pressable onPress={() => handleFriendPress(item.user_id)}>
            <Box className="w-3 h-3 bg-green-500 rounded-full" />
          </Pressable>
        ) : null}
      </HStack>
    </Box>
  );

  const renderEmptyState = () => (
    <Box className="flex-1 items-center justify-center p-8">
      <Text className="text-gray-500 text-center mb-4">
        {activeTab === 'all' && '目前沒有好友'}
        {activeTab === 'pending' && '沒有待處理的好友邀請'}
        {activeTab === 'blocked' && '沒有封鎖的使用者'}
      </Text>
      {activeTab === 'all' && (
        <Button onPress={handleAddFriend} variant="solid">
          <ButtonText>新增好友</ButtonText>
        </Button>
      )}
      {activeTab === 'blocked' && (
        <Text className="text-gray-400 text-sm text-center mt-2">
          解除封鎖後，你們將可以重新互動
        </Text>
      )}
    </Box>
  );

  return (
    <Box className="flex-1 bg-gray-50">
      {/* Header */}
      <Box className="bg-white px-4 pt-4 pb-2">
        <HStack className="items-center justify-between mb-4">
          <Heading size="xl">好友</Heading>
          <Button onPress={handleAddFriend} size="sm" variant="outline">
            <ButtonText>+ 新增</ButtonText>
          </Button>
        </HStack>

        {/* Tabs */}
        <HStack className="space-x-0">
          {renderTabButton('all', '好友')}
          {renderTabButton('pending', '待處理')}
          {renderTabButton('blocked', '已封鎖')}
        </HStack>
      </Box>

      {/* Friends list */}
      {isLoading ? (
        <Box className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#6366f1" />
        </Box>
      ) : (
        <FlatList
          data={friends || []}
          renderItem={renderFriendItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: 16 }}
          ListEmptyComponent={renderEmptyState}
          refreshControl={
            <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
          }
        />
      )}
    </Box>
  );
}
