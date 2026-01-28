/**
 * SendMessageForm Component - Form to send a message in a thread
 */
'use client'

import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'

interface SendMessageFormProps {
  threadId: string
}

export function SendMessageForm({ threadId }: SendMessageFormProps) {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!content.trim()) {
      return
    }

    setLoading(true)
    try {
      // TODO: Call send message endpoint using generated SDK
      // await sendMessage({
      //   thread_id: threadId,
      //   content: content.trim(),
      // });

      setContent('')

      // Refresh messages
      // queryClient.invalidateQueries(['thread-messages', threadId]);

      toast({
        title: '訊息已送出',
      })
    } catch (_error) {
      toast({
        title: '錯誤',
        description: '無法送出訊息',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        placeholder="輸入訊息..."
        value={content}
        onChange={e => setContent(e.target.value)}
        disabled={loading}
        className="flex-1 bg-muted/50 border-border rounded-2xl px-4 py-3"
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
          }
        }}
      />
      <Button
        type="submit"
        disabled={loading || !content.trim()}
        className="w-14 rounded-2xl bg-slate-900 text-white font-black hover:bg-slate-800"
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : '送'}
      </Button>
    </form>
  )
}
