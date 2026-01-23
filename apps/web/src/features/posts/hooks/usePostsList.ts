import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api/client'
import type { PostCategory, PostListResponse } from '@/shared/api/generated'

interface UsePostsListParams {
  cityCode?: string | null
  category?: PostCategory | null
}

export function usePostsList({ cityCode, category }: UsePostsListParams = {}) {
  return useQuery({
    queryKey: ['posts', 'list', { cityCode, category }],
    queryFn: async () => {
      const params: Record<string, any> = {}
      if (cityCode) params.cityCode = cityCode
      if (category) params.category = category
      params.limit = 50

      const response = await apiClient.get<PostListResponse>('/api/v1/posts', { params })
      return response.data
    },
  })
}
