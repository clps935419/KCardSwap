import { Suspense } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { PostFilters } from '@/features/posts/components/PostFilters'
import { PostsList } from '@/features/posts/components/PostsList'

export default function PostsPage() {
  return (
    <div className="space-y-6">
      {/* 標題與導覽 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">貼文</h1>
          <p className="mt-1 text-sm text-muted-foreground">瀏覽社群中的最新貼文</p>
        </div>
        <Link href="/posts/new">
          <Button>發文</Button>
        </Link>
      </div>

      {/* 篩選區域 */}
      <Card className="p-4">
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
