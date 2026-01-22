/**
 * M701: 城市看板列表
 * Board Posts Screen (Updated to match UI prototype)
 * 
 * 功能：
 * - 顯示指定城市的貼文列表
 * - 支援偶像/團體篩選
 * - 點擊貼文查看詳情
 * - 導航至建立貼文頁面
 * 
 * 使用 Gluestack UI 元件 + Indigo 主色調
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
  Heading,
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

    // Calculate relative time (simplified)
    const getRelativeTime = (dateString: string) => {
      const now = new Date();
      const created = new Date(dateString);
      const diffMs = now.getTime() - created.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 60) return `${diffMins}m`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h`;
      return `${Math.floor(diffHours / 24)}d`;
    };

    return (
      <Pressable
        className="p-4 mb-3 bg-white rounded-3xl shadow-sm border border-gray-100"
        onPress={() => handlePostPress(post)}
      >
        {/* Mock Image Placeholder - 原型中有圖片 */}
        <Box className="w-full h-32 bg-gray-100 rounded-2xl mb-3" />

        {/* 貼文資訊 */}
        <Box className="flex-row justify-between items-start">
          <Box className="flex-1 mr-3">
            <Text className="text-sm font-bold text-gray-800 mb-1">
              {post.title}
            </Text>
            <Text className="text-xs text-gray-400">
              • {getRelativeTime(post.created_at)}
            </Text>
          </Box>
          
          {/* 偶像團體標籤 */}
          {(post.idol_group || post.idol) && (
            <Box className="px-2 py-1 bg-indigo-50 rounded-full">
              <Text className="text-xs text-indigo-600 font-bold">
                #{post.idol_group || post.idol}
              </Text>
            </Box>
          )}
        </Box>
      </Pressable>
    );
  };

  const renderHeader = () => (
    <Box className="mb-4">
      {/* 頁面標題 */}
      <Box className="px-6 pt-4 pb-2">
        <Text className="text-xs text-gray-400 font-bold uppercase tracking-widest">
          Discover
        </Text>
        <Heading size="2xl" className="text-gray-900 font-black">
          城市看板
        </Heading>
      </Box>

      {/* 城市選擇 */}
      <Box className="px-6 py-3">
        <Box className="flex-row flex-wrap gap-2">
          {CITIES.map((city) => (
            <Pressable
              key={city.code}
              className={`px-4 py-2 rounded-full ${
                selectedCity === city.code 
                  ? 'bg-indigo-600' 
                  : 'bg-gray-100'
              }`}
              onPress={() => setSelectedCity(city.code)}
            >
              <Text
                className={`text-sm font-bold ${
                  selectedCity === city.code 
                    ? 'text-white' 
                    : 'text-gray-700'
                }`}
              >
                {city.name}
              </Text>
            </Pressable>
          ))}
        </Box>
      </Box>
    </Box>
  );

  const renderEmpty = () => (
    <Box className="items-center justify-center py-12 px-6">
      <Text className="text-4xl mb-4">📭</Text>
      <Text className="text-lg text-gray-500 text-center mb-2 font-bold">
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
        <Spinner size="large" color="#4F46E5" />
        <Text className="mt-4 text-gray-600">載入中...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className="flex-1 items-center justify-center bg-gray-50 px-6">
        <Text className="text-4xl mb-4">⚠️</Text>
        <Text className="text-lg text-red-600 text-center mb-2 font-bold">
          載入失敗
        </Text>
        <Text className="text-sm text-gray-600 text-center mb-4">
          {error instanceof Error ? error.message : '請稍後再試'}
        </Text>
        <Button 
          className="bg-indigo-600"
          onPress={() => refetch()}
        >
          <ButtonText className="text-white font-bold">重試</ButtonText>
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
        contentContainerStyle={{ paddingHorizontal: 24, paddingBottom: 16 }}
        refreshControl={
          <RefreshControl 
            refreshing={isRefetching} 
            onRefresh={refetch}
            tintColor="#4F46E5"
          />
        }
      />
    </Box>
  );
}
