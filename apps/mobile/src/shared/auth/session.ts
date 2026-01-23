import { Platform } from 'react-native';
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
 * Cross-platform storage adapter
 * Uses SecureStore on mobile, localStorage on web
 */
const storage = {
  async setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  },

  async getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    } else {
      return await SecureStore.getItemAsync(key);
    }
  },

  async deleteItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
    } else {
      await SecureStore.deleteItemAsync(key);
    }
  },
};

/**
 * Save authentication tokens to secure storage
 */
export async function saveTokens(tokens: TokenData): Promise<void> {
  try {
    await storage.setItem(TOKEN_KEY, tokens.accessToken);
    await storage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
    await storage.setItem('token_expires_at', tokens.expiresAt.toString());
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
    return await storage.getItem(TOKEN_KEY);
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
    return await storage.getItem(REFRESH_TOKEN_KEY);
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
    const expiresAt = await storage.getItem('token_expires_at');
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
    await storage.setItem(USER_KEY, JSON.stringify(user));
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
    const userData = await storage.getItem(USER_KEY);
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
    await storage.deleteItem(TOKEN_KEY);
    await storage.deleteItem(REFRESH_TOKEN_KEY);
    await storage.deleteItem('token_expires_at');
    await storage.deleteItem(USER_KEY);
  } catch (error) {
    console.error('Failed to clear auth data:', error);
    throw error;
  }
}
