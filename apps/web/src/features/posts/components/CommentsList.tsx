'use client'

import { Loader2 } from 'lucide-react'
import Image from 'next/image'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import type { CommentResponse } from '@/shared/api/generated'

interface CommentsListProps {
  comments: (CommentResponse & { pending?: boolean })[]
  isLoading: boolean
}

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '剛剛'
  if (minutes < 60) return `${minutes} 分鐘前`
  if (hours < 24) return `${hours} 小時前`
  return `${days} 天前`
}

export function CommentsList({ comments, isLoading }: CommentsListProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner className="h-6 w-6" />
      </div>
    )
  }

  if (!comments || comments.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground text-sm">尚無留言，說點什麼吧</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {comments.map(comment => {
        const isPending = comment.pending || false

        return (
          <Card
            key={comment.id.toString()}
            className={`p-4 ${
              isPending ? 'bg-muted/50 opacity-70 border-dashed' : 'bg-card border-border/30'
            }`}
          >
            <div className="flex items-start gap-3">
              {/* Avatar */}
              <div className="w-8 h-8 bg-primary-50 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden">
                {comment.user_avatar_url ? (
                  <Image
                    src={comment.user_avatar_url}
                    alt={comment.user_nickname || '使用者'}
                    width={32}
                    height={32}
                    sizes="32px"
                    unoptimized
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-lg">👤</span>
                )}
              </div>

              {/* Comment content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold text-foreground">
                    {comment.user_nickname || `使用者 ${comment.user_id.toString().slice(0, 8)}`}
                  </span>
                  <span className="text-[10px] text-muted-foreground">
                    {formatTimeAgo(comment.created_at)}
                  </span>
                  {isPending && (
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <Loader2 className="h-3 w-3 animate-spin" />
                      送出中…
                    </span>
                  )}
                </div>
                <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                  {comment.content}
                </p>
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
