/**
 * usePost - Hook for fetching a single post by ID (Web)
 * Phase 9: Returns post with media_asset_ids for image display
 */
import { useQuery } from '@tanstack/react-query'
import { getPostApiV1PostsPostIdGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

/**
 * Hook to fetch a single post by ID
 * 
 * @param postId - The post ID to fetch
 * @param options - Additional query options
 * @returns Query result with post data
 * 
 * @example
 * ```tsx
 * const { data, isLoading, error } = usePost('post-id-123');
 * const post = data?.data;
 * const mediaAssetIds = post?.media_asset_ids || [];
 * ```
 */
export function usePost(
  postId: string,
  options?: {
    enabled?: boolean
  }
) {
  return useQuery({
    ...getPostApiV1PostsPostIdGetOptions({
      path: {
        post_id: postId,
      },
    }),
    enabled: options?.enabled !== false && !!postId,
    // Cache for 5 minutes
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })
}
