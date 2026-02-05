'use client'

import { useParams, useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { useToast } from '@/components/ui/use-toast'
import { PostImages } from '@/features/media/components/PostImages'
import { useToggleLike } from '@/features/posts/hooks/useToggleLike'
import { useCreateMessageRequest } from '@/features/inbox/hooks/useCreateMessageRequest'
import type { PostCategory } from '@/shared/api/generated'

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

export default function PostDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const postId = params.id as string
  const [messagingPost, setMessagingPost] = useState(false)

  // TODO: Implement usePost hook to fetch single post
  // For now using placeholder data
  const isLoading = false
  const error = null
  
  const post = {
    id: postId,
    owner_id: 'placeholder-owner-id',
    scope: 'global' as const,
    city_code: null,
    category: 'trade' as PostCategory,
    title: '徵求 BTS Jungkook 小卡',
    content: '我想用我的 IU 小卡交換 BTS Jungkook 的小卡。我有多個版本，歡迎聊聊交換細節。誠徵可信賴的交換夥伴！',
    idol: 'Jungkook',
    idol_group: 'BTS',
    status: 'open' as const,
    like_count: 5,
    liked_by_me: false,
    // Phase 9: Placeholder media IDs for demonstration (same as list page would show)
    // TODO: Replace with actual media_asset_ids from API when fetching real post data
    media_asset_ids: [
      'demo-media-1',
      'demo-media-2',
      'demo-media-3',
    ] as string[],
    expires_at: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }

  const { createRequest } = useCreateMessageRequest()
  const toggleLikeMutation = useToggleLike()

  const handleMessageAuthor = async () => {
    setMessagingPost(true)

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
    } catch (_err) {
      toast({
        title: '錯誤',
        description: '無法送出訊息請求，請稍後再試',
        variant: 'destructive',
      })
    } finally {
      setMessagingPost(false)
    }
  }

  const handleToggleLike = async () => {
    try {
      await toggleLikeMutation.mutateAsync(postId)
    } catch (_err) {
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

  if (error || !post) {
    return (
      <Card className="p-6 text-center max-w-2xl mx-auto">
        <p className="text-destructive">載入貼文時發生錯誤</p>
        <p className="mt-2 text-sm text-muted-foreground">
          {error instanceof Error ? error.message : '找不到此貼文'}
        </p>
        <Button onClick={() => router.push('/posts')} className="mt-4">
          返回貼文列表
        </Button>
      </Card>
    )
  }

  const isExpired = new Date(post.expires_at) < new Date()
  const isClosed = post.status === 'closed'
  const liked = post.liked_by_me ?? false
  const likeCount = post.like_count ?? 0

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      {/* Back button */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.back()} className="text-primary-500 font-black">
          ← 返回
        </Button>
      </div>

      {/* Post Card */}
      <Card className="p-6 rounded-2xl shadow-sm border border-border/30 bg-card">
        {/* Post Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-50 rounded-full flex items-center justify-center">
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
              className={`${CATEGORY_COLORS[post.category]} text-[10px] px-3 py-1 rounded-full font-black`}
            >
              {CATEGORY_LABELS[post.category]}
            </span>
            {post.scope === 'global' ? (
              <span className="bg-slate-900 text-white text-[10px] px-3 py-1 rounded-full font-black">
                全域
              </span>
            ) : (
              <span className="bg-accent text-primary-500 text-[10px] px-3 py-1 rounded-full font-black">
                城市 • {post.city_code}
              </span>
            )}
          </div>
        </div>

        {/* Status Badge */}
        {(isClosed || isExpired) && (
          <div className="mb-4">
            <span className="bg-muted text-muted-foreground text-xs px-3 py-1 rounded-full font-semibold">
              {isClosed ? '已關閉' : '已到期'}
            </span>
          </div>
        )}

        {/* Post Title */}
        <h1 className="text-xl font-black text-foreground mb-4 leading-relaxed">
          {post.title}
        </h1>

        {/* Idol Tags */}
        {(post.idol || post.idol_group) && (
          <div className="flex flex-wrap gap-2 mb-4">
            {post.idol_group && (
              <span className="bg-purple-100 text-purple-700 text-sm px-3 py-1 rounded-full font-semibold">
                {post.idol_group}
              </span>
            )}
            {post.idol && (
              <span className="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-full font-semibold">
                {post.idol}
              </span>
            )}
          </div>
        )}

        {/* Post Content */}
        <div className="mb-6 p-4 bg-muted/30 rounded-lg">
          <p className="text-base text-foreground leading-relaxed whitespace-pre-wrap">
            {post.content}
          </p>
        </div>

        {/* Phase 9: Display post images using signed read URLs */}
        {post.media_asset_ids && post.media_asset_ids.length > 0 && (
          <div className="mb-6">
            <PostImages mediaAssetIds={post.media_asset_ids} maxDisplay={4} />
          </div>
        )}

        {/* Post Meta */}
        <div className="mb-6 p-4 bg-muted/20 rounded-lg text-xs text-muted-foreground space-y-1">
          <p>📅 發布時間: {new Date(post.created_at).toLocaleString('zh-TW')}</p>
          <p>⏰ 到期時間: {new Date(post.expires_at).toLocaleString('zh-TW')}</p>
        </div>

        {/* Post Actions */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            size="sm"
            onClick={handleToggleLike}
            disabled={toggleLikeMutation.isPending}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${
              liked
                ? 'border-secondary-300 bg-secondary-50 text-secondary-900 hover:bg-secondary-50/80'
                : 'border-border bg-card text-muted-foreground hover:bg-muted'
            }`}
          >
            <span className="text-lg">{liked ? '💗' : '🤍'}</span>
            <span className="text-[12px] font-black">
              {liked ? '已讚' : '讚'} • {likeCount}
            </span>
          </Button>

          <Button
            variant="default"
            size="sm"
            onClick={handleMessageAuthor}
            disabled={messagingPost}
            className="px-5 py-2 rounded-xl bg-slate-900 text-white text-[12px] font-black shadow hover:bg-slate-800"
          >
            {messagingPost ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            私信作者
          </Button>
        </div>
      </Card>
    </div>
  )
}
