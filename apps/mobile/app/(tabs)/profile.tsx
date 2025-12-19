import { ScrollView, Alert } from 'react-native';
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/src/shared/state/authStore';
import {
  getMyProfile,
  updateMyProfile,
  validateNickname,
  validateBio,
  Profile,
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
} from '@/src/shared/ui/components';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Form fields
  const [nickname, setNickname] = useState('');
  const [bio, setBio] = useState('');
  const [nearbyVisible, setNearbyVisible] = useState(true);
  const [showOnline, setShowOnline] = useState(true);
  const [allowStrangerChat, setAllowStrangerChat] = useState(true);

  // Load profile on mount
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      const data = await getMyProfile();
      setProfile(data);
      
      // Initialize form fields
      setNickname(data.nickname || '');
      setBio(data.bio || '');
      setNearbyVisible(data.privacy_flags.nearby_visible);
      setShowOnline(data.privacy_flags.show_online);
      setAllowStrangerChat(data.privacy_flags.allow_stranger_chat);
    } catch (error: any) {
      console.error('Failed to load profile:', error);
      Alert.alert('Error', error.message || 'Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      // Validate inputs
      const nicknameError = validateNickname(nickname);
      if (nicknameError) {
        Alert.alert('Validation Error', nicknameError);
        return;
      }

      const bioError = validateBio(bio);
      if (bioError) {
        Alert.alert('Validation Error', bioError);
        return;
      }

      setIsSaving(true);

      // Update profile
      const updated = await updateMyProfile({
        nickname: nickname.trim(),
        bio: bio.trim() || undefined,
        privacy_flags: {
          nearby_visible: nearbyVisible,
          show_online: showOnline,
          allow_stranger_chat: allowStrangerChat,
        },
      });

      setProfile(updated);
      setIsEditing(false);
      Alert.alert('Success', 'Profile updated successfully!');
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      Alert.alert('Error', error.message || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset form to current profile values
    if (profile) {
      setNickname(profile.nickname || '');
      setBio(profile.bio || '');
      setNearbyVisible(profile.privacy_flags.nearby_visible);
      setShowOnline(profile.privacy_flags.show_online);
      setAllowStrangerChat(profile.privacy_flags.allow_stranger_chat);
    }
    setIsEditing(false);
  };

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await logout();
          },
        },
      ]
    );
  };

  if (isLoading) {
    return (
      <Box className="flex-1 bg-white items-center justify-center">
        <Spinner size="large" />
        <Text className="mt-4 text-gray-600">Loading profile...</Text>
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

        {/* Profile Form */}
        <Box className="mb-6">
          {/* Nickname */}
          <Box className="mb-4">
            <Text size="sm" className="font-semibold text-gray-700 mb-2">
              Nickname
            </Text>
            <Input isDisabled={!isEditing}>
              <InputField
                value={nickname}
                onChangeText={setNickname}
                placeholder="Enter your nickname"
                maxLength={50}
              />
            </Input>
            <Text size="xs" className="text-gray-500 mt-1">
              {nickname.length}/50 characters
            </Text>
          </Box>

          {/* Bio */}
          <Box className="mb-4">
            <Text size="sm" className="font-semibold text-gray-700 mb-2">
              Bio
            </Text>
            <Input isDisabled={!isEditing}>
              <InputField
                value={bio}
                onChangeText={setBio}
                placeholder="Tell us about yourself..."
                multiline
                numberOfLines={4}
                textAlignVertical="top"
                maxLength={500}
              />
            </Input>
            <Text size="xs" className="text-gray-500 mt-1">
              {bio.length}/500 characters
            </Text>
          </Box>

          {/* Privacy Settings */}
          <Box className="mb-4">
            <Text size="sm" className="font-semibold text-gray-700 mb-3">
              Privacy Settings
            </Text>

            <Box className="flex-row justify-between items-center mb-3">
              <Text size="md" className="text-gray-700">Visible in Nearby Search</Text>
              <Switch
                value={nearbyVisible}
                onValueChange={setNearbyVisible}
                isDisabled={!isEditing}
              />
            </Box>

            <Box className="flex-row justify-between items-center mb-3">
              <Text size="md" className="text-gray-700">Show Online Status</Text>
              <Switch
                value={showOnline}
                onValueChange={setShowOnline}
                isDisabled={!isEditing}
              />
            </Box>

            <Box className="flex-row justify-between items-center">
              <Text size="md" className="text-gray-700">Allow Stranger Chat</Text>
              <Switch
                value={allowStrangerChat}
                onValueChange={setAllowStrangerChat}
                isDisabled={!isEditing}
              />
            </Box>
          </Box>
        </Box>

        {/* Action Buttons */}
        {isEditing ? (
          <Box className="flex-row gap-3 mb-4">
            <Button
              onPress={handleCancel}
              isDisabled={isSaving}
              variant="outline"
              className="flex-1"
            >
              <ButtonText>Cancel</ButtonText>
            </Button>

            <Button
              onPress={handleSave}
              isDisabled={isSaving}
              variant="solid"
              className="flex-1 bg-blue-500"
            >
              {isSaving ? (
                <Spinner color="white" size="small" />
              ) : (
                <ButtonText>Save</ButtonText>
              )}
            </Button>
          </Box>
        ) : (
          <Button
            onPress={() => setIsEditing(true)}
            variant="solid"
            className="bg-blue-500 mb-4"
          >
            <ButtonText>Edit Profile</ButtonText>
          </Button>
        )}

        {/* Logout Button */}
        <Button
          onPress={handleLogout}
          variant="solid"
          className="bg-red-500"
        >
          <ButtonText>Logout</ButtonText>
        </Button>

        {/* Profile Info */}
        {profile && (
          <Box className="mt-6 p-4 bg-gray-50 rounded-lg">
            <Text size="xs" className="text-gray-500 mb-1">
              Profile ID: {profile.id.substring(0, 8)}...
            </Text>
            <Text size="xs" className="text-gray-500">
              Last updated: {new Date(profile.updated_at).toLocaleDateString()}
            </Text>
          </Box>
        )}
      </Box>
    </ScrollView>
  );
}
