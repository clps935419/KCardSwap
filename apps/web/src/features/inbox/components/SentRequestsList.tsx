/**
 * SentRequestsList Component
 *
 * Displays pending message requests sent by the current user.
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { UserAvatar } from '@/components/ui/user-avatar'
import type { MessageRequestResponse } from '@/shared/api/generated'
import { getMySentMessageRequestsApiV1MessageRequestsSentGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

interface SentRequestsListProps {
  limit?: number
  showHeader?: boolean
  hideEmpty?: boolean
}

export function SentRequestsList({ limit, showHeader, hideEmpty }: SentRequestsListProps) {
  const [showAll, setShowAll] = useState(false)

  const requestsQueryOptions = getMySentMessageRequestsApiV1MessageRequestsSentGetOptions({
    query: {
      status_filter: 'pending',
    },
  })
  const requestsQuery = useQuery({
    ...requestsQueryOptions,
  })
  const requests = (requestsQuery.data ?? []) as MessageRequestResponse[]

  if (requestsQuery.isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (requestsQuery.error) {
    return (
      <div className="text-center text-muted-foreground text-sm py-8">載入已送出請求時發生錯誤</div>
    )
  }

  if (requests.length === 0) {
    if (hideEmpty) {
      return null
    }
    return (
      <div className="text-center text-muted-foreground text-sm py-8">目前沒有等待中的請求</div>
    )
  }

  const totalCount = requests.length
  const displayLimit = limit ?? totalCount
  const shouldShowAll = showAll || totalCount <= displayLimit
  const displayRequests = shouldShowAll ? requests : requests.slice(0, displayLimit)
  const canViewAll = !shouldShowAll && totalCount > displayLimit

  return (
    <div className="space-y-4">
      {showHeader && (
        <div className="flex items-center justify-between">
          <p className="text-sm font-black text-foreground">已送出 ({totalCount})</p>
          {canViewAll && (
            <Button
              type="button"
              variant="ghost"
              className="h-8 px-2 text-[11px] font-black text-primary-500 hover:text-primary-500/80"
              onClick={() => setShowAll(true)}
            >
              查看全部請求
            </Button>
          )}
        </div>
      )}
      {displayRequests.map(request => (
        <Card
          key={request.id}
          className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <UserAvatar
                nickname={request.recipient_nickname}
                avatarUrl={request.recipient_avatar_url}
                userId={request.recipient_id}
              />
              <div>
                <p className="text-sm font-black text-foreground">
                  {request.recipient_nickname || `使用者 ${request.recipient_id.slice(0, 8)}`}
                </p>
                <p className="text-[11px] text-muted-foreground">等待對方回覆</p>
              </div>
            </div>
            <span className="bg-slate-100 text-slate-700 text-[10px] px-2 py-1 rounded-full font-black">
              等待中
            </span>
          </div>
        </Card>
      ))}
    </div>
  )
}
