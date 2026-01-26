import { Suspense } from 'react'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { PostFilters } from '@/features/posts/components/PostFilters'
import { PostsList } from '@/features/posts/components/PostsList'

export default function PostsPage() {
  return (
    <div className="space-y-4 max-w-2xl mx-auto">
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
