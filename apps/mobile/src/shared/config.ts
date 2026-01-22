// Environment configuration
export const config = {
  apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1',
  googleClientId: process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID || '',
  googleRedirectUri: process.env.EXPO_PUBLIC_GOOGLE_REDIRECT_URI || 'kcardswap://',
  appScheme: process.env.EXPO_PUBLIC_APP_SCHEME || 'kcardswap',
  appName: process.env.EXPO_PUBLIC_APP_NAME || '小卡Show!',
  appVersion: process.env.EXPO_PUBLIC_APP_VERSION || '1.0.0',
  env: process.env.EXPO_PUBLIC_ENV || 'development',
  enableDevLogin: process.env.EXPO_PUBLIC_ENABLE_DEV_LOGIN === 'true',

  // API timeouts (in milliseconds)
  apiTimeout: 30000, // 30 seconds
  apiRetries: 3,
} as const;

export const isDevelopment = config.env === 'development';
export const isProduction = config.env === 'production';
export const isDevLoginEnabled = config.enableDevLogin;
