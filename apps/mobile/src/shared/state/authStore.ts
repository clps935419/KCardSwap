import { create } from 'zustand';
import { UserData, saveTokens, saveUserData, getUserData, clearAuthData, TokenData } from '../auth/session';
import { ensureValidToken } from '../api/client';

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
      set({ error: 'Failed to save authentication tokens' });
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
        error: null 
      });
    } catch (error) {
      console.error('Login failed:', error);
      set({ 
        error: 'Login failed. Please try again.',
        isLoading: false 
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
        error: null 
      });
    } catch (error) {
      console.error('Logout failed:', error);
      set({ 
        error: 'Logout failed. Please try again.',
        isLoading: false 
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
            isLoading: false 
          });
        } catch (error) {
          // If refresh fails, clear auth data
          console.error('Session initialization failed:', error);
          await clearAuthData();
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false 
          });
        }
      } else {
        set({ 
          user: null, 
          isAuthenticated: false, 
          isLoading: false 
        });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      set({ 
        user: null, 
        isAuthenticated: false, 
        isLoading: false,
        error: 'Failed to initialize authentication' 
      });
    }
  },
}));
