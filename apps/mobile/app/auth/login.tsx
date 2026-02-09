import { Alert, Platform, Image } from 'react-native';
import { useState } from 'react';
import { router } from 'expo-router';
import { useAuthStore } from '@/src/shared/state/authStore';
import { googleLoginWithPKCE, isGoogleOAuthConfigured } from '@/src/shared/auth/googleOAuth';
import { isDevLoginEnabled } from '@/src/shared/config';
import { adminLoginApiV1AuthAdminLoginPost } from '@/src/shared/api/generated';
import { brandShadows } from '@/src/shared/styles/shadows';
import {
  Box,
  Text,
  Heading,
  Button,
  ButtonText,
  Spinner,
  Input,
  InputField,
} from '@/src/shared/ui/components';

export default function LoginScreen() {
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuthStore();

  const containerClass = isDevLoginEnabled
    ? 'flex-1 items-center justify-center bg-white p-6'
    : 'flex-1 items-center bg-white px-6 pt-10 pb-6';

  const logoSpacingClass = isDevLoginEnabled ? 'mb-8' : 'mb-4';

  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true);

      // Check if Google OAuth is configured
      if (!isGoogleOAuthConfigured()) {
        Alert.alert(
          '設定錯誤',
          'Google OAuth 尚未設定。請在 .env 檔案中設定 GOOGLE_CLIENT_ID。'
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
      
      let errorMessage = '使用 Google 帳號登入失敗，請再試一次。';
      
      if (error.message?.includes('cancelled')) {
        errorMessage = '登入已取消。';
      } else if (error.message?.includes('timeout')) {
        errorMessage = '連線逾時，請檢查網路連線後再試一次。';
      } else if (error.message?.includes('configuration')) {
        errorMessage = error.message;
      }

      Alert.alert('登入失敗', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDevLogin = async () => {
    if (!email || !password) {
      Alert.alert('錯誤', '請輸入帳號和密碼');
      return;
    }

    try {
      setIsLoading(true);
      console.log('Starting dev login...');

      // Call admin login API
      const response = await adminLoginApiV1AuthAdminLoginPost({
        body: { email, password },
      });

      // Response structure: { data: { data: TokenResponse } }
      const result = response.data?.data;
      
      if (!result) {
        throw new Error('登入回應無效');
      }

      console.log('Dev login successful, user:', result.user_id);

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
      console.error('Dev login error:', error);
      
      let errorMessage = '登入失敗，請檢查帳號密碼是否正確。';
      
      if (error.response?.status === 401) {
        errorMessage = '帳號或密碼錯誤';
      } else if (error.response?.status === 404) {
        errorMessage = '找不到此帳號';
      } else if (error.message) {
        errorMessage = error.message;
      }

      Alert.alert('登入失敗', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box className={containerClass}>
      {/* Logo/Title Section - 小卡Show! Branding */}
      <Box className={`items-center ${logoSpacingClass}`}>
        {/* Logo Image */}
        <Image
          source={require('@/assets/CardShow_Logo.png')}
          style={{ width: 64, height: 64, marginBottom: 12 }}
          resizeMode="contain"
        />
        
        <Heading size="xl" className="font-black text-pink-500 tracking-tight">
          小卡Show!
        </Heading>
        <Text size="xs" className="text-slate-500 mt-1 tracking-wide font-medium">
          尋找你的本命
        </Text>
      </Box>

      {/* Login Forms */}
      <Box className="w-full max-w-sm space-y-4">
        {/* Development Mode: Email/Password Login */}
        {isDevLoginEnabled && (
          <Box className={`space-y-4 mb-6 p-4 bg-slate-50 rounded-2xl border border-slate-200 ${brandShadows.devSection}`}>
            <Text size="xs" className="text-slate-500 font-bold uppercase tracking-wider text-center">
              開發者模式
            </Text>
            
            <Input variant="outline" size="md" className={`bg-white ${brandShadows.input}`}>
              <InputField
                placeholder="電子信箱"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                editable={!isLoading}
              />
            </Input>

            <Input variant="outline" size="md" className={`bg-white ${brandShadows.input}`}>
              <InputField
                placeholder="密碼"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                editable={!isLoading}
              />
            </Input>

            <Button
              onPress={handleDevLogin}
              isDisabled={isLoading}
              className={`w-full h-12 bg-slate-700 rounded-xl ${brandShadows.devButton}`}
            >
              {isLoading ? (
                <Spinner color="#ffffff" />
              ) : (
                <ButtonText className="font-bold text-white">
                  開發者登入
                </ButtonText>
              )}
            </Button>

            <Box className="w-full h-px bg-slate-200 my-4" />
          </Box>
        )}

        {/* Google Login Button */}
        <Button
          onPress={handleGoogleLogin}
          isDisabled={isLoading}
          className={`w-full h-12 bg-gradient-to-r from-pink-50 to-rose-50 border-2 border-pink-200 rounded-2xl ${brandShadows.googleButton}`}
        >
          {isLoading ? (
            <Spinner color="#EC4899" />
          ) : (
            <Box className="flex-row items-center justify-center">
              <Box className={`w-8 h-8 bg-white rounded-full items-center justify-center mr-3 ${brandShadows.googleIcon}`}>
                <Text size="lg" className="font-black text-pink-500">
                  G
                </Text>
              </Box>
              <ButtonText className="font-bold text-pink-600 text-sm">
                使用 Google 帳號登入
              </ButtonText>
            </Box>
          )}
        </Button>

        {/* Terms Text */}
        <Text size="xs" className="text-slate-400 text-center px-4 leading-relaxed">
          登入即表示您同意本平台的服務條款與隱私協議。
        </Text>
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Text size="sm" className="mt-6 text-slate-500 font-medium">
          正在連接帳號...
        </Text>
      )}
    </Box>
  );
}
