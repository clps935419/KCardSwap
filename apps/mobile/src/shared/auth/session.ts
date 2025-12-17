import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user_data';

export interface TokenData {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface UserData {
  id: string;
  email: string;
  nickname?: string;
  avatarUrl?: string;
}

/**
 * Save authentication tokens to secure storage
 */
export async function saveTokens(tokens: TokenData): Promise<void> {
  try {
    await SecureStore.setItemAsync(TOKEN_KEY, tokens.accessToken);
    await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokens.refreshToken);
    await SecureStore.setItemAsync('token_expires_at', tokens.expiresAt.toString());
  } catch (error) {
    console.error('Failed to save tokens:', error);
    throw error;
  }
}

/**
 * Get access token from secure storage
 */
export async function getAccessToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch (error) {
    console.error('Failed to get access token:', error);
    return null;
  }
}

/**
 * Get refresh token from secure storage
 */
export async function getRefreshToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
  } catch (error) {
    console.error('Failed to get refresh token:', error);
    return null;
  }
}

/**
 * Get token expiration time
 */
export async function getTokenExpiresAt(): Promise<number | null> {
  try {
    const expiresAt = await SecureStore.getItemAsync('token_expires_at');
    return expiresAt ? parseInt(expiresAt, 10) : null;
  } catch (error) {
    console.error('Failed to get token expiration:', error);
    return null;
  }
}

/**
 * Check if access token is expired or about to expire (within 5 minutes)
 */
export async function isTokenExpired(): Promise<boolean> {
  const expiresAt = await getTokenExpiresAt();
  if (!expiresAt) return true;

  const now = Date.now();
  const fiveMinutes = 5 * 60 * 1000;
  return now >= expiresAt - fiveMinutes;
}

/**
 * Save user data to secure storage
 */
export async function saveUserData(user: UserData): Promise<void> {
  try {
    await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
  } catch (error) {
    console.error('Failed to save user data:', error);
    throw error;
  }
}

/**
 * Get user data from secure storage
 */
export async function getUserData(): Promise<UserData | null> {
  try {
    const userData = await SecureStore.getItemAsync(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error('Failed to get user data:', error);
    return null;
  }
}

/**
 * Clear all authentication data
 */
export async function clearAuthData(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
    await SecureStore.deleteItemAsync('token_expires_at');
    await SecureStore.deleteItemAsync(USER_KEY);
  } catch (error) {
    console.error('Failed to clear auth data:', error);
    throw error;
  }
}
