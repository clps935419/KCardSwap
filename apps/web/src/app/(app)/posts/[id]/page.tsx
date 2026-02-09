import { HydrationBoundary, dehydrate } from '@tanstack/react-query'
import { PostDetailPageClient } from '@/features/posts/components/PostDetailPageClient'
import { createServerQueryClient } from '@/lib/query-client'
import { getPostApiV1PostsPostIdGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

interface PostDetailPageProps {
  params: {
    id: string
  }
}

export default async function PostDetailPage({ params }: PostDetailPageProps) {
  const queryClient = createServerQueryClient()

  await queryClient.prefetchQuery({
    ...getPostApiV1PostsPostIdGetOptions({
      path: {
        post_id: params.id,
      },
    }),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })

  const dehydratedState = dehydrate(queryClient)

  return (
    <HydrationBoundary state={dehydratedState}>
      <PostDetailPageClient postId={params.id} />
    </HydrationBoundary>
  )
}
