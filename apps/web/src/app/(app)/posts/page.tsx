import { dehydrate, HydrationBoundary } from '@tanstack/react-query'
import Link from 'next/link'
import { Suspense } from 'react'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { PostFilters } from '@/features/posts/components/PostFilters'
import { PostsList } from '@/features/posts/components/PostsList'
import { createServerQueryClient } from '@/lib/query-client'
import type { PostCategory } from '@/shared/api/generated'
import {
  getCategoriesApiV1PostsCategoriesGetOptions,
  getCitiesApiV1LocationsCitiesGetOptions,
  listPostsApiV1PostsGetOptions,
} from '@/shared/api/generated/@tanstack/react-query.gen'

interface PostsPageProps {
  searchParams?: Promise<{
    city?: string
    category?: string
  }>
}

export default async function PostsPage({ searchParams }: PostsPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {}
  const queryClient = createServerQueryClient()
  const filtersStaleTime = 24 * 60 * 60 * 1000
  const cityParam = resolvedSearchParams.city
  const categoryParam = resolvedSearchParams.category
  const cityCode = cityParam && cityParam !== 'ALL' ? cityParam : undefined
  const category =
    categoryParam && categoryParam !== 'all' ? (categoryParam as PostCategory) : undefined

  await Promise.all([
    queryClient.prefetchQuery({
      ...getCitiesApiV1LocationsCitiesGetOptions(),
      staleTime: filtersStaleTime,
    }),
    queryClient.prefetchQuery({
      ...getCategoriesApiV1PostsCategoriesGetOptions(),
      staleTime: filtersStaleTime,
    }),
    queryClient.prefetchQuery({
      ...listPostsApiV1PostsGetOptions({
        query: {
          city_code: cityCode,
          category,
          limit: 50,
        },
      }),
    }),
  ])

  const dehydratedState = dehydrate(queryClient)

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

      <HydrationBoundary state={dehydratedState}>
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
      </HydrationBoundary>
    </div>
  )
}
