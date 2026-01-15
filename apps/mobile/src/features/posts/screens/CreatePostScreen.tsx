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

import React from 'react';
import { ScrollView, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
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
  Select,
  SelectTrigger,
  SelectInput,
  SelectIcon,
  SelectPortal,
  SelectBackdrop,
  SelectContent,
  SelectDragIndicatorWrapper,
  SelectDragIndicator,
  SelectItem,
} from '@/src/shared/ui/components';
import { ChevronDownIcon } from '@/src/shared/ui/components';
import { useCreatePost, useCities } from '@/src/features/posts/hooks';
import { createPostFormSchema, type CreatePostFormData } from '@/src/shared/forms';
import type { CreatePostRequest } from '@/src/features/posts/types';

export function CreatePostScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ city_code?: string }>();
  
  // M706: 使用 useCities hook 取得城市列表
  const { data: cities, isLoading: citiesLoading } = useCities();
  
  const createPostMutation = useCreatePost();

  // React Hook Form setup with Zod validation
  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<CreatePostFormData>({
    resolver: zodResolver(createPostFormSchema),
    mode: 'onChange',
    defaultValues: {
      cityCode: params.city_code || 'TPE',
      title: '',
      content: '',
      idol: '',
      idolGroup: '',
    },
  });

  // Watch form values for character count display
  const title = watch('title');
  const cityCode = watch('cityCode');

  const onSubmit = async (data: CreatePostFormData) => {
    // 建立貼文資料
    const postData: CreatePostRequest = {
      city_code: data.cityCode,
      title: data.title.trim(),
      content: data.content.trim(),
      idol: data.idol?.trim() || undefined,
      idol_group: data.idolGroup?.trim() || undefined,
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

        {/* M706: 城市下拉選單 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            城市 <Text className="text-red-500">*</Text>
          </Text>
          {citiesLoading ? (
            <Box className="flex-row items-center p-3 bg-gray-100 rounded-lg">
              <Spinner size="small" />
              <Text className="text-sm text-gray-600 ml-2">載入城市列表...</Text>
            </Box>
          ) : (
            <Controller
              control={control}
              name="cityCode"
              render={({ field: { onChange, value } }) => (
                <Select selectedValue={value} onValueChange={onChange}>
                  <SelectTrigger variant="outline" size="md">
                    <SelectInput 
                      placeholder="選擇城市"
                      value={cities?.find(c => c.code === value)?.name_zh || '選擇城市'}
                    />
                    <SelectIcon className="mr-3">
                      <ChevronDownIcon />
                    </SelectIcon>
                  </SelectTrigger>
                  <SelectPortal>
                    <SelectBackdrop />
                    <SelectContent>
                      <SelectDragIndicatorWrapper>
                        <SelectDragIndicator />
                      </SelectDragIndicatorWrapper>
                      {cities?.map((city) => (
                        <SelectItem
                          key={city.code}
                          label={`${city.name_zh} (${city.code})`}
                          value={city.code}
                        />
                      ))}
                    </SelectContent>
                  </SelectPortal>
                </Select>
              )}
            />
          )}
          {errors.cityCode && (
            <Text className="text-xs text-red-500 mt-1">
              {errors.cityCode.message}
            </Text>
          )}
          <Text className="text-xs text-gray-500 mt-1">
            貼文將發布至選定城市的看板
          </Text>
        </Box>

        {/* 標題輸入 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            標題 <Text className="text-red-500">*</Text>
          </Text>
          <Controller
            control={control}
            name="title"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input variant="outline" size="md">
                <InputField
                  placeholder="例如：徵求 BTS Jungkook 小卡"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  maxLength={120}
                />
              </Input>
            )}
          />
          {errors.title && (
            <Text className="text-xs text-red-500 mt-1">
              {errors.title.message}
            </Text>
          )}
          <Text className="text-xs text-gray-500 mt-1">
            {title?.length || 0} / 120
          </Text>
        </Box>

        {/* 內容輸入 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            內容 <Text className="text-red-500">*</Text>
          </Text>
          <Controller
            control={control}
            name="content"
            render={({ field: { onChange, onBlur, value } }) => (
              <Textarea size="md" className="min-h-[150px]">
                <TextareaInput
                  placeholder="詳細描述你想交換的小卡..."
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  multiline
                />
              </Textarea>
            )}
          />
          {errors.content && (
            <Text className="text-xs text-red-500 mt-1">
              {errors.content.message}
            </Text>
          )}
          <Text className="text-xs text-gray-500 mt-1">
            請勿在內容中包含精確地址或聯絡方式
          </Text>
        </Box>

        {/* 偶像名稱 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            偶像名稱 (選填)
          </Text>
          <Controller
            control={control}
            name="idol"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input variant="outline" size="md">
                <InputField
                  placeholder="例如：Jungkook"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                />
              </Input>
            )}
          />
        </Box>

        {/* 團體名稱 */}
        <Box className="mb-4">
          <Text className="text-sm font-bold text-gray-900 mb-2">
            團體名稱 (選填)
          </Text>
          <Controller
            control={control}
            name="idolGroup"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input variant="outline" size="md">
                <InputField
                  placeholder="例如：BTS"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                />
              </Input>
            )}
          />
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
          onPress={handleSubmit(onSubmit)}
          disabled={!isValid || createPostMutation.isPending}
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
          disabled={createPostMutation.isPending}
        >
          <ButtonText>取消</ButtonText>
        </Button>
      </ScrollView>
    </Box>
  );
}
