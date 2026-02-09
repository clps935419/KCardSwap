/**
 * Custom hook for creating message requests
 *
 * TODO: Replace with generated SDK mutation after OpenAPI generation
 */
'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { MessageRequestResponse } from '@/shared/api/generated'
import { createMessageRequestApiV1MessageRequestsPost } from '@/shared/api/generated'
import { getMyMessageRequestsApiV1MessageRequestsInboxGetQueryKey } from '@/shared/api/generated/@tanstack/react-query.gen'

interface CreateMessageRequestParams {
  recipientId: string
  initialMessage: string
  postId?: string
}

export function useCreateMessageRequest() {
  const queryClient = useQueryClient()

  const mutation = useMutation<MessageRequestResponse, Error, CreateMessageRequestParams>({
    mutationFn: async params => {
      const response = await createMessageRequestApiV1MessageRequestsPost({
        body: {
          recipient_id: params.recipientId,
          initial_message: params.initialMessage,
          post_id: params.postId ?? null,
        },
        throwOnError: true,
      })
      return response.data as MessageRequestResponse
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: getMyMessageRequestsApiV1MessageRequestsInboxGetQueryKey({
          query: {
            status_filter: 'pending',
          },
        }),
      })
    },
  })

  return {
    createRequest: mutation.mutateAsync,
    loading: mutation.isPending,
    error: mutation.error,
  }
}
