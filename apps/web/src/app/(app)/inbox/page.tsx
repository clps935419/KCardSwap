'use client'

import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { MessageRequestsList } from '@/features/inbox/components/MessageRequestsList'
import { SentRequestsList } from '@/features/inbox/components/SentRequestsList'
import { ThreadsList } from '@/features/inbox/components/ThreadsList'
import type { MessageRequestResponse } from '@/shared/api/generated'
import {
  getMyMessageRequestsApiV1MessageRequestsInboxGetOptions,
  getMyProfileApiV1ProfileMeGetOptions,
  getMySentMessageRequestsApiV1MessageRequestsSentGetOptions,
  getMyThreadsApiV1ThreadsGetOptions,
} from '@/shared/api/generated/@tanstack/react-query.gen'

export default function InboxPage() {
  const messageRequestsQuery = useQuery({
    ...getMyMessageRequestsApiV1MessageRequestsInboxGetOptions({
      query: {
        status_filter: 'pending',
      },
    }),
  })
  const sentRequestsQuery = useQuery({
    ...getMySentMessageRequestsApiV1MessageRequestsSentGetOptions({
      query: {
        status_filter: 'pending',
      },
    }),
  })
  const profileQuery = useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })
  const threadsQuery = useQuery({
    ...getMyThreadsApiV1ThreadsGetOptions(),
    refetchInterval: 30000, // 每 30 秒自動更新 inbox 列表
  })

  const isPageLoading =
    messageRequestsQuery.isLoading ||
    sentRequestsQuery.isLoading ||
    profileQuery.isLoading ||
    threadsQuery.isLoading

  const messageRequests = (messageRequestsQuery.data ?? []) as MessageRequestResponse[]
  const sentRequests = (sentRequestsQuery.data ?? []) as MessageRequestResponse[]
  const currentUserId = profileQuery.data?.data?.user_id
  const threads = threadsQuery.data?.threads ?? []
  const hasRequests = messageRequests.length > 0 || sentRequests.length > 0

  if (isPageLoading) {
    return (
      <div className="mx-auto w-full max-w-2xl px-4 pb-10 pt-6">
        <div className="flex items-center justify-center gap-3 p-10 text-sm text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          內容載入中
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-2xl px-4 pb-10">
      <div className={hasRequests ? 'space-y-6' : 'space-y-0'}>
        {hasRequests && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-black text-foreground">請求</p>
              <span className="text-xs font-black text-muted-foreground">
                共 {messageRequests.length + sentRequests.length} 筆
              </span>
            </div>

            {messageRequests.length > 0 && (
              <div className="space-y-3">
                <MessageRequestsList
                  limit={3}
                  showHeader={false}
                  hideEmpty
                  requests={messageRequests}
                  error={messageRequestsQuery.error}
                />
              </div>
            )}

            {sentRequests.length > 0 && (
              <div className="space-y-3">
                <SentRequestsList
                  limit={3}
                  showHeader={false}
                  hideEmpty
                  requests={sentRequests}
                  error={sentRequestsQuery.error}
                />
              </div>
            )}
          </div>
        )}

        <div className={hasRequests ? 'border-t border-border/60 pt-4' : ''}>
          <div className="mb-3 flex items-center justify-between">
            <p className="text-sm font-black text-foreground">聊天</p>
            <span className="text-xs font-black text-muted-foreground">
              共 {threads.length} 間
            </span>
          </div>
          <ThreadsList
            currentUserId={currentUserId}
            threads={threads}
            error={threadsQuery.error}
          />
        </div>
      </div>
    </div>
  )
}
