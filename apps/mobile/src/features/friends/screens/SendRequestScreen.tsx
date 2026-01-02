/**
 * Send Friend Request Screen
 * 
 * Allows users to search for other users and send friend requests
 */

import React, { useState } from 'react';
import { Alert } from 'react-native';
import { Box } from '@/components/ui/box';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { Button, ButtonText } from '@/components/ui/button';
import { Input, InputField } from '@/components/ui/input';
import { Heading } from '@/components/ui/heading';
import { useSendFriendRequest } from '../hooks/useFriends';
import { useRouter } from 'expo-router';

export default function SendRequestScreen() {
  const router = useRouter();
  const [friendId, setFriendId] = useState('');
  const { mutate: sendRequest, isPending } = useSendFriendRequest();

  const handleSendRequest = () => {
    if (!friendId.trim()) {
      Alert.alert('錯誤', '請輸入好友 ID');
      return;
    }

    sendRequest(
      {
        body: {
          target_user_id: friendId.trim(),
        },
      },
      {
        onSuccess: () => {
          Alert.alert('成功', '好友邀請已發送', [
            {
              text: '確定',
              onPress: () => router.back(),
            },
          ]);
        },
        onError: (error: any) => {
          const message = error?.message || '發送邀請失敗，請稍後再試';
          Alert.alert('錯誤', message);
        },
      }
    );
  };

  return (
    <Box className="flex-1 bg-white p-4">
      <VStack className="space-y-4">
        <Heading size="lg" className="mb-2">
          新增好友
        </Heading>

        <Text className="text-gray-600 mb-4">
          輸入好友的 User ID 來發送好友邀請
        </Text>

        <VStack className="space-y-2">
          <Text className="font-medium text-gray-700">好友 ID</Text>
          <Input>
            <InputField
              placeholder="輸入好友 ID"
              value={friendId}
              onChangeText={setFriendId}
              autoCapitalize="none"
              autoCorrect={false}
            />
          </Input>
          <Text className="text-xs text-gray-500">
            可以在使用者的個人檔案中找到 ID
          </Text>
        </VStack>

        <Button
          onPress={handleSendRequest}
          isDisabled={isPending || !friendId.trim()}
          variant="solid"
          className="mt-6"
        >
          <ButtonText>{isPending ? '發送中...' : '發送好友邀請'}</ButtonText>
        </Button>

        <Button onPress={() => router.back()} variant="outline" className="mt-2">
          <ButtonText>取消</ButtonText>
        </Button>
      </VStack>

      {/* Info section */}
      <Box className="mt-8 p-4 bg-blue-50 rounded-lg">
        <Text className="text-sm text-blue-800 font-medium mb-2">💡 小提示</Text>
        <Text className="text-xs text-blue-700">
          • 只能向未封鎖的使用者發送邀請{'\n'}
          • 對方接受後即可開始聊天和交換小卡{'\n'}
          • 已經是好友的話會顯示錯誤訊息
        </Text>
      </Box>
    </Box>
  );
}
