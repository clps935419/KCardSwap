import { ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@/src/shared/state/authStore';
import { Box } from '@/src/shared/ui/components/box';
import { Text } from '@/src/shared/ui/components/text';
import { Heading } from '@/src/shared/ui/components/heading';
import { Pressable } from '@/src/shared/ui/components/pressable';
import { HStack } from '@/src/shared/ui/components/hstack';
import { VStack } from '@/src/shared/ui/components/vstack';
import { Card } from '@/src/shared/ui/components/card';

export default function HomeScreen() {
  const { user } = useAuthStore();
  const router = useRouter();

  return (
    <ScrollView className="flex-1 bg-gray-50">
      <Box className="p-4">
        {/* Welcome Header */}
        <Box className="mb-6">
          <Heading size="2xl" className="text-gray-800 mb-2">
            歡迎回來！
          </Heading>
          {user && (
            <Text className="text-gray-600">
              Hello, {user.nickname || user.email}
            </Text>
          )}
        </Box>

        {/* Quick Actions */}
        <Box className="mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            快速導航
          </Text>
          <HStack className="space-x-3">
            {/* Friends Entry */}
            <Pressable
              onPress={() => router.push('/friends')}
              className="flex-1"
            >
              <Card className="bg-blue-50 p-4 items-center">
                <Text className="text-3xl mb-2">👥</Text>
                <Text className="font-semibold text-blue-900">好友</Text>
                <Text className="text-sm text-blue-700">管理好友關係</Text>
              </Card>
            </Pressable>

            {/* Chat Entry */}
            <Pressable
              onPress={() => router.push('/chat')}
              className="flex-1"
            >
              <Card className="bg-green-50 p-4 items-center">
                <Text className="text-3xl mb-2">💬</Text>
                <Text className="font-semibold text-green-900">聊天</Text>
                <Text className="text-sm text-green-700">即時訊息</Text>
              </Card>
            </Pressable>
          </HStack>
        </Box>

        {/* Feature Status */}
        <Box className="mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            功能狀態
          </Text>
          <Card className="p-4">
            <VStack className="space-y-2">
              <HStack className="items-center space-x-2">
                <Text className="text-green-500">✅</Text>
                <Text className="text-gray-700">US1: Google 登入與個人檔案</Text>
              </HStack>
              <HStack className="items-center space-x-2">
                <Text className="text-green-500">✅</Text>
                <Text className="text-gray-700">US2: 小卡上傳 (部分完成)</Text>
              </HStack>
              <HStack className="items-center space-x-2">
                <Text className="text-green-500">✅</Text>
                <Text className="text-gray-700">US3: 附近搜尋</Text>
              </HStack>
              <HStack className="items-center space-x-2">
                <Text className="text-green-500">✅</Text>
                <Text className="text-gray-700">US4: 好友系統與聊天 (Phase 6)</Text>
              </HStack>
              <HStack className="items-center space-x-2">
                <Text className="text-orange-500">⏳</Text>
                <Text className="text-gray-700">US5: 小卡交換</Text>
              </HStack>
              <HStack className="items-center space-x-2">
                <Text className="text-orange-500">⏳</Text>
                <Text className="text-gray-700">US6: 訂閱與付費</Text>
              </HStack>
            </VStack>
          </Card>
        </Box>

        {/* Info Card */}
        <Card className="p-4 bg-blue-50">
          <Text className="text-sm text-blue-800 font-medium mb-2">
            💡 提示
          </Text>
          <Text className="text-xs text-blue-700">
            • 點擊上方「好友」進入好友管理頁面{'\n'}
            • 點擊「聊天」查看所有對話{'\n'}
            • 使用底部導航切換到「我的卡冊」、「附近」或「個人檔案」
          </Text>
        </Card>
      </Box>
    </ScrollView>
  );
}
