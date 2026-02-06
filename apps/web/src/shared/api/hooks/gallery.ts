/**
 * Gallery API Hooks
 *
 * TanStack Query hooks for gallery operations using the generated SDK.
 */

import {
  type UseMutationOptions,
  type UseQueryOptions,
  type UseQueryResult,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import type {
  CreateGalleryCardApiV1GalleryCardsPostError,
  CreateGalleryCardApiV1GalleryCardsPostResponse,
  CreateGalleryCardRequest,
  GetMyGalleryCardsApiV1GalleryCardsMeGetError,
  GetMyGalleryCardsApiV1GalleryCardsMeGetResponse,
  GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetError,
  GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse,
  ReorderGalleryCardsApiV1GalleryCardsReorderPutResponse,
} from '../generated'
import {
  createGalleryCardApiV1GalleryCardsPost,
  deleteGalleryCardApiV1GalleryCardsCardIdDelete,
  reorderGalleryCardsApiV1GalleryCardsReorderPut,
} from '../generated'
import {
  getMyGalleryCardsApiV1GalleryCardsMeGetOptions,
  getMyGalleryCardsApiV1GalleryCardsMeGetQueryKey,
  getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions,
} from '../generated/@tanstack/react-query.gen'

/**
 * Hook to fetch current user's gallery cards
 */
export function useMyGalleryCards(
  options?: Omit<
    UseQueryOptions<
      GetMyGalleryCardsApiV1GalleryCardsMeGetResponse,
      AxiosError<GetMyGalleryCardsApiV1GalleryCardsMeGetError>
    >,
    'queryKey' | 'queryFn'
  >
): UseQueryResult<
  GetMyGalleryCardsApiV1GalleryCardsMeGetResponse,
  AxiosError<GetMyGalleryCardsApiV1GalleryCardsMeGetError>
> {
  const queryOptions = getMyGalleryCardsApiV1GalleryCardsMeGetOptions()
  const mergedOptions = {
    ...queryOptions,
    ...options,
  } as UseQueryOptions<
    GetMyGalleryCardsApiV1GalleryCardsMeGetResponse,
    AxiosError<GetMyGalleryCardsApiV1GalleryCardsMeGetError>
  >
  return useQuery(mergedOptions) as UseQueryResult<
    GetMyGalleryCardsApiV1GalleryCardsMeGetResponse,
    AxiosError<GetMyGalleryCardsApiV1GalleryCardsMeGetError>
  >
}

/**
 * Hook to fetch another user's gallery cards
 */
export function useUserGalleryCards(
  userId: string,
  options?: Omit<
    UseQueryOptions<
      GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse,
      AxiosError<GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetError>
    >,
    'queryKey' | 'queryFn'
  >
): UseQueryResult<
  GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse,
  AxiosError<GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetError>
> {
  const queryOptions = getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions({
    path: {
      user_id: userId,
    },
  })
  const mergedOptions = {
    ...queryOptions,
    enabled: !!userId,
    ...options,
  } as UseQueryOptions<
    GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse,
    AxiosError<GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetError>
  >
  return useQuery(mergedOptions) as UseQueryResult<
    GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetResponse,
    AxiosError<GetUserGalleryCardsApiV1UsersUserIdGalleryCardsGetError>
  >
}

/**
 * Hook to create a new gallery card
 */
export function useCreateGalleryCard(
  options?: UseMutationOptions<
    CreateGalleryCardApiV1GalleryCardsPostResponse,
    AxiosError<CreateGalleryCardApiV1GalleryCardsPostError>,
    CreateGalleryCardRequest
  >
) {
  const queryClient = useQueryClient()

  return useMutation<
    CreateGalleryCardApiV1GalleryCardsPostResponse,
    AxiosError<CreateGalleryCardApiV1GalleryCardsPostError>,
    CreateGalleryCardRequest
  >({
    mutationFn: async (data: CreateGalleryCardRequest) => {
      const response = await createGalleryCardApiV1GalleryCardsPost({
        body: data,
        throwOnError: true,
      })
      return response.data as CreateGalleryCardApiV1GalleryCardsPostResponse
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

/**
 * Hook to delete a gallery card
 */
export function useDeleteGalleryCard(options?: UseMutationOptions<void, Error, string>) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (cardId: string) => {
      await deleteGalleryCardApiV1GalleryCardsCardIdDelete({
        path: {
          card_id: cardId,
        },
        throwOnError: true,
      })
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
      const response = await reorderGalleryCardsApiV1GalleryCardsReorderPut({
        body: {
          card_ids: cardIds,
        },
        throwOnError: true,
      })
      return response.data as ReorderGalleryCardsApiV1GalleryCardsReorderPutResponse
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
