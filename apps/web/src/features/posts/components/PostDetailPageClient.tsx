'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, Trash2 } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/components/ui/use-toast'
import { useCreateMessageRequest } from '@/features/inbox/hooks/useCreateMessageRequest'
import { PostImages } from '@/features/media/components/PostImages'
import { CommentForm } from '@/features/posts/components/CommentForm'
import { CommentsList } from '@/features/posts/components/CommentsList'
import { useCreateComment, usePostComments } from '@/features/posts/hooks/useComments'
import { usePost } from '@/features/posts/hooks/usePost'
import { useToggleLike } from '@/features/posts/hooks/useToggleLike'
import type { PostCategory } from '@/shared/api/generated'
import {
  closePostApiV1PostsPostIdClosePostMutation,
  getPostApiV1PostsPostIdGetQueryKey,
  listPostsApiV1PostsGetQueryKey,
} from '@/shared/api/generated/@tanstack/react-query.gen'
import { useMyProfile } from '@/shared/api/hooks/profile'

const BLUR_DATA_URL =
  'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNlZWVlZWUiLz48L3N2Zz4='

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

const clampText = (value: string, maxLength: number) => {
  if (value.length <= maxLength) return value
  return `${value.slice(0, Math.max(0, maxLength - 1))}…`
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

interface PostDetailPageClientProps {
  postId: string
}

export function PostDetailPageClient({ postId }: PostDetailPageClientProps) {
  const router = useRouter()
  const { toast } = useToast()
  const [messagingPost, setMessagingPost] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = usePost(postId)
  const post = data?.data
  const { data: myProfileData } = useMyProfile()
  const myUserId = myProfileData?.data?.user_id

  const { createRequest } = useCreateMessageRequest()
  const toggleLikeMutation = useToggleLike()
  const closePostMutation = useMutation({
    ...closePostApiV1PostsPostIdClosePostMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: listPostsApiV1PostsGetQueryKey(),
        exact: false,
      })
      queryClient.invalidateQueries({
        queryKey: getPostApiV1PostsPostIdGetQueryKey({
          path: {
            post_id: postId,
          },
        }),
      })
      toast({
        title: '已刪除',
        description: '貼文已關閉並從列表移除',
      })
      setDeleteDialogOpen(false)
      router.back()
    },
  })

  // Comments functionality
  const { data: commentsData, isLoading: commentsLoading } = usePostComments(postId, {
    enabled: !!post, // Only fetch comments if post is loaded
  })
  const commentsResponse = commentsData?.data
  const comments = commentsResponse?.comments || []
  const createCommentMutation = useCreateComment(postId)

  const handleCreateComment = async (content: string) => {
    try {
      await createCommentMutation.mutateAsync(content)
    } catch (err) {
      // Error handling is done in the mutation's onError callback
      console.error('Error creating comment:', err)
    }
  }

  const handleMessageAuthor = async () => {
    if (!post) return

    setMessagingPost(true)

    try {
      await createRequest({
        recipientId: post.owner_id.toString(),
        initialMessage: `Hi! I'm interested in your post "${post.title}"`,
        postId: post.id.toString(),
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

  const handleConfirmDelete = async () => {
    try {
      await closePostMutation.mutateAsync({
        path: {
          post_id: postId,
        },
      })
    } catch (_err) {
      toast({
        title: '刪除失敗',
        description: '無法刪除貼文，請稍後再試',
        variant: 'destructive',
      })
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-20 rounded-xl" />
        </div>
        <Card className="p-6 rounded-2xl shadow-sm border border-border/30 bg-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-24" />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Skeleton className="h-5 w-14 rounded-full" />
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>
          </div>

          <div className="mb-3 flex items-center gap-2">
            <Skeleton className="h-6 w-20 rounded-full" />
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>
          <Skeleton className="h-6 w-4/5 mb-3" />
          <Skeleton className="h-6 w-2/3 mb-4" />
          <div className="mb-6 space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
          <Skeleton className="h-[180px] w-full rounded-2xl mb-6" />

          <div className="mb-6 space-y-2">
            <Skeleton className="h-3 w-2/3" />
            <Skeleton className="h-3 w-1/2" />
          </div>

          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-24 rounded-xl" />
            <Skeleton className="h-8 w-24 rounded-xl" />
          </div>
        </Card>

        <Card className="p-6 rounded-2xl shadow-sm border border-border/30 bg-card">
          <Skeleton className="h-5 w-28 mb-4" />
          <div className="mb-6 space-y-2">
            <Skeleton className="h-10 w-full rounded-xl" />
            <Skeleton className="h-10 w-24 rounded-xl" />
          </div>
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={`comment-skeleton-${i}`} className="flex items-start gap-3">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-4/5" />
                </div>
              </div>
            ))}
          </div>
        </Card>
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
  const isOwner = !!myUserId && post.owner_id === myUserId
  const canMessage = !isOwner && (post.can_message ?? false)
  const canDelete = isOwner && !isClosed
  const category = post.category as PostCategory
  const categoryLabel = CATEGORY_LABELS[category] ?? post.category
  const categoryColor = CATEGORY_COLORS[category] ?? 'bg-muted text-muted-foreground'

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      {/* Back button */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="text-primary-500 font-black"
        >
          ← 返回
        </Button>
      </div>

      {/* Post Card */}
      <Card className="p-6 rounded-2xl shadow-sm border border-border/30 bg-card">
        {/* Post Header */}
        <div className="flex items-center justify-between mb-4">
          <Link 
            href={`/users/${post.owner_id}`}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
          >
            <div className="w-10 h-10 bg-primary-50 rounded-full flex items-center justify-center overflow-hidden">
              {post.owner_avatar_url ? (
                <Image
                  src={post.owner_avatar_url}
                  alt={post.owner_nickname || '使用者'}
                  width={40}
                  height={40}
                  sizes="40px"
                  unoptimized
                  placeholder="blur"
                  blurDataURL={BLUR_DATA_URL}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-xl">👤</span>
              )}
            </div>
            <div>
              <p className="text-sm font-black text-foreground">
                {post.owner_nickname || `使用者 ${post.owner_id.slice(0, 8)}`}
              </p>
              <p className="text-[10px] text-muted-foreground font-bold uppercase">
                {formatTimeAgo(post.created_at)} • {post.id.slice(0, 8)}
              </p>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <span className={`${categoryColor} text-[10px] px-3 py-1 rounded-full font-black`}>
              {categoryLabel}
            </span>
            {post.scope === 'global' ? (
              <span className="bg-slate-900 text-white text-[10px] px-3 py-1 rounded-full font-black">
                全部
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
        <h1 className="text-xl font-black text-foreground mb-4 leading-relaxed">{post.title}</h1>

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
        <div className="mb-4 bg-muted/30 rounded-lg">
          <p className="text-base text-foreground leading-relaxed whitespace-pre-wrap">
            {post.content}
          </p>
        </div>

        {/* Phase 9: Display post images using signed read URLs */}
        {post.media_asset_ids && post.media_asset_ids.length > 0 && (
          <div className="mb-4 flex justify-center">
            <PostImages mediaAssetIds={post.media_asset_ids} maxDisplay={4} />
          </div>
        )}

        {/* Post Meta */}
        <div className="mb-4 bg-muted/20 rounded-lg text-xs text-muted-foreground space-y-1">
          <p>📅 發布時間: {new Date(post.created_at).toLocaleString('zh-TW')}</p>
          <p>⏰ 到期時間: {new Date(post.expires_at).toLocaleString('zh-TW')}</p>
        </div>

        {/* Post Actions */}
        <div className="flex items-center justify-between gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleToggleLike}
            disabled={toggleLikeMutation.isPending}
            className={`flex h-9 items-center gap-2 px-4 rounded-xl text-[11px] font-black leading-none border transition-all ${
              liked
                ? 'border-secondary-300 bg-secondary-50 text-secondary-900 hover:bg-secondary-50/80'
                : 'border-border bg-card text-muted-foreground hover:bg-muted'
            }`}
          >
            <span className="text-base leading-none">{liked ? '💗' : '🤍'}</span>
            <span className="leading-none">
              {liked ? '已讚' : '讚'} • {likeCount}
            </span>
          </Button>
          <div className="flex items-center gap-2">
            {canMessage && (
              <Button
                variant="default"
                size="sm"
                onClick={handleMessageAuthor}
                disabled={messagingPost}
                className="h-9 px-4 rounded-xl bg-slate-900 text-white text-[11px] font-black shadow hover:bg-slate-800"
              >
                {messagingPost ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                私信作者
              </Button>
            )}
            {canDelete && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setDeleteDialogOpen(true)}
                className="h-9 px-4 rounded-xl text-[11px] font-black text-destructive border-destructive/40 hover:bg-destructive/10"
              >
                <Trash2 className="h-4 w-4" />
                刪除
              </Button>
            )}
          </div>
        </div>
      </Card>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="max-w-sm rounded-3xl border border-border/60 bg-card/95 p-6">
          <DialogHeader className="text-center">
            <DialogTitle className="text-lg font-black leading-snug">
              刪除「{clampText(post.title, 22)}」？
            </DialogTitle>
          </DialogHeader>
          <DialogFooter className="flex-col gap-2 sm:flex-col sm:space-x-0">
            <Button
              type="button"
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={closePostMutation.isPending}
              className="h-11 w-full rounded-2xl text-sm font-black"
            >
              {closePostMutation.isPending ? '刪除中...' : '確認刪除'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              className="h-11 w-full rounded-2xl text-sm font-black"
            >
              取消
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Comments Section */}
      <Card className="p-6 rounded-2xl shadow-sm border border-border/30 bg-card">
        <h2 className="text-lg font-black text-foreground mb-4">
          留言 ({commentsData?.data?.total || 0})
        </h2>

        {/* Comment Form - Only show if user is authenticated */}
        <div className="mb-6">
          <CommentForm
            onSubmit={handleCreateComment}
            isSubmitting={createCommentMutation.isPending}
            disabled={false} // User must be logged in to see this page
          />
        </div>

        {/* Comments List */}
        <CommentsList comments={comments} isLoading={commentsLoading} />
      </Card>
    </div>
  )
}
