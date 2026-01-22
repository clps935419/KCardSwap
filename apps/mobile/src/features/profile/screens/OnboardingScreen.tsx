/**
 * Onboarding Screen
 * 新用戶引導畫面 - 選擇偶像團體偏好
 * 
 * 對應 UI 原型中的 Onboarding (Bias Selection) 流程
 */

import React, { useState } from 'react';
import { ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import {
  Box,
  Text,
  Pressable,
  Button,
  ButtonText,
  Heading,
  Spinner,
} from '@/src/shared/ui/components';
import { useIdolGroups, useUpdateProfile } from '@/src/features/profile/hooks';

export function OnboardingScreen() {
  const router = useRouter();
  const [selectedGroups, setSelectedGroups] = useState<string[]>([]);
  const updateProfile = useUpdateProfile();
  const { data: idolGroups, isLoading, error } = useIdolGroups();

  const toggleGroup = (groupId: string) => {
    setSelectedGroups((prev) =>
      prev.includes(groupId)
        ? prev.filter((id) => id !== groupId)
        : [...prev, groupId]
    );
  };

  const handleComplete = async () => {
    if (selectedGroups.length === 0) {
      Alert.alert('提示', '請至少選擇一個偶像團體');
      return;
    }

    try {
      // 將選擇的團體儲存到 Profile preferences
      await updateProfile.mutateAsync({
        preferences: {
          favorite_idol_groups: selectedGroups,
          onboarding_completed: true,
        },
      });

      // 導航到主應用
      router.replace('/(tabs)');
    } catch (error) {
      Alert.alert('錯誤', '儲存失敗，請稍後再試');
      console.error('Onboarding save failed:', error);
    }
  };

  return (
    <ScrollView className="flex-1 bg-white">
      <Box className="p-6 pt-12">
        {/* Header */}
        <Box className="flex-row items-center mb-8">
          <Box className="w-12 h-12 bg-indigo-100 rounded-full items-center justify-center mr-3">
            <Text className="text-2xl">👤</Text>
          </Box>
          <Box className="flex-1">
            <Text className="text-xs text-gray-500 font-bold">你好！</Text>
            <Heading size="lg" className="text-gray-900">
              最後一步：選擇你的本命
            </Heading>
          </Box>
        </Box>

        {/* Description */}
        <Text className="text-sm text-gray-600 mb-6">
          選擇你喜歡的偶像團體，我們會為你推薦相關的小卡交換資訊
        </Text>

        {/* Loading State */}
        {isLoading && (
          <Box className="items-center justify-center py-12">
            <Spinner size="large" />
            <Text className="text-sm text-gray-500 mt-4">載入偶像團體...</Text>
          </Box>
        )}

        {/* Error State */}
        {error && (
          <Box className="items-center justify-center py-12">
            <Text className="text-sm text-red-500 mb-4">載入失敗，請稍後再試</Text>
            <Button size="sm" onPress={() => router.replace('/(tabs)')}>
              <ButtonText>稍後再說</ButtonText>
            </Button>
          </Box>
        )}

        {/* Idol Groups Grid */}
        {!isLoading && !error && (
          <>
            <Box className="flex-row flex-wrap gap-3 mb-8">
              {idolGroups.map((group) => {
                const isSelected = selectedGroups.includes(group.id);
                return (
                  <Pressable
                    key={group.id}
                    onPress={() => toggleGroup(group.id)}
                    className={`w-[48%] p-4 rounded-2xl border-2 items-center ${
                      isSelected
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 bg-white'
                    }`}
                  >
                    <Text className="text-3xl mb-2">{group.emoji}</Text>
                    <Text
                      className={`text-xs font-bold ${
                        isSelected ? 'text-indigo-700' : 'text-gray-900'
                      }`}
                    >
                      {group.name}
                    </Text>
                    {isSelected && (
                      <Box className="absolute top-2 right-2 w-5 h-5 bg-indigo-600 rounded-full items-center justify-center">
                        <Text className="text-white text-xs">✓</Text>
                      </Box>
                    )}
                  </Pressable>
                );
              })}
            </Box>

            {/* Selected Count */}
            <Text className="text-sm text-gray-500 text-center mb-4">
              已選擇 {selectedGroups.length} 個團體
            </Text>

            {/* Complete Button */}
            <Button
              size="lg"
              className="w-full bg-gray-900"
              onPress={handleComplete}
              isDisabled={updateProfile.isPending}
            >
              {updateProfile.isPending ? (
                <Spinner color="white" />
              ) : (
                <ButtonText className="text-white font-bold">開始探索小卡</ButtonText>
              )}
            </Button>

            {/* Skip Option */}
            <Pressable onPress={() => router.replace('/(tabs)')} className="mt-4">
              <Text className="text-sm text-gray-500 text-center">稍後再說</Text>
            </Pressable>
          </>
        )}
      </Box>
    </ScrollView>
  );
}
