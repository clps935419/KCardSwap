import { create } from 'zustand';
import {
  UserData,
  saveTokens,
  saveUserData,
  getUserData,
  clearAuthData,
  TokenData,
  getRefreshToken,
  isTokenExpired,
} from '@/src/shared/auth/session';
import { client } from '@/src/shared/api/sdk';
import type { RefreshTokenRequest, RefreshTokenResponse } from '@/src/shared/api/sdk';

export interface AuthState {
  user: UserData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: UserData) => void;
  setTokens: (tokens: TokenData) => void;
  login: (tokens: TokenData, user: UserData) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  clearError: () => void;
  initialize: () => Promise<void>;
}

/**
 * Refresh access token using SDK
 * 
 * @returns New access token or null if refresh fails
 */
async function refreshAccessToken(): Promise<TokenData | null> {
  try {
    const refreshToken = await getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    // Use SDK client directly for token refresh
    const requestBody: RefreshTokenRequest = {
      refresh_token: refreshToken,
    };

    const response = await client.post<RefreshTokenResponse>({
      url: '/api/v1/auth/refresh',
      body: requestBody,
    });

    if (!response.data?.data) {
      return null;
    }

    const tokenData: TokenData = {
      accessToken: response.data.data.access_token,
      refreshToken: response.data.data.refresh_token,
      expiresAt: Date.now() + response.data.data.expires_in * 1000,
    };

    await saveTokens(tokenData);
    return tokenData;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    return null;
  }
}

/**
 * Ensure valid token - check expiration and refresh if needed
 */
async function ensureValidToken(): Promise<void> {
  const expired = await isTokenExpired();

  if (expired) {
    const tokens = await refreshAccessToken();
    
    if (!tokens) {
      throw new Error('Failed to refresh token');
    }
  }
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  setUser: (user: UserData) => {
    set({ user, isAuthenticated: true });
  },

  setTokens: async (tokens: TokenData) => {
    try {
      await saveTokens(tokens);
    } catch (error) {
      console.error('Failed to save tokens:', error);
      set({ error: '儲存驗證資料失敗' });
    }
  },

  login: async (tokens: TokenData, user: UserData) => {
    try {
      set({ isLoading: true, error: null });

      // Save tokens and user data
      await saveTokens(tokens);
      await saveUserData(user);

      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      console.error('Login failed:', error);
      set({
        error: '登入失敗，請再試一次。',
        isLoading: false,
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      set({ isLoading: true });

      // Clear all auth data
      await clearAuthData();

      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      console.error('Logout failed:', error);
      set({
        error: '登出失敗，請再試一次。',
        isLoading: false,
      });
    }
  },

  refreshSession: async () => {
    try {
      await ensureValidToken();
    } catch (error) {
      console.error('Session refresh failed:', error);
      // If refresh fails, logout the user
      await get().logout();
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  initialize: async () => {
    try {
      set({ isLoading: true });

      // Try to load user data from storage
      const userData = await getUserData();

      if (userData) {
        // Try to refresh the session
        try {
          await ensureValidToken();
          set({
            user: userData,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // If refresh fails, clear auth data
          console.error('Session initialization failed:', error);
          await clearAuthData();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } else {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Failed to initialize authentication',
      });
    }
  },
}));
