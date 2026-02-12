'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { PostResponse } from '@/shared/api/generated'
import { toggleLikeApiV1PostsPostIdLikePost } from '@/shared/api/generated'
import {
  getPostApiV1PostsPostIdGetQueryKey,
  listPostsApiV1PostsGetQueryKey,
} from '@/shared/api/generated/@tanstack/react-query.gen'

interface ToggleLikeResponse {
  data: {
    liked: boolean
    like_count: number
  }
}

export function useToggleLike() {
  const queryClient = useQueryClient()
  const postsQueryKey = listPostsApiV1PostsGetQueryKey()

  const mutation = useMutation({
    mutationFn: async (postId: string) => {
      const response = await toggleLikeApiV1PostsPostIdLikePost({
        path: {
          post_id: postId,
        },
        throwOnError: true,
      })
      return response.data as ToggleLikeResponse
    },
    onMutate: async postId => {
      const postDetailQueryKey = getPostApiV1PostsPostIdGetQueryKey({
        path: {
          post_id: postId,
        },
      })

      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: postsQueryKey })
      await queryClient.cancelQueries({ queryKey: postDetailQueryKey })

      // Snapshot the previous value
      const previousPosts = queryClient.getQueriesData({ queryKey: postsQueryKey })
      const previousPostDetail = queryClient.getQueryData(postDetailQueryKey)

      // Optimistically update to the new value
      queryClient.setQueriesData<{ data: { posts: PostResponse[]; total: number } }>(
        { queryKey: postsQueryKey },
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
                      ? Math.max(0, (post.like_count ?? 0) - 1)
                      : (post.like_count ?? 0) + 1,
                  }
                }
                return post
              }),
            },
          }
        }
      )

      queryClient.setQueryData(postDetailQueryKey, old => {
        if (!old || typeof old !== 'object') return old
        const typed = old as { data?: PostResponse }
        const currentPost = typed.data
        if (!currentPost || currentPost.id !== postId) return old

        const currentlyLiked = currentPost.liked_by_me ?? false

        return {
          ...typed,
          data: {
            ...currentPost,
            liked_by_me: !currentlyLiked,
            like_count: currentlyLiked
              ? Math.max(0, (currentPost.like_count ?? 0) - 1)
              : (currentPost.like_count ?? 0) + 1,
          },
        }
      })

      return { previousPosts, previousPostDetail, postDetailQueryKey }
    },
    onError: (_err, _postId, context) => {
      // Rollback on error
      if (context?.previousPosts) {
        context.previousPosts.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data)
        })
      }

      if (context?.postDetailQueryKey) {
        queryClient.setQueryData(context.postDetailQueryKey, context.previousPostDetail)
      }
    },
    onSettled: (_data, _error, postId) => {
      // Refetch to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: postsQueryKey })

      queryClient.invalidateQueries({
        queryKey: getPostApiV1PostsPostIdGetQueryKey({
          path: {
            post_id: postId,
          },
        }),
      })
    },
  })

  return mutation
}
