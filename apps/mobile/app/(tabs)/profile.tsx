import { ScrollView, Alert } from 'react-native';
import { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@/src/shared/state/authStore';
import {
  getMyProfileOptions,
  getMyProfileQueryKey,
  updateMyProfileMutation,
  type Profile,
} from '@/src/features/profile/api/profileApi';
import {
  Box,
  Text,
  Heading,
  Button,
  ButtonText,
  Input,
  InputField,
  Spinner,
  Switch,
  Pressable,
} from '@/src/shared/ui/components';
import { useSubscriptionStatus } from '@/src/features/subscription';
import { profileFormSchema, type ProfileFormData } from '@/src/shared/forms';

export default function ProfileScreen() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { user, logout } = useAuthStore();
  
  // Use TanStack Query for fetching profile
  const { data: profileData, isLoading, error } = useQuery(getMyProfileOptions());
  const profile = profileData?.data;
  
  // Get subscription status
  const { subscription, isPremium } = useSubscriptionStatus();
  
  const [isEditing, setIsEditing] = useState(false);

  // React Hook Form setup with Zod validation
  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      nickname: '',
      bio: '',
      nearbyVisible: true,
      showOnline: true,
      allowStrangerChat: true,
    },
  });

  // Watch form values for character count display
  const nickname = watch('nickname');
  const bio = watch('bio');
  
  // Use TanStack Query mutation for updating profile
  const updateProfile = useMutation({
    ...updateMyProfileMutation(),
    onSuccess: () => {
      // Invalidate and refetch profile data
      queryClient.invalidateQueries({ queryKey: getMyProfileQueryKey() });
      setIsEditing(false);
      Alert.alert('成功', '個人資料已更新！');
    },
    onError: (error: any) => {
      console.error('Failed to update profile:', error);
      Alert.alert('錯誤', error.message || '更新個人資料失敗');
    },
  });

  // Initialize form fields when profile loads
  useEffect(() => {
    if (profile) {
      reset({
        nickname: profile.nickname || '',
        bio: profile.bio || '',
        nearbyVisible: profile.privacy_flags?.nearby_visible ?? true,
        showOnline: profile.privacy_flags?.show_online ?? true,
        allowStrangerChat: profile.privacy_flags?.allow_stranger_chat ?? true,
      });
    }
  }, [profile, reset]);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      const mutation = updateMyProfileMutation();
      if (mutation.mutationFn) {
        // Update profile using mutation
        await mutation.mutationFn({
          body: {
            nickname: data.nickname.trim(),
            bio: data.bio?.trim() || undefined,
            privacy_flags: {
              nearby_visible: data.nearbyVisible,
              show_online: data.showOnline,
              allow_stranger_chat: data.allowStrangerChat,
            },
          },
        });
        // Invalidate and refetch profile data
        queryClient.invalidateQueries({ queryKey: getMyProfileQueryKey() });
        setIsEditing(false);
        Alert.alert('成功', '個人資料已更新！');
      }
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      Alert.alert('錯誤', error?.message || '更新個人資料失敗');
    }
  };

  const handleCancel = () => {
    // Reset form to current profile values
    if (profile) {
      reset({
        nickname: profile.nickname || '',
        bio: profile.bio || '',
        nearbyVisible: profile.privacy_flags?.nearby_visible ?? true,
        showOnline: profile.privacy_flags?.show_online ?? true,
        allowStrangerChat: profile.privacy_flags?.allow_stranger_chat ?? true,
      });
    }
    setIsEditing(false);
  };

  const handleLogout = async () => {
    Alert.alert(
      '登出',
      '確定要登出嗎？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '登出',
          style: 'destructive',
          onPress: async () => {
            await logout();
          },
        },
      ]
    );
  };

  // Show loading spinner
  if (isLoading) {
    return (
      <Box className="flex-1 bg-white items-center justify-center">
        <Spinner size="large" />
        <Text className="mt-4 text-gray-600">載入個人資料中...</Text>
      </Box>
    );
  }

  // Show error message
  if (error) {
    return (
      <Box className="flex-1 bg-white items-center justify-center p-4">
        <Text className="text-red-500 text-center mb-4">
          載入個人資料失敗
        </Text>
        <Button onPress={() => queryClient.invalidateQueries({ queryKey: getMyProfileQueryKey() })}>
          <ButtonText>重試</ButtonText>
        </Button>
      </Box>
    );
  }

  return (
    <ScrollView className="flex-1 bg-white">
      <Box className="p-4">
        {/* Header */}
        <Box className="items-center mt-4 mb-6">
          <Box className="w-24 h-24 rounded-full bg-gray-300 items-center justify-center mb-4">
            <Text size="3xl">
              {profile?.avatar_url ? '🖼️' : '👤'}
            </Text>
          </Box>

          {user && (
            <Text size="sm" className="text-gray-600">{user.email}</Text>
          )}
        </Box>

        {/* Subscription Card */}
        <Pressable
          onPress={() => router.push('/subscription')}
          className="mb-6 p-4 rounded-lg border-2"
          style={{
            borderColor: isPremium ? '#3b82f6' : '#d1d5db',
            backgroundColor: isPremium ? '#eff6ff' : '#f9fafb',
          }}
        >
          <Box className="flex-row justify-between items-center">
            <Box className="flex-1">
              <Text className="text-lg font-bold mb-1">
                {isPremium ? '✨ 付費方案' : '📦 免費方案'}
              </Text>
              {isPremium && subscription?.expires_at && (
                <Text size="sm" className="text-gray-600">
                  到期日: {new Date(subscription.expires_at).toLocaleDateString('zh-TW')}
                </Text>
              )}
              {!isPremium && (
                <Text size="sm" className="text-gray-600">
                  升級享受無限上傳與搜尋
                </Text>
              )}
            </Box>
            <Box className="ml-4">
              <Text size="lg">→</Text>
            </Box>
          </Box>
        </Pressable>

        {/* Profile Form */}
        <Box className="mb-6">
          {/* Nickname */}
          <Box className="mb-4">
            <Text size="sm" className="font-semibold text-gray-700 mb-2">
              暱稱
            </Text>
            <Controller
              control={control}
              name="nickname"
              render={({ field: { onChange, onBlur, value } }) => (
                <Input isDisabled={!isEditing}>
                  <InputField
                    value={value}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    placeholder="請輸入您的暱稱"
                    maxLength={50}
                  />
                </Input>
              )}
            />
            {errors.nickname && (
              <Text size="xs" className="text-red-500 mt-1">
                {errors.nickname.message}
              </Text>
            )}
            <Text size="xs" className="text-gray-500 mt-1">
              {(nickname?.length || 0)}/50 字元
            </Text>
          </Box>

          {/* Bio */}
          <Box className="mb-4">
            <Text size="sm" className="font-semibold text-gray-700 mb-2">
              個人簡介
            </Text>
            <Controller
              control={control}
              name="bio"
              render={({ field: { onChange, onBlur, value } }) => (
                <Input isDisabled={!isEditing}>
                  <InputField
                    value={value || ''}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    placeholder="介紹一下自己..."
                    multiline
                    numberOfLines={4}
                    textAlignVertical="top"
                    maxLength={500}
                  />
                </Input>
              )}
            />
            {errors.bio && (
              <Text size="xs" className="text-red-500 mt-1">
                {errors.bio.message}
              </Text>
            )}
            <Text size="xs" className="text-gray-500 mt-1">
              {(bio?.length || 0)}/500 字元
            </Text>
          </Box>

          {/* Privacy Settings */}
          <Box className="mb-4">
            <Text size="sm" className="font-semibold text-gray-700 mb-3">
              隱私設定
            </Text>

            <Box className="flex-row justify-between items-center mb-3">
              <Text size="md" className="text-gray-700">在附近搜尋中顯示</Text>
              <Controller
                control={control}
                name="nearbyVisible"
                render={({ field: { onChange, value } }) => (
                  <Switch
                    value={value}
                    onValueChange={onChange}
                    disabled={!isEditing}
                  />
                )}
              />
            </Box>

            <Box className="flex-row justify-between items-center mb-3">
              <Text size="md" className="text-gray-700">顯示在線狀態</Text>
              <Controller
                control={control}
                name="showOnline"
                render={({ field: { onChange, value } }) => (
                  <Switch
                    value={value}
                    onValueChange={onChange}
                    disabled={!isEditing}
                  />
                )}
              />
            </Box>

            <Box className="flex-row justify-between items-center">
              <Text size="md" className="text-gray-700">允許陌生人聊天</Text>
              <Controller
                control={control}
                name="allowStrangerChat"
                render={({ field: { onChange, value } }) => (
                  <Switch
                    value={value}
                    onValueChange={onChange}
                    disabled={!isEditing}
                  />
                )}
              />
            </Box>
          </Box>
        </Box>

        {/* Action Buttons */}
        {isEditing ? (
          <Box className="flex-row gap-3 mb-4">
            <Button
              onPress={handleCancel}
              variant="outline"
              className="flex-1"
            >
              <ButtonText>取消</ButtonText>
            </Button>

            <Button
              onPress={handleSubmit(onSubmit)}
              isDisabled={!isDirty}
              variant="solid"
              className="flex-1 bg-blue-500"
            >
              <ButtonText>儲存</ButtonText>
            </Button>
          </Box>
        ) : (
          <Button
            onPress={() => setIsEditing(true)}
            variant="solid"
            className="bg-blue-500 mb-4"
          >
            <ButtonText>編輯個人資料</ButtonText>
          </Button>
        )}

        {/* Logout Button */}
        <Button
          onPress={handleLogout}
          variant="solid"
          className="bg-red-500"
        >
          <ButtonText>登出</ButtonText>
        </Button>

        {/* Profile Info */}
        {profile && (
          <Box className="mt-6 p-4 bg-gray-50 rounded-lg">
            <Text size="xs" className="text-gray-500 mb-1">
              個人資料 ID: {profile.id.substring(0, 8)}...
            </Text>
            <Text size="xs" className="text-gray-500">
              最後更新: {new Date(profile.updated_at).toLocaleDateString('zh-TW')}
            </Text>
          </Box>
        )}
      </Box>
    </ScrollView>
  );
}
