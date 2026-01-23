import { useQuery } from '@tanstack/react-query'
import { listPostsApiV1PostsGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'
import type { PostCategory } from '@/shared/api/generated'

interface UsePostsListParams {
  cityCode?: string | null
  category?: PostCategory | null
}

export function usePostsList({ cityCode, category }: UsePostsListParams = {}) {
  return useQuery(
    listPostsApiV1PostsGetOptions({
      query: {
        city_code: cityCode,
        category: category,
        limit: 50,
      },
    })
  )
}
