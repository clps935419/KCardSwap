/**
 * Chat Rooms List Screen
 * 
 * Displays list of all chat rooms with:
 * - Last message preview
 * - Unread count badge
 * - Pull-to-refresh
 */

import React from 'react';
import { FlatList, RefreshControl, ActivityIndicator } from 'react-native';
import { Box } from '@/components/ui/box';
import { Text } from '@/components/ui/text';
import { Pressable } from '@/components/ui/pressable';
import { HStack } from '@/components/ui/hstack';
import { VStack } from '@/components/ui/vstack';
import { Heading } from '@/components/ui/heading';
import { Badge, BadgeText } from '@/components/ui/badge';
import { useChatRooms } from '../hooks/useChat';
import { useRouter } from 'expo-router';

export default function ChatRoomsScreen() {
  const router = useRouter();
  const { data: rooms, isLoading, refetch, isRefetching } = useChatRooms();

  const handleRoomPress = (roomId: string) => {
    router.push(`/chat/${roomId}`);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('zh-TW', {
        hour: '2-digit',
        minute: '2-digit',
      });
    } else {
      return date.toLocaleDateString('zh-TW', {
        month: 'numeric',
        day: 'numeric',
      });
    }
  };

  const renderChatRoom = ({ item }: { item: any }) => {
    const lastMessage = item.last_message;
    const hasUnread = (item.unread_count || 0) > 0;

    return (
      <Pressable onPress={() => handleRoomPress(item.id)}>
        <Box className="bg-white px-4 py-3 border-b border-gray-200">
          <HStack className="items-center space-x-3">
            {/* Avatar */}
            <Box className="w-12 h-12 bg-gray-300 rounded-full items-center justify-center">
              <Text className="text-white font-bold text-lg">
                {item.other_participant?.nickname?.[0]?.toUpperCase() || 'U'}
              </Text>
            </Box>

            {/* Room info */}
            <VStack className="flex-1">
              <HStack className="items-center justify-between mb-1">
                <Text className={`font-semibold ${hasUnread ? 'text-gray-900' : 'text-gray-700'}`}>
                  {item.other_participant?.nickname || `Room ${item.id.slice(0, 8)}`}
                </Text>
                {lastMessage && (
                  <Text className="text-xs text-gray-500">
                    {formatTime(lastMessage.created_at)}
                  </Text>
                )}
              </HStack>

              <HStack className="items-center justify-between">
                <Text
                  className={`text-sm ${hasUnread ? 'text-gray-900 font-medium' : 'text-gray-600'}`}
                  numberOfLines={1}
                >
                  {lastMessage?.content || '開始聊天'}
                </Text>

                {hasUnread && (
                  <Badge size="sm" variant="solid" className="bg-primary-500">
                    <BadgeText className="text-white">
                      {item.unread_count > 99 ? '99+' : item.unread_count}
                    </BadgeText>
                  </Badge>
                )}
              </HStack>
            </VStack>
          </HStack>
        </Box>
      </Pressable>
    );
  };

  const renderEmptyState = () => (
    <Box className="flex-1 items-center justify-center p-8">
      <Text className="text-6xl mb-4">💬</Text>
      <Text className="text-gray-500 text-center text-lg font-medium mb-2">
        尚無聊天室
      </Text>
      <Text className="text-gray-400 text-center text-sm">
        新增好友後即可開始聊天
      </Text>
    </Box>
  );

  return (
    <Box className="flex-1 bg-white">
      {/* Header */}
      <Box className="bg-white px-4 pt-4 pb-2 border-b border-gray-200">
        <Heading size="xl">聊天</Heading>
      </Box>

      {/* Chat rooms list */}
      {isLoading ? (
        <Box className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#6366f1" />
        </Box>
      ) : (
        <FlatList
          data={rooms || []}
          renderItem={renderChatRoom}
          keyExtractor={(item) => item.id}
          ListEmptyComponent={renderEmptyState}
          refreshControl={
            <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
          }
        />
      )}
    </Box>
  );
}
