import { Alert } from 'react-native';
import { useState } from 'react';
import { router } from 'expo-router';
import { useAuthStore } from '@/src/shared/state/authStore';
import { googleLoginWithPKCE, isGoogleOAuthConfigured } from '@/src/shared/auth/googleOAuth';
import {
  Box,
  Text,
  Heading,
  Button,
  ButtonText,
  Spinner,
} from '@/src/shared/ui/components';

export default function LoginScreen() {
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();

  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true);

      // Check if Google OAuth is configured
      if (!isGoogleOAuthConfigured()) {
        Alert.alert(
          'Configuration Error',
          'Google OAuth is not configured. Please set GOOGLE_CLIENT_ID in your .env file.'
        );
        return;
      }

      console.log('Starting Google login with PKCE...');

      // Start Google OAuth flow with PKCE
      const result = await googleLoginWithPKCE();

      console.log('Login successful, user:', result.email);

      // Calculate token expiration time
      const expiresAt = Date.now() + result.expires_in * 1000;

      // Save tokens and user data to auth store
      await login(
        {
          accessToken: result.access_token,
          refreshToken: result.refresh_token,
          expiresAt,
        },
        {
          id: result.user_id,
          email: result.email,
        }
      );

      // Navigate to main app
      router.replace('/(tabs)');
    } catch (error: any) {
      console.error('Google login error:', error);
      
      let errorMessage = 'Failed to sign in with Google. Please try again.';
      
      if (error.message?.includes('cancelled')) {
        errorMessage = 'Login was cancelled.';
      } else if (error.message?.includes('timeout')) {
        errorMessage = 'Connection timeout. Please check your network and try again.';
      } else if (error.message?.includes('configuration')) {
        errorMessage = error.message;
      }

      Alert.alert('Login Failed', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box className="flex-1 items-center justify-center bg-white p-4">
      <Heading size="3xl" className="mb-2 text-gray-800">
        Welcome to KCardSwap
      </Heading>
      <Text size="md" className="mb-8 text-gray-600 text-center">
        Sign in to start trading your cards
      </Text>

      <Button
        onPress={handleGoogleLogin}
        isDisabled={isLoading}
        size="lg"
        className={`px-8 py-4 rounded-lg shadow-md ${
          isLoading ? 'bg-blue-300' : 'bg-blue-500'
        }`}
      >
        {isLoading ? (
          <Spinner color="white" />
        ) : (
          <ButtonText size="lg" className="font-semibold">
            Sign in with Google
          </ButtonText>
        )}
      </Button>

      {isLoading && (
        <Text size="sm" className="mt-4 text-gray-500">
          Redirecting to Google...
        </Text>
      )}

      <Text size="sm" className="mt-8 text-gray-500 text-center">
        Phase 3 (US1): Google OAuth with PKCE{'\n'}
        Secure mobile authentication
      </Text>
    </Box>
  );
}
