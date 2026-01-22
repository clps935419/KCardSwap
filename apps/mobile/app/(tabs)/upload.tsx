/**
 * Upload Tab
 * Shows upload options (matching UI prototype style)
 */
import { useState } from 'react';
import { useRouter } from 'expo-router';
import { Box, Text, Button, ButtonText, Pressable } from '@/src/shared/ui/components';

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
    <Box className="flex-1 bg-gray-50">
      {/* Semi-transparent overlay */}
      <Box className="flex-1 bg-black/20 justify-end">
        {/* Bottom sheet style container */}
        <Box className="bg-white rounded-t-[2rem] p-6 shadow-2xl">
          {/* Handle bar */}
          <Box className="w-12 h-1.5 bg-gray-200 rounded-full mx-auto mb-8" />
          
          <Text className="text-2xl font-black text-gray-900 text-center mb-2">
            上傳內容
          </Text>
          <Text className="text-sm text-gray-500 text-center mb-8">
            選擇要上傳的內容類型
          </Text>

          {/* Upload Card Option */}
          <Pressable
            onPress={handleUploadCard}
            className="mb-4 p-4 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 items-center"
          >
            <Text className="text-4xl mb-2">📷</Text>
            <Text className="text-sm font-bold text-gray-800">上傳小卡照片</Text>
            <Text className="text-xs text-gray-500 mt-1">分享你的收藏</Text>
          </Pressable>

          {/* Create Post Option */}
          <Pressable
            onPress={handleCreatePost}
            className="mb-4 p-4 bg-indigo-50 rounded-2xl border-2 border-indigo-100 items-center"
          >
            <Text className="text-4xl mb-2">📝</Text>
            <Text className="text-sm font-bold text-indigo-900">發布交換貼文</Text>
            <Text className="text-xs text-indigo-600 mt-1">尋找交換對象</Text>
          </Pressable>

          {/* Submit Button */}
          <Button
            size="lg"
            className="w-full bg-gray-900 mb-4"
            onPress={handleUploadCard}
          >
            <ButtonText className="text-white font-bold">開始上傳</ButtonText>
          </Button>

          {/* Cancel */}
          <Pressable onPress={() => router.back()}>
            <Text className="text-sm text-gray-500 text-center">取消</Text>
          </Pressable>
        </Box>
      </Box>
    </Box>
  );
}
