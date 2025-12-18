import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  Switch,
} from 'react-native';
import { useState, useEffect } from 'react';
import { useAuthStore } from '../../src/shared/state/authStore';
import {
  getMyProfile,
  updateMyProfile,
  validateNickname,
  validateBio,
  Profile,
} from '../../src/features/profile/api/profileApi';

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
        bio: bio.trim() || null,
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
      <View className="flex-1 bg-white items-center justify-center">
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text className="mt-4 text-gray-600">Loading profile...</Text>
      </View>
    );
  }

  return (
    <ScrollView className="flex-1 bg-white">
      <View className="p-4">
        {/* Header */}
        <View className="items-center mt-4 mb-6">
          <View className="w-24 h-24 rounded-full bg-gray-300 items-center justify-center mb-4">
            <Text className="text-3xl">
              {profile?.avatar_url ? '🖼️' : '👤'}
            </Text>
          </View>

          {user && (
            <Text className="text-sm text-gray-600">{user.email}</Text>
          )}
        </View>

        {/* Profile Form */}
        <View className="mb-6">
          {/* Nickname */}
          <View className="mb-4">
            <Text className="text-sm font-semibold text-gray-700 mb-2">
              Nickname
            </Text>
            <TextInput
              className="border border-gray-300 rounded-lg px-4 py-3 text-base"
              value={nickname}
              onChangeText={setNickname}
              placeholder="Enter your nickname"
              editable={isEditing}
              maxLength={50}
            />
            <Text className="text-xs text-gray-500 mt-1">
              {nickname.length}/50 characters
            </Text>
          </View>

          {/* Bio */}
          <View className="mb-4">
            <Text className="text-sm font-semibold text-gray-700 mb-2">
              Bio
            </Text>
            <TextInput
              className="border border-gray-300 rounded-lg px-4 py-3 text-base"
              value={bio}
              onChangeText={setBio}
              placeholder="Tell us about yourself..."
              editable={isEditing}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
              maxLength={500}
            />
            <Text className="text-xs text-gray-500 mt-1">
              {bio.length}/500 characters
            </Text>
          </View>

          {/* Privacy Settings */}
          <View className="mb-4">
            <Text className="text-sm font-semibold text-gray-700 mb-3">
              Privacy Settings
            </Text>

            <View className="flex-row justify-between items-center mb-3">
              <Text className="text-base text-gray-700">Visible in Nearby Search</Text>
              <Switch
                value={nearbyVisible}
                onValueChange={setNearbyVisible}
                disabled={!isEditing}
              />
            </View>

            <View className="flex-row justify-between items-center mb-3">
              <Text className="text-base text-gray-700">Show Online Status</Text>
              <Switch
                value={showOnline}
                onValueChange={setShowOnline}
                disabled={!isEditing}
              />
            </View>

            <View className="flex-row justify-between items-center">
              <Text className="text-base text-gray-700">Allow Stranger Chat</Text>
              <Switch
                value={allowStrangerChat}
                onValueChange={setAllowStrangerChat}
                disabled={!isEditing}
              />
            </View>
          </View>
        </View>

        {/* Action Buttons */}
        {isEditing ? (
          <View className="flex-row gap-3 mb-4">
            <TouchableOpacity
              onPress={handleCancel}
              disabled={isSaving}
              className="flex-1 bg-gray-500 px-6 py-3 rounded-lg active:bg-gray-600"
            >
              <Text className="text-white font-semibold text-center">Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleSave}
              disabled={isSaving}
              className="flex-1 bg-blue-500 px-6 py-3 rounded-lg active:bg-blue-600"
            >
              {isSaving ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text className="text-white font-semibold text-center">Save</Text>
              )}
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity
            onPress={() => setIsEditing(true)}
            className="bg-blue-500 px-6 py-3 rounded-lg active:bg-blue-600 mb-4"
          >
            <Text className="text-white font-semibold text-center">Edit Profile</Text>
          </TouchableOpacity>
        )}

        {/* Logout Button */}
        <TouchableOpacity
          onPress={handleLogout}
          className="bg-red-500 px-6 py-3 rounded-lg active:bg-red-600"
        >
          <Text className="text-white font-semibold text-center">Logout</Text>
        </TouchableOpacity>

        {/* Profile Info */}
        {profile && (
          <View className="mt-6 p-4 bg-gray-50 rounded-lg">
            <Text className="text-xs text-gray-500 mb-1">
              Profile ID: {profile.id.substring(0, 8)}...
            </Text>
            <Text className="text-xs text-gray-500">
              Last updated: {new Date(profile.updated_at).toLocaleDateString()}
            </Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
}
