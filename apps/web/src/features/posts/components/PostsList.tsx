'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, Trash2 } from 'lucide-react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useMemo, useState } from 'react'
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
import { UserAvatar } from '@/components/ui/user-avatar'
import { useCreateMessageRequest } from '@/features/inbox/hooks/useCreateMessageRequest'
import { PostImages } from '@/features/media/components/PostImages'
import { useReadMediaUrls } from '@/features/media/hooks/useReadMediaUrls'
import { usePostsList } from '@/features/posts/hooks/usePostsList'
import { useToggleLike } from '@/features/posts/hooks/useToggleLike'
import type { PostCategory, PostResponse } from '@/shared/api/generated'
import {
  closePostApiV1PostsPostIdClosePostMutation,
  getPostApiV1PostsPostIdGetQueryKey,
  listPostsApiV1PostsGetQueryKey,
} from '@/shared/api/generated/@tanstack/react-query.gen'
import { useMyProfile } from '@/shared/api/hooks/profile'

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

const clampText = (value: string, maxLength: number) => {
  if (value.length <= maxLength) return value
  return `${value.slice(0, Math.max(0, maxLength - 1))}…`
}

export function PostsList() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { toast } = useToast()
  const city = searchParams.get('city') || undefined
  const category = searchParams.get('category') as PostCategory | undefined
  const [messagingPostId, setMessagingPostId] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<PostResponse | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = usePostsList({
    cityCode: city === 'ALL' ? undefined : city,
    category,
  })
  const { data: myProfileData } = useMyProfile()
  const myUserId = myProfileData?.data?.user_id
  const posts = data?.data?.posts ?? []

  const postListMediaAssetIds = useMemo(() => {
    return Array.from(
      new Set(
        posts
          .map(post => post.media_asset_ids?.[0])
          .filter((mediaId): mediaId is string => Boolean(mediaId))
      )
    )
  }, [posts])

  const readMediaUrlsQuery = useReadMediaUrls(postListMediaAssetIds, {
    enabled: posts.length > 0,
  })
  const preloadedMediaUrls = readMediaUrlsQuery.data?.data?.urls ?? {}

  const { createRequest } = useCreateMessageRequest()
  const toggleLikeMutation = useToggleLike()
  const closePostMutation = useMutation({
    ...closePostApiV1PostsPostIdClosePostMutation(),
    onMutate: async variables => {
      await queryClient.cancelQueries({
        queryKey: listPostsApiV1PostsGetQueryKey(),
        exact: false,
      })

      const previous = queryClient.getQueriesData({
        queryKey: listPostsApiV1PostsGetQueryKey(),
        exact: false,
      })

      queryClient.setQueriesData(
        { queryKey: listPostsApiV1PostsGetQueryKey(), exact: false },
        data => {
          if (!data || typeof data !== 'object') return data
          const typed = data as { data?: { posts?: PostResponse[] } }
          const nextPosts = typed.data?.posts?.filter(post => post.id !== variables.path.post_id)
          return {
            ...typed,
            data: {
              ...typed.data,
              posts: nextPosts,
            },
          }
        }
      )

      setDeleteTarget(null)

      return { previous }
    },
    onError: (_error, _variables, context) => {
      context?.previous?.forEach(([queryKey, data]) => {
        queryClient.setQueryData(queryKey, data)
      })
      toast({
        title: '刪除失敗',
        description: '無法刪除貼文，請稍後再試',
        variant: 'destructive',
      })
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: listPostsApiV1PostsGetQueryKey(),
        exact: false,
      })
      queryClient.invalidateQueries({
        queryKey: getPostApiV1PostsPostIdGetQueryKey({
          path: {
            post_id: variables.path.post_id,
          },
        }),
      })
      toast({
        title: '已刪除',
        description: '貼文已關閉並從列表移除',
      })
      setDeleteTarget(null)
    },
  })

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
    } catch (_err) {
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
    } catch (_err) {
      toast({
        title: '錯誤',
        description: '無法更新按讚狀態，請稍後再試',
        variant: 'destructive',
      })
    }
  }

  const handleConfirmDelete = async () => {
    if (!deleteTarget) return
    try {
      await closePostMutation.mutateAsync({
        path: {
          post_id: deleteTarget.id,
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
      <div className="space-y-4">
        {[...Array(6)].map((_, i) => (
          <Card
            key={`post-skeleton-${i}`}
            className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Skeleton className="h-9 w-9 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-3 w-28" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Skeleton className="h-4 w-12 rounded-full" />
                <Skeleton className="h-4 w-16 rounded-full" />
              </div>
            </div>

            <Skeleton className="h-4 w-4/5" />
            <Skeleton className="mt-2 h-24 w-full rounded-lg" />

            <div className="mt-3 flex items-center justify-between">
              <Skeleton className="h-8 w-22 rounded-xl" />
              <Skeleton className="h-8 w-22 rounded-xl" />
            </div>
          </Card>
        ))}
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

  if (posts.length === 0) {
    return <div className="text-center text-muted-foreground text-sm py-12">沒有符合篩選的貼文</div>
  }

  return (
    <div className="space-y-4">
      {posts.map((post: PostResponse) => {
        const liked = post.liked_by_me ?? false
        const likeCount = post.like_count ?? 0
        const isOwner = !!myUserId && post.owner_id === myUserId
        const canMessage = !isOwner && (post.can_message ?? false)
        const canDelete = isOwner && post.status !== 'closed'

        return (
          <Card key={post.id} className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card">
            {/* Post Header */}
            <div className="flex items-center justify-between mb-2">
              <Link
                href={`/users/${post.owner_id}`}
                className="flex items-center gap-2 hover:opacity-80 transition-opacity"
              >
                <UserAvatar
                  nickname={post.owner_nickname}
                  avatarUrl={post.owner_avatar_url}
                  userId={post.owner_id}
                  size="sm"
                  fallback={<span>👤</span>}
                />
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
                <span
                  className={`${CATEGORY_COLORS[post.category as PostCategory]} text-[10px] px-2 py-1 rounded-full font-black`}
                >
                  {CATEGORY_LABELS[post.category as PostCategory]}
                </span>
                {post.scope === 'global' ? (
                  <span className="bg-slate-900 text-white text-[10px] px-2 py-1 rounded-full font-black">
                    全部
                  </span>
                ) : (
                  <span className="bg-accent text-primary-500 text-[10px] px-2 py-1 rounded-full font-black">
                    城市 • {post.city_code}
                  </span>
                )}
              </div>
            </div>

            {/* Post Content */}
            <Button
              type="button"
              variant="ghost"
              onClick={() => router.push(`/posts/${post.id}`)}
              className="w-full h-auto p-0 text-left mt-1 flex flex-col items-start group"
            >
              <p className="text-sm text-foreground/90 font-bold leading-relaxed group-hover:underline">
                {post.title}
              </p>

              {/* Phase 9: Display post images using signed read URLs */}
              {post.media_asset_ids && post.media_asset_ids.length > 0 ? (
                <div className="mt-2 w-full flex justify-center">
                  <PostImages
                    mediaAssetIds={post.media_asset_ids}
                    maxDisplay={1}
                    preloadedUrls={preloadedMediaUrls}
                    isPreloadedUrlsLoading={readMediaUrlsQuery.isLoading}
                    hasPreloadedUrlsError={!!readMediaUrlsQuery.error}
                  />
                </div>
              ) : (
                <div className="mt-2 text-[11px] text-muted-foreground">無附圖</div>
              )}

              <div className="mt-2 flex items-center justify-end text-[11px]">
                <span className="font-black text-primary-500">查看貼文 ›</span>
              </div>
            </Button>

            {/* Post Actions */}
            <div className="mt-3 flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleToggleLike(post.id)}
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

              {canMessage && (
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => handleMessageAuthor(post)}
                  disabled={messagingPostId === post.id}
                  className="h-9 px-4 rounded-xl bg-slate-900 text-white text-[11px] font-black shadow hover:bg-slate-800"
                >
                  {messagingPostId === post.id ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : null}
                  私信作者
                </Button>
              )}
              {canDelete && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setDeleteTarget(post)}
                  className="h-9 px-4 rounded-xl text-[11px] font-black text-destructive border-destructive/40 hover:bg-destructive/10"
                >
                  <Trash2 className="h-4 w-4" />
                  刪除
                </Button>
              )}
            </div>
          </Card>
        )
      })}

      <Dialog open={!!deleteTarget} onOpenChange={open => !open && setDeleteTarget(null)}>
        <DialogContent className="max-w-sm rounded-3xl border border-border/60 bg-card/95 p-6">
          <DialogHeader className="text-center">
            <DialogTitle className="text-lg font-black leading-snug">
              刪除「
              {clampText(deleteTarget?.title || '這則貼文', 22)}」？
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
              onClick={() => setDeleteTarget(null)}
              className="h-11 w-full rounded-2xl text-sm font-black"
            >
              取消
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
