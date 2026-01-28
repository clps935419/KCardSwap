'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { PostResponse } from '@/shared/api/generated'
import { PostsService } from '@/shared/api/generated'

interface ToggleLikeResponse {
  data: {
    liked: boolean
    like_count: number
  }
}

export function useToggleLike() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: async (postId: string) => {
      const response = await PostsService.toggleLikeApiV1PostsPostIdLikePost({
        postId,
      })
      return response as unknown as ToggleLikeResponse
    },
    onMutate: async postId => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['posts'] })

      // Snapshot the previous value
      const previousPosts = queryClient.getQueryData(['posts'])

      // Optimistically update to the new value
      queryClient.setQueriesData<{ data: { posts: PostResponse[]; total: number } }>(
        { queryKey: ['posts'] },
        old => {
          if (!old) return old

          return {
            ...old,
            data: {
              ...old.data,
              posts: old.data.posts.map(post => {
                if (post.id === postId) {
                  const currentlyLiked = post.liked_by_me ?? false
                  return {
                    ...post,
                    liked_by_me: !currentlyLiked,
                    like_count: currentlyLiked
                      ? (post.like_count ?? 0) - 1
                      : (post.like_count ?? 0) + 1,
                  }
                }
                return post
              }),
            },
          }
        }
      )

      return { previousPosts }
    },
    onError: (_err, _postId, context) => {
      // Rollback on error
      if (context?.previousPosts) {
        queryClient.setQueryData(['posts'], context.previousPosts)
      }
    },
    onSettled: () => {
      // Refetch to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: ['posts'] })
    },
  })

  return mutation
}
