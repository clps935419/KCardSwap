/**
 * SendMessageForm Component - Form to send a message in a thread
 */
'use client'

import { Loader2 } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import { useSendMessage } from '@/features/inbox/hooks/useSendMessage'

interface SendMessageFormProps {
  threadId: string
}

interface SendMessageFormValues {
  content: string
}

export function SendMessageForm({ threadId }: SendMessageFormProps) {
  const { toast } = useToast()
  const { sendMessage, loading } = useSendMessage()
  const form = useForm<SendMessageFormValues>({
    defaultValues: {
      content: '',
    },
  })
  const content = form.watch('content')

  const handleSubmit = async (values: SendMessageFormValues) => {
    const trimmedContent = values.content.trim()
    if (!trimmedContent) {
      return
    }

    try {
      await sendMessage({
        threadId,
        content: trimmedContent,
      })
      form.reset({ content: '' })

      toast({
        title: '訊息已送出',
      })
    } catch (_error) {
      toast({
        title: '錯誤',
        description: '無法送出訊息',
        variant: 'destructive',
      })
    }
  }

  const onSubmit = form.handleSubmit(handleSubmit)

  return (
    <form onSubmit={onSubmit} className="flex gap-2">
      <Input
        placeholder="輸入訊息..."
        disabled={loading}
        className="flex-1 bg-muted/50 border-border rounded-2xl px-4 py-3"
        {...form.register('content')}
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            onSubmit()
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
