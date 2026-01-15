/**
 * Chat Room Screen
 * 
 * Single chat room with:
 * - Message list (scrollable, inverted)
 * - Message input field
 * - Auto-polling with backoff (M403)
 * - Auto-scroll to bottom on new messages
 */

import React, { useState, useRef, useEffect } from 'react';
import { FlatList, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Box } from '@/src/shared/ui/components/box';
import { Text } from '@/src/shared/ui/components/text';
import { HStack } from '@/src/shared/ui/components/hstack';
import { VStack } from '@/src/shared/ui/components/vstack';
import { Input, InputField } from '@/src/shared/ui/components/input';
import { Button, ButtonText } from '@/src/shared/ui/components/button';
import { useSendMessage } from '../hooks/useChat';
import { useMessagePolling } from '../services/polling';
import { useLocalSearchParams } from 'expo-router';
import { useAuthStore } from '@/src/shared/state/authStore';

export default function ChatRoomScreen() {
  const { roomId } = useLocalSearchParams<{ roomId: string }>();
  const { user } = useAuthStore();
  const [messageText, setMessageText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  // Use polling hook with backoff (M403)
  const { messages, refetch, pollInterval, isActive } = useMessagePolling(roomId || '');

  // Send message mutation
  const { mutate: sendMessage, isPending: isSending } = useSendMessage(roomId || '');

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToOffset({ offset: 0, animated: true });
      }, 100);
    }
  }, [messages.length]);

  const handleSendMessage = () => {
    if (!messageText.trim() || isSending) return;

    sendMessage(
      {
        path: { room_id: roomId || '' },
        body: {
          content: messageText.trim(),
        },
      },
      {
        onSuccess: () => {
          setMessageText('');
          // Trigger immediate refetch and reset poll interval
          refetch();
        },
        onError: (error: any) => {
          Alert.alert('錯誤', error?.message || '發送訊息失敗');
        },
      }
    );
  };

  const renderMessage = ({ item }: { item: any }) => {
    const isOwnMessage = item.sender_id === user?.id;
    const messageTime = new Date(item.created_at).toLocaleTimeString('zh-TW', {
      hour: '2-digit',
      minute: '2-digit',
    });

    return (
      <Box className={`mb-3 ${isOwnMessage ? 'items-end' : 'items-start'}`}>
        <Box
          className={`max-w-[75%] px-4 py-2 rounded-2xl ${
            isOwnMessage
              ? 'bg-primary-500 rounded-tr-sm'
              : 'bg-gray-200 rounded-tl-sm'
          }`}
        >
          <Text className={isOwnMessage ? 'text-white' : 'text-gray-900'}>
            {item.content}
          </Text>
        </Box>
        <HStack className="items-center space-x-2 mt-1 px-2">
          <Text className="text-xs text-gray-500">{messageTime}</Text>
          {isOwnMessage && (
            <Text className="text-xs text-gray-500">
              {item.status === 'read' ? '已讀' : item.status === 'delivered' ? '已送達' : '已發送'}
            </Text>
          )}
        </HStack>
      </Box>
    );
  };

  const renderEmptyState = () => (
    <Box className="flex-1 items-center justify-center p-8">
      <Text className="text-6xl mb-4">👋</Text>
      <Text className="text-gray-500 text-center">
        開始聊天吧！
      </Text>
    </Box>
  );

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-white"
      keyboardVerticalOffset={90}
    >
      {/* Debug info (dev mode only) */}
      {__DEV__ && (
        <Box className="bg-yellow-100 px-3 py-1">
          <Text className="text-xs text-yellow-800">
            輪詢: {pollInterval / 1000}s | 狀態: {isActive ? '活動' : '暫停'} | 訊息: {messages.length}
          </Text>
        </Box>
      )}

      {/* Messages list (inverted) */}
      <FlatList
        ref={flatListRef}
        inverted
        data={[...messages].reverse()} // Reverse to show newest at bottom
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16, flexGrow: 1 }}
        ListEmptyComponent={renderEmptyState}
      />

      {/* Message input */}
      <Box className="border-t border-gray-200 bg-white px-4 py-3">
        <HStack className="items-end space-x-2">
          <Box className="flex-1">
            <Input>
              <InputField
                placeholder="輸入訊息..."
                value={messageText}
                onChangeText={setMessageText}
                multiline
                maxLength={500}
                editable={!isSending}
              />
            </Input>
          </Box>

          <Button
            onPress={handleSendMessage}
            disabled={!messageText.trim() || isSending}
            size="md"
            variant="solid"
          >
            <ButtonText>{isSending ? '...' : '發送'}</ButtonText>
          </Button>
        </HStack>
      </Box>
    </KeyboardAvoidingView>
  );
}
