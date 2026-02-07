import { Suspense } from 'react'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { PostFilters } from '@/features/posts/components/PostFilters'
import { PostsList } from '@/features/posts/components/PostsList'

export default function PostsPage() {
  return (
    <div className="space-y-4 max-w-2xl mx-auto">
      {/* 發文入口（簡潔單列） */}
      <Card className="p-4 rounded-2xl border border-primary/30 bg-primary/10 shadow-sm">
        <Link
          href="/posts/new"
          className="flex items-center justify-between rounded-2xl border border-primary/30 bg-card px-4 py-3 text-sm shadow-sm hover:bg-primary/5 transition-colors"
        >
          <span className="font-black text-foreground">聊聊偶像最新動態...</span>
          <span className="text-lg leading-none text-primary">＋</span>
        </Link>
      </Card>

      {/* 篩選區域 */}
      <Card className="p-4 rounded-2xl border border-border/30 bg-card">
        <Suspense fallback={<div className="h-10" />}>
          <PostFilters />
        </Suspense>
      </Card>

      {/* 貼文列表 */}
      <Suspense
        fallback={
          <div className="flex justify-center py-12">
            <Spinner className="h-8 w-8" />
          </div>
        }
      >
        <PostsList />
      </Suspense>
    </div>
  )
}
