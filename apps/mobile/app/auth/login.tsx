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
    <Box className="flex-1 items-center justify-center bg-white p-6">
      {/* Logo/Title Section */}
      <Box className="items-center mb-12">
        <Heading size="2xl" className="font-black text-[rgb(169,142,216)] tracking-tight">
          KCardSwap
        </Heading>
        <Text size="xs" className="text-[rgb(165,162,159)] mt-1 uppercase tracking-widest font-bold">
          Find Your Bias
        </Text>
      </Box>

      {/* Google Login Button */}
      <Box className="w-full max-w-sm space-y-4">
        <Button
          onPress={handleGoogleLogin}
          isDisabled={isLoading}
          className="w-full h-16 bg-white border border-[rgb(240,237,234)] rounded-2xl shadow-sm"
        >
          {isLoading ? (
            <Spinner color="#A98ED8" />
          ) : (
            <Box className="flex-row items-center">
              <Text size="xl" className="mr-4 font-bold">
                G
              </Text>
              <ButtonText className="font-bold text-[rgb(133,130,127)]">
                使用 Google 帳號登入
              </ButtonText>
            </Box>
          )}
        </Button>

        {/* Terms Text */}
        <Text size="xs" className="text-[rgb(165,162,159)] text-center px-4 leading-relaxed">
          登入即表示您同意本平台的服務條款與隱私協議。
        </Text>
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Text size="sm" className="mt-6 text-[rgb(133,130,127)] font-medium">
          正在連接 Google 帳號...
        </Text>
      )}
    </Box>
  );
}
