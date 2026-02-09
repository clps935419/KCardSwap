'use client'

import { MessageRequestsList } from '@/features/inbox/components/MessageRequestsList'
import { SentRequestsList } from '@/features/inbox/components/SentRequestsList'
import { ThreadsList } from '@/features/inbox/components/ThreadsList'

export default function InboxPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <MessageRequestsList limit={3} showHeader hideEmpty />
      <SentRequestsList limit={3} showHeader hideEmpty />

      <div className="space-y-3">
        <p className="text-sm font-black text-foreground">聊天</p>
        <ThreadsList />
      </div>
    </div>
  )
}
