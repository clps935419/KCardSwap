/**
 * ThreadsList Component
 *
 * Displays list of message threads for the current user
 */
'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Card } from '@/components/ui/card'

// TODO: Replace with generated SDK types after OpenAPI generation
interface MessageThread {
  id: string
  user_a_id: string
  user_b_id: string
  created_at: string
  updated_at: string
  last_message_at?: string
  last_message?: string
  peer_name?: string
}

export function ThreadsList() {
  const [threads, _setThreads] = useState<MessageThread[]>([])

  // TODO: Replace with generated SDK hook
  // const { data, isLoading } = useGetMyThreads();

  if (threads.length === 0) {
    return <div className="text-center text-muted-foreground text-sm py-12">目前沒有聊天</div>
  }

  return (
    <div className="space-y-2">
      {threads.map(thread => (
        <Link key={thread.id} href={`/inbox/threads/${thread.id}`}>
          <Card className="p-4 rounded-2xl shadow-sm border border-border/30 flex items-center justify-between hover:bg-muted cursor-pointer transition-colors bg-card">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-50 rounded-2xl flex items-center justify-center">
                💬
              </div>
              <div>
                <p className="text-sm font-black text-foreground">
                  {thread.peer_name || `User ${thread.user_b_id.slice(0, 8)}`}
                </p>
                <p className="text-[11px] text-muted-foreground">
                  {thread.last_message || '無訊息'}
                </p>
              </div>
            </div>
            <span className="text-muted-foreground/30 font-black">›</span>
          </Card>
        </Link>
      ))}
    </div>
  )
}
