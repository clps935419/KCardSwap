'use client'

import { useSearchParams } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { usePostsList } from '@/features/posts/hooks/usePostsList'
import type { PostCategory, PostResponse } from '@/shared/api/generated'

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

const CATEGORY_LABELS: Record<PostCategory, string> = {
  trade: '交換',
  giveaway: '贈送',
  group: '揪團',
  showcase: '展示',
  help: '求助',
  announcement: '公告',
}

export function PostsList() {
  const searchParams = useSearchParams()
  const city = searchParams.get('city') || undefined
  const category = searchParams.get('category') as PostCategory | undefined

  const { data, isLoading, error } = usePostsList({
    cityCode: city === 'global' ? undefined : city,
    category,
  })

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
    return (
      <Card className="p-12 text-center">
        <p className="text-muted-foreground">目前沒有貼文</p>
        <p className="mt-2 text-sm text-muted-foreground">成為第一個發文的人吧！</p>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {posts.map((post: PostResponse) => (
        <Card key={post.id} className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                  {CATEGORY_LABELS[post.category as PostCategory]}
                </span>
                {post.scope === 'city' && post.city_code && (
                  <span className="rounded-full bg-secondary px-2 py-1 text-xs font-medium">
                    {post.city_code}
                  </span>
                )}
                {post.scope === 'global' && (
                  <span className="rounded-full bg-secondary px-2 py-1 text-xs font-medium">
                    全域
                  </span>
                )}
              </div>
              <h3 className="mt-2 text-lg font-semibold">{post.title}</h3>
              <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{post.content}</p>
              <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                <span>作者 ID：{post.owner_id}</span>
                <span>發布時間：{formatDate(post.created_at)}</span>
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
