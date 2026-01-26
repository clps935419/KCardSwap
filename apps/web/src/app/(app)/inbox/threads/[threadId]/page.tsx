/**
 * Thread Page - Shows messages in a conversation thread
 */
'use client'

import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { MessageList } from '@/features/inbox/components/MessageList'
import { SendMessageForm } from '@/features/inbox/components/SendMessageForm'

export default function ThreadPage() {
  const params = useParams()
  const router = useRouter()
  const threadId = params.threadId as string

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col max-w-2xl mx-auto">
      {/* Header */}
      <div className="px-6 py-3 bg-card border-b border-border/30 flex items-center justify-between">
        <button
          onClick={() => router.push('/inbox')}
          className="text-[11px] font-black text-primary-500 hover:text-primary-500/80"
        >
          ← 返回信箱
        </button>
        <p className="text-[11px] text-muted-foreground font-black">唯一對話規則（per pair）</p>
      </div>

      {/* Messages */}
      <div className="flex-1 px-6 py-4 overflow-y-auto">
        <MessageList threadId={threadId} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 bg-card border-t border-border/30">
        <SendMessageForm threadId={threadId} />
        <p className="text-[10px] text-muted-foreground mt-2">
          示意：訊息可選帶 post_id 引用（此頁不再額外演示）
        </p>
      </div>
    </div>
  )
}
