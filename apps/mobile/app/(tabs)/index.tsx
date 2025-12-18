import { View, Text } from 'react-native';
import { useAuthStore } from '../../src/shared/state/authStore';

export default function HomeScreen() {
  const { user } = useAuthStore();

  return (
    <View className="flex-1 items-center justify-center bg-white p-4">
      <Text className="text-2xl font-bold mb-4 text-gray-800">Welcome to KCardSwap!</Text>
      {user && (
        <Text className="text-base text-gray-600 mb-2">Hello, {user.nickname || user.email}</Text>
      )}
      <Text className="text-sm text-gray-500 text-center mt-4">
        Phase 1M Mobile Setup Complete ✅{'\n\n'}
        Features will be implemented in User Story phases:{'\n'}• US1: Google Login & Profile{'\n'}•
        US2: Card Upload{'\n'}• US3: Nearby Search{'\n'}• US4: Friends & Chat{'\n'}• US5: Trading
        {'\n'}• US6: Subscription
      </Text>
    </View>
  );
}
