/**
 * Flow mutations for multi-step operations.
 */

import { type UseMutationOptions, useMutation, useQueryClient } from '@tanstack/react-query'
import type {
  CityCode,
  GalleryCardResponse,
  PostCategory,
  PostResponse,
  PostScope,
} from '@/shared/api/generated'
import {
  attachMediaToGalleryCardApiV1MediaGalleryCardsCardIdAttachPost,
  attachMediaToPostApiV1MediaPostsPostIdAttachPost,
} from '@/shared/api/generated'
import {
  createGalleryCardApiV1GalleryCardsPostMutation,
  createPostApiV1PostsPostMutation,
  getMyGalleryCardsApiV1GalleryCardsMeGetQueryKey,
  listPostsApiV1PostsGetQueryKey,
} from '@/shared/api/generated/@tanstack/react-query.gen'
import { runUploadFlow } from '@/shared/api/hooks/media'

export interface CreatePostFlowInput {
  title: string
  content: string
  scope: PostScope
  city_code?: CityCode | null
  category: PostCategory
  imageFile?: File
  onUploadProgress?: (progress: number) => void
}

export interface CreateGalleryCardFlowInput {
  title: string
  idol_name: string
  era?: string
  description?: string
  imageFile?: File
  onUploadProgress?: (progress: number) => void
}

export function useCreatePostFlowMutation(
  options?: UseMutationOptions<PostResponse, Error, CreatePostFlowInput>
) {
  const queryClient = useQueryClient()
  const createPostMutationOptions = createPostApiV1PostsPostMutation()

  return useMutation({
    mutationFn: async input => {
      const { title, content, scope, city_code, category, imageFile, onUploadProgress } = input

      let mediaId: string | undefined

      if (imageFile) {
        mediaId = await runUploadFlow({
          file: imageFile,
          onProgress: onUploadProgress,
        })
      }

      if (!createPostMutationOptions.mutationFn) {
        throw new Error('Create post mutation is not available')
      }

      const postResponse = await createPostMutationOptions.mutationFn(
        {
          body: {
            title,
            content,
            scope,
            city_code: scope === 'city' ? city_code || null : null,
            category,
          },
        } as Parameters<typeof createPostMutationOptions.mutationFn>[0],
        undefined as unknown as Parameters<typeof createPostMutationOptions.mutationFn>[1]
      )

      if (mediaId && postResponse?.data?.id) {
        await attachMediaToPostApiV1MediaPostsPostIdAttachPost({
          path: {
            post_id: postResponse.data.id,
          },
          body: {
            media_id: mediaId,
          },
          throwOnError: true,
        })
      }

      return postResponse.data as PostResponse
    },
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: listPostsApiV1PostsGetQueryKey() })
      options?.onSuccess?.(...args)
    },
    ...options,
  })
}

export function useCreateGalleryCardFlowMutation(
  options?: UseMutationOptions<GalleryCardResponse, Error, CreateGalleryCardFlowInput>
) {
  const queryClient = useQueryClient()
  const createGalleryCardMutationOptions = createGalleryCardApiV1GalleryCardsPostMutation()

  return useMutation({
    mutationFn: async input => {
      const { title, idol_name, era, description, imageFile, onUploadProgress } = input

      let mediaId: string | undefined

      if (imageFile) {
        mediaId = await runUploadFlow({
          file: imageFile,
          onProgress: onUploadProgress,
        })
      }

      if (!createGalleryCardMutationOptions.mutationFn) {
        throw new Error('Create gallery card mutation is not available')
      }

      const response = await createGalleryCardMutationOptions.mutationFn(
        {
          body: {
            title,
            idol_name,
            era: era || undefined,
            description: description || undefined,
          },
        } as Parameters<typeof createGalleryCardMutationOptions.mutationFn>[0],
        undefined as unknown as Parameters<typeof createGalleryCardMutationOptions.mutationFn>[1]
      )

      if (mediaId && response?.data?.id) {
        await attachMediaToGalleryCardApiV1MediaGalleryCardsCardIdAttachPost({
          path: {
            card_id: response.data.id,
          },
          body: {
            media_id: mediaId,
          },
          throwOnError: true,
        })
      }

      return response.data as GalleryCardResponse
    },
    onSuccess: (...args) => {
      queryClient.invalidateQueries({
        queryKey: getMyGalleryCardsApiV1GalleryCardsMeGetQueryKey(),
      })
      options?.onSuccess?.(...args)
    },
    ...options,
  })
}
