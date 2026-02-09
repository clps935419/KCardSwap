/**
 * useReadMediaUrls - Hook for batch fetching signed read URLs for media assets (Web)
 * Phase 9: Login-only access to images with 10-minute TTL
 */
import { useQuery } from '@tanstack/react-query'
import { getMediaReadUrlsApiV1MediaReadUrlsPost } from '@/shared/api/generated'

/**
 * Hook to batch fetch signed read URLs for media assets
 *
 * @param mediaAssetIds - Array of media asset IDs to fetch URLs for
 * @param options - Additional query options
 * @returns Query result with urls mapping and expires_in_minutes
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useReadMediaUrls(['uuid-1', 'uuid-2']);
 * const imageUrl = data?.data?.urls['uuid-1'];
 * ```
 */
export function useReadMediaUrls(
  mediaAssetIds: string[],
  options?: {
    enabled?: boolean
  }
) {
  return useQuery({
    queryKey: ['media', 'read-urls', ...mediaAssetIds.sort()],
    queryFn: async () => {
      if (mediaAssetIds.length === 0) {
        return {
          data: {
            urls: {},
            expires_in_minutes: 10,
          },
        }
      }

      const response = await getMediaReadUrlsApiV1MediaReadUrlsPost({
        body: {
          media_asset_ids: mediaAssetIds,
        },
        throwOnError: true,
      })

      return response.data
    },
    enabled: options?.enabled !== false && mediaAssetIds.length > 0,
    // Cache for 9 minutes (slightly less than 10-minute TTL)
    staleTime: 9 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })
}
