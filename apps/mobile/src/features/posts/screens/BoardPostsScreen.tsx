/**
 * M701: 城市看板列表
 * Board Posts Screen
 * 
 * 功能：
 * - 顯示指定城市的貼文列表
 * - 支援偶像/團體篩選
 * - 點擊貼文查看詳情
 * - 導航至建立貼文頁面
 * 
 * 使用 Gluestack UI 元件
 */

import React, { useState } from 'react';
import { FlatList, RefreshControl, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import {
  Box,
  Text,
  Pressable,
  Spinner,
  Button,
  ButtonText,
  Input,
  InputField,
} from '@/src/shared/ui/components';
import { useBoardPosts } from '@/src/features/posts/hooks/usePosts';
import type { Post } from '@/src/features/posts/types';

// 台灣城市列表
const CITIES = [
  { code: 'TPE', name: '台北市' },
  { code: 'TPH', name: '新北市' },
  { code: 'TAO', name: '桃園市' },
  { code: 'TXG', name: '台中市' },
  { code: 'TNN', name: '台南市' },
  { code: 'KHH', name: '高雄市' },
];

export function BoardPostsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ city_code?: string }>();
  
  const [selectedCity, setSelectedCity] = useState<string>(params.city_code || 'TPE');
  const [idolFilter, setIdolFilter] = useState<string>('');
  const [idolGroupFilter, setIdolGroupFilter] = useState<string>('');

  const {
    data: postsData,
    isLoading,
    error,
    refetch,
    isRefetching,
  } = useBoardPosts({
    city_code: selectedCity,
    idol: idolFilter || undefined,
    idol_group: idolGroupFilter || undefined,
  });

  const posts = postsData?.posts || [];

  const handlePostPress = (post: Post) => {
    router.push(`/posts/${post.id}`);
  };

  const handleCreatePost = () => {
    router.push(`/posts/create?city_code=${selectedCity}`);
  };

  const renderPostItem = ({ item: post }: { item: Post }) => {
    const isExpired = new Date(post.expires_at) < new Date();
    const isClosed = post.status === 'closed';

    return (
      <Pressable
        className="p-4 mb-3 bg-white rounded-lg shadow-sm border border-gray-200"
        onPress={() => handlePostPress(post)}
      >
        {/* 貼文標題 */}
        <Text className="text-lg font-bold text-gray-900 mb-2">{post.title}</Text>

        {/* 貼文內容預覽 */}
        <Text className="text-sm text-gray-700 mb-2" numberOfLines={3}>
          {post.content}
        </Text>

        {/* 偶像/團體標籤 */}
        <Box className="flex-row flex-wrap gap-2 mb-2">
          {post.idol && (
            <Box className="px-2 py-1 bg-blue-100 rounded">
              <Text className="text-xs text-blue-700">{post.idol}</Text>
            </Box>
          )}
          {post.idol_group && (
            <Box className="px-2 py-1 bg-purple-100 rounded">
              <Text className="text-xs text-purple-700">{post.idol_group}</Text>
            </Box>
          )}
        </Box>

        {/* 貼文狀態與到期時間 */}
        <Box className="flex-row justify-between items-center">
          <Text className="text-xs text-gray-500">
            到期: {new Date(post.expires_at).toLocaleDateString('zh-TW')}
          </Text>
          <Box
            className={`px-2 py-1 rounded ${
              isClosed || isExpired ? 'bg-gray-200' : 'bg-green-100'
            }`}
          >
            <Text
              className={`text-xs font-semibold ${
                isClosed || isExpired ? 'text-gray-600' : 'text-green-700'
              }`}
            >
              {isClosed ? '已關閉' : isExpired ? '已到期' : '開放中'}
            </Text>
          </Box>
        </Box>
      </Pressable>
    );
  };

  const renderHeader = () => (
    <Box className="px-4 pb-4">
      {/* 城市選擇 */}
      <Box className="mb-4">
        <Text className="text-sm font-bold text-gray-900 mb-2">選擇城市</Text>
        <Box className="flex-row flex-wrap gap-2">
          {CITIES.map((city) => (
            <Pressable
              key={city.code}
              className={`px-4 py-2 rounded-full ${
                selectedCity === city.code ? 'bg-blue-500' : 'bg-gray-200'
              }`}
              onPress={() => setSelectedCity(city.code)}
            >
              <Text
                className={`text-sm ${
                  selectedCity === city.code ? 'text-white font-bold' : 'text-gray-700'
                }`}
              >
                {city.name}
              </Text>
            </Pressable>
          ))}
        </Box>
      </Box>

      {/* 篩選器 */}
      <Box className="mb-4">
        <Text className="text-sm font-bold text-gray-900 mb-2">篩選</Text>
        <Box className="gap-2">
          <Input variant="outline" size="md">
            <InputField
              placeholder="偶像名稱"
              value={idolFilter}
              onChangeText={setIdolFilter}
            />
          </Input>
          <Input variant="outline" size="md">
            <InputField
              placeholder="團體名稱"
              value={idolGroupFilter}
              onChangeText={setIdolGroupFilter}
            />
          </Input>
        </Box>
      </Box>

      {/* 建立貼文按鈕 */}
      <Button
        size="lg"
        variant="solid"
        action="primary"
        className="w-full"
        onPress={handleCreatePost}
      >
        <ButtonText>建立新貼文</ButtonText>
      </Button>

      {/* 貼文數量 */}
      <Text className="text-sm text-gray-600 mt-4">
        共 {posts.length} 則貼文
      </Text>
    </Box>
  );

  const renderEmpty = () => (
    <Box className="items-center justify-center py-12 px-4">
      <Text className="text-lg text-gray-500 text-center mb-2">
        目前沒有貼文
      </Text>
      <Text className="text-sm text-gray-400 text-center">
        成為第一個在 {CITIES.find((c) => c.code === selectedCity)?.name} 發布貼文的人！
      </Text>
    </Box>
  );

  if (isLoading) {
    return (
      <Box className="flex-1 items-center justify-center bg-gray-50">
        <Spinner size="large" />
        <Text className="mt-4 text-gray-600">載入中...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className="flex-1 items-center justify-center bg-gray-50 px-4">
        <Text className="text-lg text-red-600 text-center mb-4">
          載入失敗
        </Text>
        <Text className="text-sm text-gray-600 text-center mb-4">
          {error instanceof Error ? error.message : '請稍後再試'}
        </Text>
        <Button onPress={() => refetch()}>
          <ButtonText>重試</ButtonText>
        </Button>
      </Box>
    );
  }

  return (
    <Box className="flex-1 bg-gray-50">
      <FlatList
        data={posts}
        renderItem={renderPostItem}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={{ paddingTop: 16, paddingBottom: 16 }}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
        }
      />
    </Box>
  );
}
