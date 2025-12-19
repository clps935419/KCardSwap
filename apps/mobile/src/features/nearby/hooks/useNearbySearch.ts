/**
 * Nearby search API hooks
 * M302: 附近搜尋頁 & M303: 限次錯誤處理
 * 
 * 功能：
 * - 搜尋附近的小卡
 * - 更新使用者位置
 * - 處理 429 限制錯誤
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/src/shared/api/client';
import { SEARCH_LIMITS } from '@/src/shared/config/constants';
import type { LocationCoords } from './useLocation';

// Types based on nearby search API contract
export interface NearbyCard {
  card_id: string;
  owner_id: string;
  distance_km: number;
  idol?: string;
  idol_group?: string;
  album?: string;
  version?: string;
  rarity?: string;
  image_url?: string;
  owner_nickname?: string;
}

export interface SearchNearbyRequest {
  lat: number;
  lng: number;
  radius_km?: number;
}

export interface SearchNearbyResponse {
  results: NearbyCard[];
  count: number;
}

export interface RateLimitError {
  is_rate_limit: true;
  current_count: number;
  limit: number;
  message: string;
}

/**
 * Hook for searching nearby cards
 * 
 * @param request - Search parameters (lat, lng, radius_km)
 * @param enabled - Whether to enable automatic query execution
 * @returns Query result with nearby cards
 * 
 * @example
 * ```tsx
 * const { data, error, refetch } = useNearbySearch({
 *   lat: 25.0330,
 *   lng: 121.5654,
 *   radius_km: 10
 * });
 * 
 * if (error?.response?.status === 429) {
 *   // Handle rate limit error
 * }
 * ```
 */
export function useNearbySearch(request: SearchNearbyRequest | null, enabled = false) {
  return useQuery({
    queryKey: ['nearby-search', request],
    queryFn: async () => {
      if (!request) {
        throw new Error('Search location is required');
      }

      try {
        const response = await apiClient.post<SearchNearbyResponse>(
          '/nearby/search',
          request
        );
        return response.data;
      } catch (error: any) {
        // Enhanced error handling for 429 rate limit
        if (error.response?.status === 429) {
          const rateLimitError: RateLimitError = {
            is_rate_limit: true,
            current_count: SEARCH_LIMITS.FREE_USER_DAILY_LIMIT,
            limit: SEARCH_LIMITS.FREE_USER_DAILY_LIMIT,
            message: error.response?.data?.detail || '每日搜尋次數已達上限',
          };

          // Try to parse actual counts from error message
          const match = error.response?.data?.detail?.match(/(\d+)\/(\d+)/);
          if (match) {
            rateLimitError.current_count = parseInt(match[1], 10);
            rateLimitError.limit = parseInt(match[2], 10);
          }

          throw rateLimitError;
        }
        throw error;
      }
    },
    enabled: enabled && request !== null,
    // Don't retry on rate limit errors
    retry: (failureCount, error: any) => {
      if (error.is_rate_limit) {
        return false;
      }
      return failureCount < 2;
    },
    // Keep data for 5 minutes
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook for updating user's location
 * 
 * @returns Mutation for updating location
 * 
 * @example
 * ```tsx
 * const updateLocation = useUpdateLocation();
 * 
 * await updateLocation.mutateAsync({
 *   lat: 25.0330,
 *   lng: 121.5654
 * });
 * ```
 */
export function useUpdateLocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (coords: LocationCoords) => {
      const response = await apiClient.put('/nearby/location', {
        lat: coords.latitude,
        lng: coords.longitude,
      });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate nearby searches to reflect new location
      queryClient.invalidateQueries({ queryKey: ['nearby-search'] });
    },
  });
}

/**
 * Helper to check if error is a rate limit error
 * 
 * @param error - Error object
 * @returns True if rate limit error
 */
export function isRateLimitError(error: any): error is RateLimitError {
  return error && error.is_rate_limit === true;
}
