/**
 * Custom hook for sending messages
 *
 * TODO: Replace with generated SDK mutation after OpenAPI generation
 */
'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ThreadMessageResponse } from '@/shared/api/generated'
import { sendMessageApiV1ThreadsThreadIdMessagesPost } from '@/shared/api/generated'
import {
  getMyThreadsApiV1ThreadsGetQueryKey,
  getThreadMessagesApiV1ThreadsThreadIdMessagesGetQueryKey,
} from '@/shared/api/generated/@tanstack/react-query.gen'

interface SendMessageParams {
  threadId: string
  content: string
  postId?: string
}

export function useSendMessage() {
  const queryClient = useQueryClient()

  const mutation = useMutation<ThreadMessageResponse, Error, SendMessageParams>({
    mutationFn: async params => {
      const response = await sendMessageApiV1ThreadsThreadIdMessagesPost({
        path: {
          thread_id: params.threadId,
        },
        body: {
          content: params.content,
          post_id: params.postId ?? null,
        },
        throwOnError: true,
      })
      return response.data as ThreadMessageResponse
    },
    onSuccess: (_data, params) => {
      queryClient.invalidateQueries({
        queryKey: getThreadMessagesApiV1ThreadsThreadIdMessagesGetQueryKey({
          path: {
            thread_id: params.threadId,
          },
          query: {
            limit: 50,
            offset: 0,
          },
        }),
      })
      queryClient.invalidateQueries({ queryKey: getMyThreadsApiV1ThreadsGetQueryKey() })
    },
  })

  return {
    sendMessage: mutation.mutateAsync,
    loading: mutation.isPending,
    error: mutation.error,
  }
}
