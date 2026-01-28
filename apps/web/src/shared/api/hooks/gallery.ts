/**
 * Gallery API Hooks
 *
 * TanStack Query hooks for gallery operations using the generated SDK.
 */

import {
  type UseMutationOptions,
  type UseQueryOptions,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import type {
  CreateGalleryCardApiV1GalleryCardsPostData,
  CreateGalleryCardApiV1GalleryCardsPostResponse,
  GetMyGalleryCardsApiV1GalleryCardsMeGetResponse,
  GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse,
  ReorderGalleryCardsApiV1GalleryCardsReorderPutResponse,
} from '../generated'
import { GalleryService } from '../generated'
import { getAxiosClient } from '../sdk-config'

/**
 * Hook to fetch current user's gallery cards
 */
export function useMyGalleryCards(
  options?: Omit<
    UseQueryOptions<GetMyGalleryCardsApiV1GalleryCardsMeGetResponse>,
    'queryKey' | 'queryFn'
  >
) {
  return useQuery({
    queryKey: ['my-gallery'],
    queryFn: async () => {
      getAxiosClient()
      const response = await GalleryService.getMyGalleryCardsApiV1GalleryCardsMeGet()
      return response
    },
    ...options,
  })
}

/**
 * Hook to fetch another user's gallery cards
 */
export function useUserGalleryCards(
  userId: string,
  options?: Omit<
    UseQueryOptions<GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse>,
    'queryKey' | 'queryFn'
  >
) {
  return useQuery({
    queryKey: ['user-gallery', userId],
    queryFn: async () => {
      getAxiosClient()
      const response = await GalleryService.getUserGalleryCardsApiV1UsersUserIdGalleryCardsGet({
        userId,
      })
      return response
    },
    enabled: !!userId,
    ...options,
  })
}

/**
 * Hook to create a new gallery card
 */
export function useCreateGalleryCard(
  options?: UseMutationOptions<
    CreateGalleryCardApiV1GalleryCardsPostResponse,
    Error,
    CreateGalleryCardApiV1GalleryCardsPostData['requestBody']
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CreateGalleryCardApiV1GalleryCardsPostData['requestBody']) => {
      getAxiosClient()
      const response = await GalleryService.createGalleryCardApiV1GalleryCardsPost({
        requestBody: data,
      })
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-gallery'] })
    },
    ...options,
  })
}

/**
 * Hook to delete a gallery card
 */
export function useDeleteGalleryCard(options?: UseMutationOptions<void, Error, string>) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (cardId: string) => {
      getAxiosClient()
      await GalleryService.deleteGalleryCardApiV1GalleryCardsCardIdDelete({
        cardId,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-gallery'] })
    },
    ...options,
  })
}

/**
 * Hook to reorder gallery cards
 */
export function useReorderGalleryCards(
  options?: UseMutationOptions<
    ReorderGalleryCardsApiV1GalleryCardsReorderPutResponse,
    Error,
    string[]
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (cardIds: string[]) => {
      getAxiosClient()
      const response = await GalleryService.reorderGalleryCardsApiV1GalleryCardsReorderPut({
        requestBody: {
          card_ids: cardIds,
        },
      })
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-gallery'] })
    },
    ...options,
  })
}
