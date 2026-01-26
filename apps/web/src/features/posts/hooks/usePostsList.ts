import { useQuery } from '@tanstack/react-query'
import type { PostCategory } from '@/shared/api/generated'
import { PostsService } from '@/shared/api/generated/services.gen'

interface UsePostsListParams {
  cityCode?: string | null
  category?: PostCategory | null
}

export function usePostsList({ cityCode, category }: UsePostsListParams = {}) {
  return useQuery({
    queryKey: ['posts', cityCode, category],
    queryFn: () =>
      PostsService.listPostsApiV1PostsGet({
        cityCode: cityCode || undefined,
        category: category || undefined,
        limit: 50,
      }),
  })
}
