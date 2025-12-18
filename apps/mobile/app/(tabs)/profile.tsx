import { View, Text, TouchableOpacity } from 'react-native';
import { useAuthStore } from '../../src/shared/state/authStore';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <View className="flex-1 bg-white p-4">
      <View className="items-center mt-8">
        <View className="w-24 h-24 rounded-full bg-gray-300 items-center justify-center mb-4">
          <Text className="text-3xl">👤</Text>
        </View>

        {user && (
          <>
            <Text className="text-xl font-bold text-gray-800">{user.nickname || 'User'}</Text>
            <Text className="text-sm text-gray-600 mt-1">{user.email}</Text>
          </>
        )}

        <TouchableOpacity
          onPress={handleLogout}
          className="mt-8 bg-red-500 px-6 py-3 rounded-lg active:bg-red-600"
        >
          <Text className="text-white font-semibold">Logout</Text>
        </TouchableOpacity>

        <Text className="text-xs text-gray-500 mt-8 text-center">
          Profile management will be implemented in US1
        </Text>
      </View>
    </View>
  );
}
