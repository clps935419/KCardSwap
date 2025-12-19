/**
 * SDK Runtime Configuration
 * 
 * This file configures the generated hey-api/openapi-ts SDK client:
 * - Sets baseURL to host-only (OpenAPI paths already include /api/v1)
 * - Configures authentication headers
 * - Handles token refresh behavior
 * 
 * Usage:
 *   import { configureSDK } from '@/src/shared/api/sdk';
 *   configureSDK();
 */

import type { RequestOptions } from './generated/client';
import { client } from './generated/client.gen';
import { getAccessToken, getRefreshToken, isTokenExpired, saveTokens, clearAuthData } from '../auth/session';

/**
 * Get the API base URL from environment variables
 * Default to localhost for development
 */
const getBaseUrl = (): string => {
  const envUrl = process.env.EXPO_PUBLIC_API_BASE_URL;
  
  if (envUrl) {
    // Remove any trailing /api/v1 if present (OpenAPI paths already include it)
    return envUrl.replace(/\/api\/v1\/?$/, '');
  }
  
  // Default fallback
  return 'http://localhost:8080';
};

/**
 * Refresh the access token using the refresh token
 * Returns the new access token or null if refresh fails
 */
const refreshAccessToken = async (): Promise<string | null> => {
  try {
    const refreshToken = await getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    // Call the refresh endpoint using the SDK
    const response = await client.post<{
      data?: {
        access_token: string;
        refresh_token: string;
        expires_in: number;
      };
    }>({
      url: '/auth/refresh',
      body: { refresh_token: refreshToken },
    });

    // Type assertion for the response data structure
    const responseData = response.data as unknown as {
      data?: {
        access_token: string;
        refresh_token: string;
        expires_in: number;
      };
    };

    if (responseData?.data) {
      const tokenData = {
        accessToken: responseData.data.access_token,
        refreshToken: responseData.data.refresh_token,
        expiresAt: Date.now() + responseData.data.expires_in * 1000,
      };
      await saveTokens(tokenData);
      return tokenData.accessToken;
    }

    return null;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    return null;
  }
};

/**
 * Configure the SDK client with base URL and interceptors
 * Call this function once at app startup
 */
export const configureSDK = () => {
  // Set base URL (host-only, no /api/v1 suffix)
  client.setConfig({
    baseUrl: getBaseUrl(),
  });

  // Request interceptor: Add auth token and handle expiration
  client.interceptors.request.use(async (request, options: RequestOptions) => {
    // Check if token is expired and try to refresh
    if (await isTokenExpired()) {
      const newToken = await refreshAccessToken();
      if (!newToken) {
        // Token refresh failed, clear auth data
        await clearAuthData();
        // Let the request continue - it will fail with 401
        // The app should handle 401 by redirecting to login
      }
    }

    // Add auth token to request
    const token = await getAccessToken();
    if (token) {
      options.headers = {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    return request;
  });

  // Response interceptor: Handle 401 errors
  client.interceptors.response.use(async (response) => {
    // Handle successful responses
    return response;
  });
};

/**
 * Re-export the configured client for direct use
 * Most users should use the TanStack Query options/mutations instead
 */
export { client };

/**
 * Re-export SDK functions for direct API calls
 * For React components, prefer using TanStack Query options/mutations from './generated/@tanstack/react-query.gen'
 */
export * from './generated/sdk.gen';

/**
 * Re-export types for use in components
 */
export type * from './generated/types.gen';

/**
 * Re-export TanStack Query option helpers
 * These are the recommended way to use the SDK in React components
 */
export * from './generated/@tanstack/react-query.gen';
