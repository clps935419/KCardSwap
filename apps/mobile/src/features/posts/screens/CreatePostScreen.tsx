/**
 * M702: 建立貼文頁
 * Create Post Screen
 * 
 * 功能：
 * - 建立新的城市看板貼文
 * - 輸入標題、內容、偶像、團體
 * - 設定到期時間
 * - 限制檢查 (免費用戶 2則/天)
 * 
 * 使用 Gluestack UI 元件
 */

import React, { useState } from 'react';
import { ScrollView, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import {
  Box,
  Text,
  Button,
  ButtonText,
  Input,
  InputField,
  Spinner,
  Textarea,
  TextareaInput,
} from '@/src/shared/ui/components';
import { useCreatePost } from '@/src/features/posts/hooks/usePosts';
import type { CreatePostRequest } from '@/src/features/posts/types';

export function CreatePostScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ city_code?: string }>();
  
  const [cityCode] = useState<string>(params.city_code || 'TPE');
  const [title, setTitle] = useState<string>('');
  const [content, setContent] = useState<string>('');
  const [idol, setIdol] = useState<string>('');
  const [idolGroup, setIdolGroup] = useState<string>('');

  const createPostMutation = useCreatePost();

  const handleSubmit = async () => {
    // 驗證輸入
    if (!title.trim()) {
      Alert.alert('錯誤', '請輸入標題');
      return;
    }

    if (!content.trim()) {
      Alert.alert('錯誤', '請輸入內容');
      return;
    }

    if (title.length > 120) {
      Alert.alert('錯誤', '標題不可超過 120 字');
      return;
    }

    // 建立貼文資料
    const postData: CreatePostRequest = {
      city_code: cityCode,
      title: title.trim(),
      content: content.trim(),
      idol: idol.trim() || undefined,
      idol_group: idolGroup.trim() || undefined,
      // expires_at 使用預設值 (後端設定為 14 天)
    };

    try {
      await createPostMutation.mutateAsync(postData);
      
      Alert.alert('成功', '貼文已發布', [
        {
          text: '確定',
          onPress: () => {
            router.back();
          },
        },
      ]);
    } catch (error: any) {
      let errorMessage = '請稍後再試';
      
      if (error.response?.status === 422) {
        errorMessage = '已達每日發文限制 (免費用戶: 2則/天)';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Alert.alert('發布失敗', errorMessage);
    }
  };

  const isFormValid = title.trim().length > 0 && content.trim().length > 0;

  return (
    <Box className="flex-1 bg-gray-50">
      <ScrollView className="flex-1 px-4 py-6">
        {/* 說明文字 */}
        <Box className="mb-6 p-4 bg-blue-50 rounded-lg">
          <Text className="text-sm text-blue-900 font-bold mb-1">
            提示
          </Text>
          <Text className="text-xs text-blue-700">
            發布交換貼文至城市看板，吸引同城玩家互相交換。
          </Text>
          <Text className="text-xs text-blue-700 mt-1">
            免費用戶每日限制: 2則貼文
          </Text>
        </Box>

        {/* 標題輸入 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            標題 <Text className="text-red-500">*</Text>
          </Text>
          <Input variant="outline" size="md">
            <InputField
              placeholder="例如：徵求 BTS Jungkook 小卡"
              value={title}
              onChangeText={setTitle}
              maxLength={120}
            />
          </Input>
          <Text className="text-xs text-gray-500 mt-1">
            {title.length} / 120
          </Text>
        </Box>

        {/* 內容輸入 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            內容 <Text className="text-red-500">*</Text>
          </Text>
          <Textarea size="md" className="min-h-[150px]">
            <TextareaInput
              placeholder="詳細描述你想交換的小卡..."
              value={content}
              onChangeText={setContent}
              multiline
            />
          </Textarea>
          <Text className="text-xs text-gray-500 mt-1">
            請勿在內容中包含精確地址或聯絡方式
          </Text>
        </Box>

        {/* 偶像名稱 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            偶像名稱 (選填)
          </Text>
          <Input variant="outline" size="md">
            <InputField
              placeholder="例如：Jungkook"
              value={idol}
              onChangeText={setIdol}
            />
          </Input>
        </Box>

        {/* 團體名稱 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            團體名稱 (選填)
          </Text>
          <Input variant="outline" size="md">
            <InputField
              placeholder="例如：BTS"
              value={idolGroup}
              onChangeText={setIdolGroup}
            />
          </Input>
        </Box>

        {/* 到期說明 */}
        <Box className="mb-6 p-3 bg-gray-100 rounded-lg">
          <Text className="text-xs text-gray-700">
            📅 貼文將在 14 天後自動到期
          </Text>
        </Box>

        {/* 提交按鈕 */}
        <Button
          size="lg"
          variant="solid"
          action="primary"
          className="w-full"
          onPress={handleSubmit}
          isDisabled={!isFormValid || createPostMutation.isPending}
        >
          {createPostMutation.isPending ? (
            <Spinner color="white" />
          ) : (
            <ButtonText>發布貼文</ButtonText>
          )}
        </Button>

        {/* 取消按鈕 */}
        <Button
          size="lg"
          variant="outline"
          action="secondary"
          className="w-full mt-3"
          onPress={() => router.back()}
          isDisabled={createPostMutation.isPending}
        >
          <ButtonText>取消</ButtonText>
        </Button>
      </ScrollView>
    </Box>
  );
}
