/**
 * MessageList Component
 *
 * Displays messages in a thread
 */
'use client'

import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import type { ThreadMessageResponse } from '@/shared/api/generated'
import {
  getMyProfileApiV1ProfileMeGetOptions,
  getThreadMessagesApiV1ThreadsThreadIdMessagesGetOptions,
} from '@/shared/api/generated/@tanstack/react-query.gen'

interface MessageListProps {
  threadId: string
}

export function MessageList({ threadId }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const profileQuery = useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })
  const messagesQuery = useQuery({
    ...getThreadMessagesApiV1ThreadsThreadIdMessagesGetOptions({
      path: {
        thread_id: threadId,
      },
      query: {
        limit: 50,
        offset: 0,
      },
    }),
    enabled: !!threadId,
  })

  const currentUserId = profileQuery.data?.data?.user_id
  const messages = (messagesQuery.data?.messages ?? []) as ThreadMessageResponse[]

  useEffect(() => {
    // Scroll to bottom when messages change
    if (messages.length === 0) {
      return
    }
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  if (messagesQuery.isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (messagesQuery.error) {
    return <div className="text-center py-12 text-muted-foreground text-sm">載入訊息時發生錯誤</div>
  }

  if (messages.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground text-sm">
        <p>目前沒有訊息</p>
        <p className="text-[11px] mt-2">在下方開始對話</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {messages.map(message => {
        const isOwnMessage = !!currentUserId && message.sender_id === currentUserId

        return (
          <div
            key={message.id}
            className={cn('flex', isOwnMessage ? 'justify-end' : 'justify-start')}
          >
            <div
              className={cn(
                'max-w-[75%] rounded-2xl px-4 py-3',
                isOwnMessage
                  ? 'bg-slate-900 text-white'
                  : 'bg-card border border-border text-foreground'
              )}
            >
              <p className="text-sm font-bold">{message.content}</p>
              {message.post_id && (
                <p className="text-[10px] opacity-70 mt-1">引用貼文：{message.post_id}</p>
              )}
            </div>
          </div>
        )
      })}
      <div ref={messagesEndRef} />
    </div>
  )
}
