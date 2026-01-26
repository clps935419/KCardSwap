'use client'

import { Loader2 } from 'lucide-react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { useToast } from '@/components/ui/use-toast'
import { useCreateMessageRequest } from '@/features/inbox/hooks/useCreateMessageRequest'
import { usePostsList } from '@/features/posts/hooks/usePostsList'
import { useToggleLike } from '@/features/posts/hooks/useToggleLike'
import type { PostCategory, PostResponse } from '@/shared/api/generated'

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes} 分`
  if (hours < 24) return `${hours} 小時`
  return `${days} 天`
}

const CATEGORY_LABELS: Record<PostCategory, string> = {
  trade: '求換',
  giveaway: '送出',
  group: '揪團',
  showcase: '展示',
  help: '求助',
  announcement: '公告',
}

const CATEGORY_COLORS: Record<PostCategory, string> = {
  trade: 'bg-rose-50 text-rose-700',
  giveaway: 'bg-emerald-50 text-emerald-700',
  group: 'bg-amber-50 text-amber-700',
  showcase: 'bg-primary-50 text-primary-500',
  help: 'bg-slate-100 text-slate-700',
  announcement: 'bg-purple-50 text-purple-700',
}

export function PostsList() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { toast } = useToast()
  const city = searchParams.get('city') || undefined
  const category = searchParams.get('category') as PostCategory | undefined
  const [messagingPostId, setMessagingPostId] = useState<string | null>(null)

  const { data, isLoading, error } = usePostsList({
    cityCode: city === 'ALL' ? undefined : city,
    category,
  })

  const { createRequest, loading: creatingRequest } = useCreateMessageRequest()
  const toggleLikeMutation = useToggleLike()

  const handleMessageAuthor = async (post: PostResponse) => {
    setMessagingPostId(post.id)

    try {
      await createRequest({
        recipientId: post.owner_id,
        initialMessage: `Hi! I'm interested in your post "${post.title}"`,
        postId: post.id,
      })

      toast({
        title: '訊息請求已送出',
        description: '作者將會在信箱中看到您的訊息',
      })

      router.push('/inbox?tab=requests')
    } catch (err) {
      toast({
        title: '錯誤',
        description: '無法送出訊息請求，請稍後再試',
        variant: 'destructive',
      })
    } finally {
      setMessagingPostId(null)
    }
  }

  const handleToggleLike = async (postId: string) => {
    try {
      await toggleLikeMutation.mutateAsync(postId)
    } catch (err) {
      toast({
        title: '錯誤',
        description: '無法更新按讚狀態，請稍後再試',
        variant: 'destructive',
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner className="h-8 w-8" />
      </div>
    )
  }

  if (error) {
    return (
      <Card className="p-6 text-center">
        <p className="text-destructive">載入貼文時發生錯誤</p>
        <p className="mt-2 text-sm text-muted-foreground">
          {error instanceof Error ? error.message : '請稍後再試'}
        </p>
      </Card>
    )
  }

  const posts = data?.data?.posts || []

  if (posts.length === 0) {
    return <div className="text-center text-muted-foreground text-sm py-12">沒有符合篩選的貼文</div>
  }

  return (
    <div className="space-y-4">
      {posts.map((post: PostResponse) => {
        const liked = post.liked_by_me ?? false
        const likeCount = post.like_count ?? 0

        return (
          <Card key={post.id} className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card">
            {/* Post Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary-50 rounded-full flex items-center justify-center">
                  👤
                </div>
                <div>
                  <p className="text-sm font-black text-foreground">
                    User {post.owner_id.slice(0, 8)}
                  </p>
                  <p className="text-[10px] text-muted-foreground font-bold uppercase">
                    {formatTimeAgo(post.created_at)} • {post.id.slice(0, 8)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`${CATEGORY_COLORS[post.category as PostCategory]} text-[10px] px-2 py-1 rounded-full font-black`}
                >
                  {CATEGORY_LABELS[post.category as PostCategory]}
                </span>
                {post.scope === 'global' ? (
                  <span className="bg-slate-900 text-white text-[10px] px-2 py-1 rounded-full font-black">
                    全域
                  </span>
                ) : (
                  <span className="bg-accent text-primary-500 text-[10px] px-2 py-1 rounded-full font-black">
                    城市 • {post.city_code}
                  </span>
                )}
              </div>
            </div>

            {/* Post Content */}
            <button
              onClick={() => router.push(`/posts/${post.id}`)}
              className="w-full text-left mt-1 group"
            >
              <p className="text-sm text-foreground/90 font-bold leading-relaxed group-hover:underline">
                {post.title}
              </p>
              <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                <span>無附圖</span>
                <span className="font-black text-primary-500">查看貼文 ›</span>
              </div>
            </button>

            {/* Post Actions */}
            <div className="mt-3 flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleToggleLike(post.id)}
                disabled={toggleLikeMutation.isPending}
                className={`flex items-center gap-2 px-3 py-2 rounded-xl border transition-all ${
                  liked
                    ? 'border-secondary-300 bg-secondary-50 text-secondary-900 hover:bg-secondary-50/80'
                    : 'border-border bg-card text-muted-foreground hover:bg-muted'
                }`}
              >
                <span className="text-base">{liked ? '💗' : '🤍'}</span>
                <span className="text-[11px] font-black">
                  {liked ? '已讚' : '讚'} • {likeCount}
                </span>
              </Button>

              <Button
                variant="default"
                size="sm"
                onClick={() => handleMessageAuthor(post)}
                disabled={messagingPostId === post.id}
                className="px-4 py-2 rounded-xl bg-slate-900 text-white text-[11px] font-black shadow hover:bg-slate-800"
              >
                {messagingPostId === post.id ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                私信作者
              </Button>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
