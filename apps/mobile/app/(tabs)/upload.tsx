/**
 * Upload Tab
 * Shows upload modal/screen for creating new card posts
 */
import { useState } from 'react';
import { useRouter } from 'expo-router';
import { Box, Text, Button, ButtonText } from '@/src/shared/ui/components';

export default function UploadScreen() {
  const router = useRouter();

  // Navigate to cards upload screen
  const handleUploadCard = () => {
    router.push('/cards/upload');
  };

  // Navigate to posts create screen
  const handleCreatePost = () => {
    router.push('/posts/create');
  };

  return (
    <Box className="flex-1 items-center justify-center p-6 bg-gray-50">
      <Box className="w-full max-w-sm">
        <Text className="text-2xl font-bold text-gray-900 text-center mb-2">
          上傳內容
        </Text>
        <Text className="text-sm text-gray-600 text-center mb-8">
          選擇要上傳的內容類型
        </Text>

        <Box className="gap-4">
          <Button
            size="lg"
            className="w-full bg-indigo-600"
            onPress={handleUploadCard}
          >
            <ButtonText className="text-white font-bold">📷 上傳小卡照片</ButtonText>
          </Button>

          <Button
            size="lg"
            variant="outline"
            className="w-full border-2 border-indigo-600"
            onPress={handleCreatePost}
          >
            <ButtonText className="text-indigo-600 font-bold">📝 發布交換貼文</ButtonText>
          </Button>

          <Button
            size="md"
            variant="link"
            className="w-full"
            onPress={() => router.back()}
          >
            <ButtonText className="text-gray-500">取消</ButtonText>
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
