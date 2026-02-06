import { useQuery } from '@tanstack/react-query'
import type { PostCategory } from '@/shared/api/generated'
import { listPostsApiV1PostsGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

interface UsePostsListParams {
  cityCode?: string | null
  category?: PostCategory | null
}

export function usePostsList({ cityCode, category }: UsePostsListParams = {}) {
  const queryOptions = listPostsApiV1PostsGetOptions({
    query: {
      city_code: cityCode || undefined,
      category: category || undefined,
      limit: 50,
    },
  })

  return useQuery({
    ...queryOptions,
  })
}
