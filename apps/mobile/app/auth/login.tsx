import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';

export default function LoginScreen() {
  const router = useRouter();

  const handleGoogleLogin = async () => {
    // TODO: Implement Google OAuth with PKCE flow
    // This will be implemented in US1 Mobile tasks (M101)
    console.log('Google login - to be implemented');
  };

  return (
    <View className="flex-1 items-center justify-center bg-white p-4">
      <Text className="text-3xl font-bold mb-2 text-gray-800">Welcome to KCardSwap</Text>
      <Text className="text-base mb-8 text-gray-600 text-center">
        Sign in to start trading your cards
      </Text>

      <TouchableOpacity
        onPress={handleGoogleLogin}
        className="bg-blue-500 px-8 py-4 rounded-lg shadow-md active:bg-blue-600"
      >
        <Text className="text-white text-lg font-semibold">Sign in with Google</Text>
      </TouchableOpacity>

      <Text className="mt-8 text-sm text-gray-500 text-center">
        Phase 1M: Mobile Setup Complete{'\n'}
        Google OAuth will be implemented in US1
      </Text>
    </View>
  );
}
