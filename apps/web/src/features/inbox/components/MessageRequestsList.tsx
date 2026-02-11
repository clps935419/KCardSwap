/**
 * MessageRequestsList Component
 *
 * Displays pending message requests for the current user
 */

'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'
import { UserAvatar } from '@/components/ui/user-avatar'
import type { MessageRequestResponse } from '@/shared/api/generated'
import {
  acceptMessageRequestApiV1MessageRequestsRequestIdAcceptPostMutation,
  declineMessageRequestApiV1MessageRequestsRequestIdDeclinePostMutation,
  getMyMessageRequestsApiV1MessageRequestsInboxGetOptions,
  getMyThreadsApiV1ThreadsGetQueryKey,
} from '@/shared/api/generated/@tanstack/react-query.gen'

interface MessageRequestsListProps {
  requests?: MessageRequestResponse[]
  error?: unknown
  limit?: number
  showHeader?: boolean
  hideEmpty?: boolean
}

export function MessageRequestsList({
  requests: requestsProp,
  error,
  limit,
  showHeader,
  hideEmpty,
}: MessageRequestsListProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [processingId, setProcessingId] = useState<string | null>(null)
  const [processingAction, setProcessingAction] = useState<'accept' | 'decline' | null>(null)
  const [showAll, setShowAll] = useState(false)

  const requestsQueryOptions = getMyMessageRequestsApiV1MessageRequestsInboxGetOptions({
    query: {
      status_filter: 'pending',
    },
  })
  const requests = requestsProp ?? []

  const acceptMutation = useMutation({
    ...acceptMessageRequestApiV1MessageRequestsRequestIdAcceptPostMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: requestsQueryOptions.queryKey })
      queryClient.invalidateQueries({ queryKey: getMyThreadsApiV1ThreadsGetQueryKey() })
    },
  })

  const declineMutation = useMutation({
    ...declineMessageRequestApiV1MessageRequestsRequestIdDeclinePostMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: requestsQueryOptions.queryKey })
    },
  })

  const handleAccept = async (requestId: string) => {
    setProcessingId(requestId)
    setProcessingAction('accept')
    try {
      await acceptMutation.mutateAsync({
        path: {
          request_id: requestId,
        },
      })
      toast({
        title: '已接受',
        description: '已建立對話，已移到「聊天」',
      })
    } catch (_error) {
      toast({
        title: '錯誤',
        description: '無法接受請求',
        variant: 'destructive',
      })
    } finally {
      setProcessingId(null)
      setProcessingAction(null)
    }
  }

  const handleDecline = async (requestId: string) => {
    setProcessingId(requestId)
    setProcessingAction('decline')
    try {
      await declineMutation.mutateAsync({
        path: {
          request_id: requestId,
        },
      })
      toast({
        title: '已拒絕',
        description: '此請求已標記為「拒絕」',
      })
    } catch (_error) {
      toast({
        title: '錯誤',
        description: '無法拒絕請求',
        variant: 'destructive',
      })
    } finally {
      setProcessingId(null)
      setProcessingAction(null)
    }
  }

  if (error) {
    return <div className="text-center text-muted-foreground text-sm py-12">載入請求時發生錯誤</div>
  }

  if (requests.length === 0) {
    if (hideEmpty) {
      return null
    }
    return (
      <div className="text-center text-muted-foreground text-sm py-12 space-y-3">
        <p>目前沒有請求</p>
        <Button asChild variant="outline" className="h-10 rounded-2xl font-black">
          <Link href="/posts">去貼文看看</Link>
        </Button>
      </div>
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
          <p className="text-sm font-black text-foreground">請求 ({totalCount})</p>
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
                nickname={request.sender_nickname}
                avatarUrl={request.sender_avatar_url}
                userId={request.sender_id}
              />
              <div>
                <p className="text-sm font-black text-foreground">
                  {request.sender_nickname || `使用者 ${request.sender_id.slice(0, 8)}`}
                </p>
              </div>
            </div>
            <span className="bg-amber-50 text-amber-700 text-[10px] px-2 py-1 rounded-full font-black">
              待處理
            </span>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <Button
              onClick={() => handleAccept(request.id)}
              disabled={processingId !== null}
              className="h-11 rounded-2xl bg-slate-900 text-white font-black hover:bg-slate-800"
            >
              {processingId === request.id && processingAction === 'accept' ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                '接受'
              )}
            </Button>
            <Button
              variant="outline"
              onClick={() => handleDecline(request.id)}
              disabled={processingId !== null}
              className="h-11 rounded-2xl border border-border bg-card font-black hover:bg-muted"
            >
              {processingId === request.id && processingAction === 'decline' ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                '拒絕'
              )}
            </Button>
          </div>
        </Card>
      ))}
    </div>
  )
}
