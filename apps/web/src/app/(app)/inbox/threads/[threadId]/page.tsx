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
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => router.push('/inbox')}
          className="text-[11px] font-black text-primary-500 hover:text-primary-500/80"
        >
          ← 返回信箱
        </Button>
        <p className="text-[11px] text-muted-foreground font-black">這是你和對方的專屬對話</p>
      </div>

      {/* Messages */}
      <div className="flex-1 px-6 py-4 overflow-y-auto">
        <MessageList threadId={threadId} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 bg-card border-t border-border/30">
        <SendMessageForm threadId={threadId} />
        <p className="text-[10px] text-muted-foreground mt-2">
          需要的話可附上貼文連結，對方更好理解你的需求
        </p>
      </div>
    </div>
  )
}
