import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { config } from '../config';
import { getAccessToken, getRefreshToken, saveTokens, isTokenExpired } from '../auth/session';
import { mapApiError } from './errorMapper';

/**
 * Create axios instance with default configuration
 */
export const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: config.apiBaseUrl,
    timeout: config.apiTimeout,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor: Add auth token to requests
  client.interceptors.request.use(
    async (requestConfig: InternalAxiosRequestConfig) => {
      const token = await getAccessToken();
      
      if (token && requestConfig.headers) {
        requestConfig.headers.Authorization = `Bearer ${token}`;
      }

      return requestConfig;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor: Handle errors and token refresh
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

      // If 401 error and we haven't retried yet, try to refresh token
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = await getRefreshToken();
          
          if (!refreshToken) {
            // No refresh token, user needs to login again
            throw mapApiError(error);
          }

          // Try to refresh the token
          const response = await axios.post(
            `${config.apiBaseUrl}/auth/refresh`,
            { refreshToken },
            { timeout: config.apiTimeout }
          );

          const { accessToken, refreshToken: newRefreshToken, expiresIn } = response.data;
          
          // Save new tokens
          await saveTokens({
            accessToken,
            refreshToken: newRefreshToken,
            expiresAt: Date.now() + expiresIn * 1000,
          });

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          }
          
          return client(originalRequest);
        } catch (refreshError) {
          // Refresh failed, user needs to login again
          // Clear tokens and redirect to login will be handled by auth store
          throw mapApiError(refreshError);
        }
      }

      // For other errors, map and throw
      throw mapApiError(error);
    }
  );

  return client;
};

// Export a singleton instance
export const apiClient = createApiClient();

/**
 * Check and refresh token if needed before making requests
 */
export async function ensureValidToken(): Promise<void> {
  const expired = await isTokenExpired();
  
  if (expired) {
    const refreshToken = await getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(
        `${config.apiBaseUrl}/auth/refresh`,
        { refreshToken },
        { timeout: config.apiTimeout }
      );

      const { accessToken, refreshToken: newRefreshToken, expiresIn } = response.data;
      
      await saveTokens({
        accessToken,
        refreshToken: newRefreshToken,
        expiresAt: Date.now() + expiresIn * 1000,
      });
    } catch (error) {
      throw mapApiError(error);
    }
  }
}
