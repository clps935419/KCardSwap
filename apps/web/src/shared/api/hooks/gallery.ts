/**
 * Gallery API Hooks
 *
 * TanStack Query hooks for gallery operations using the generated SDK.
 */

import { type UseMutationOptions, type UseQueryOptions, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type {
  CreateGalleryCardApiV1GalleryCardsPostResponse,
  CreateGalleryCardRequest,
  GetMyGalleryCardsApiV1GalleryCardsMeGetResponse,
  GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse,
  ReorderGalleryCardsApiV1GalleryCardsReorderPutResponse,
} from '../generated'
import {
  createGalleryCardApiV1GalleryCardsPostMutation,
  deleteGalleryCardApiV1GalleryCardsCardIdDeleteMutation,
  getMyGalleryCardsApiV1GalleryCardsMeGetOptions,
  getMyGalleryCardsApiV1GalleryCardsMeGetQueryKey,
  getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions,
  reorderGalleryCardsApiV1GalleryCardsReorderPutMutation,
} from '../generated/@tanstack/react-query.gen'

/**
 * Hook to fetch current user's gallery cards
 */
export function useMyGalleryCards(
  options?: Omit<
    UseQueryOptions<GetMyGalleryCardsApiV1GalleryCardsMeGetResponse>,
    'queryKey' | 'queryFn'
  >
) {
  const queryOptions = getMyGalleryCardsApiV1GalleryCardsMeGetOptions()
  return useQuery({
    ...queryOptions,
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
  const queryOptions = getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions({
    path: {
      user_id: userId,
    },
  })
  return useQuery({
    ...queryOptions,
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
    CreateGalleryCardRequest
  >
) {
  const queryClient = useQueryClient()
  const mutationOptions = createGalleryCardApiV1GalleryCardsPostMutation()

  return useMutation({
    ...mutationOptions,
    mutationFn: async (data: CreateGalleryCardRequest) => {
      const response = await mutationOptions.mutationFn?.({
        body: data,
      })
      return response as CreateGalleryCardApiV1GalleryCardsPostResponse
    },
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries({
        queryKey: getMyGalleryCardsApiV1GalleryCardsMeGetQueryKey(),
      })
      options?.onSuccess?.(data, variables, context)
    },
    ...options,
  })
}

/**
 * Hook to delete a gallery card
 */
export function useDeleteGalleryCard(options?: UseMutationOptions<void, Error, string>) {
  const queryClient = useQueryClient()
  const mutationOptions = deleteGalleryCardApiV1GalleryCardsCardIdDeleteMutation()

  return useMutation({
    ...mutationOptions,
    mutationFn: async (cardId: string) => {
      await mutationOptions.mutationFn?.({
        path: {
          card_id: cardId,
        },
      })
    },
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries({
        queryKey: getMyGalleryCardsApiV1GalleryCardsMeGetQueryKey(),
      })
      options?.onSuccess?.(data, variables, context)
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
  const mutationOptions = reorderGalleryCardsApiV1GalleryCardsReorderPutMutation()

  return useMutation({
    ...mutationOptions,
    mutationFn: async (cardIds: string[]) => {
      const response = await mutationOptions.mutationFn?.({
        body: {
          card_ids: cardIds,
        },
      })
      return response as ReorderGalleryCardsApiV1GalleryCardsReorderPutResponse
    },
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries({
        queryKey: getMyGalleryCardsApiV1GalleryCardsMeGetQueryKey(),
      })
      options?.onSuccess?.(data, variables, context)
    },
    ...options,
  })
}
