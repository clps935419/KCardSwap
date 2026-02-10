/**
 * ThreadsList Component
 *
 * Displays list of message threads for the current user
 */
'use client'

import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { UserAvatar } from '@/components/ui/user-avatar'
import type { ThreadResponse } from '@/shared/api/generated'
import {
  getMyProfileApiV1ProfileMeGetOptions,
  getMyThreadsApiV1ThreadsGetOptions,
} from '@/shared/api/generated/@tanstack/react-query.gen'

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes} 分鐘前`
  if (hours < 24) return `${hours} 小時前`
  return `${days} 天前`
}

export function ThreadsList() {
  const profileQuery = useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })
  const threadsQuery = useQuery({
    ...getMyThreadsApiV1ThreadsGetOptions(),
  })

  const currentUserId = profileQuery.data?.data?.user_id
  const threads = threadsQuery.data?.threads ?? []

  const resolvePeerData = (thread: ThreadResponse) => {
    if (!currentUserId) {
      return {
        peerId: thread.user_b_id,
        peerNickname: thread.user_b_nickname,
        peerAvatarUrl: thread.user_b_avatar_url,
      }
    }
    if (thread.user_a_id === currentUserId) {
      return {
        peerId: thread.user_b_id,
        peerNickname: thread.user_b_nickname,
        peerAvatarUrl: thread.user_b_avatar_url,
      }
    }
    return {
      peerId: thread.user_a_id,
      peerNickname: thread.user_a_nickname,
      peerAvatarUrl: thread.user_a_avatar_url,
    }
  }

  const resolveLastMessageText = (thread: ThreadResponse) => {
    const timestamp = thread.last_message_at || thread.updated_at || thread.created_at
    if (!timestamp) return '尚無訊息'
    return `更新於 ${formatTimeAgo(timestamp)}`
  }

  if (threadsQuery.isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (threadsQuery.error) {
    return <div className="text-center text-muted-foreground text-sm py-12">載入聊天時發生錯誤</div>
  }

  if (threads.length === 0) {
    return <div className="text-center text-muted-foreground text-sm py-12">目前沒有聊天</div>
  }

  return (
    <div className="space-y-2">
      {threads.map(thread => {
        const { peerId, peerNickname, peerAvatarUrl } = resolvePeerData(thread)
        const lastMessageText = resolveLastMessageText(thread)

        return (
          <Link key={thread.id} href={`/inbox/threads/${thread.id}`}>
            <Card className="p-4 rounded-2xl shadow-sm border border-border/30 flex items-center justify-between hover:bg-muted cursor-pointer transition-colors bg-card">
              <div className="flex items-center gap-3">
                <UserAvatar nickname={peerNickname} avatarUrl={peerAvatarUrl} userId={peerId} />
                <div>
                  <p className="text-sm font-black text-foreground">
                    {peerNickname || `使用者 ${peerId.slice(0, 8)}`}
                  </p>
                  <p className="text-[11px] text-muted-foreground">{lastMessageText}</p>
                </div>
              </div>
              <span className="text-muted-foreground/30 font-black">›</span>
            </Card>
          </Link>
        )
      })}
    </div>
  )
}
