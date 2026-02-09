import { HydrationBoundary, dehydrate } from '@tanstack/react-query'
import { MyGalleryPageClient } from '@/features/gallery/components/MyGalleryPageClient'
import { createServerQueryClient } from '@/lib/query-client'
import { getMyGalleryCardsApiV1GalleryCardsMeGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

export default async function MyGalleryPage() {
  const queryClient = createServerQueryClient()

  await queryClient.prefetchQuery({
    ...getMyGalleryCardsApiV1GalleryCardsMeGetOptions(),
  })

  const dehydratedState = dehydrate(queryClient)

  return (
    <HydrationBoundary state={dehydratedState}>
      <MyGalleryPageClient />
    </HydrationBoundary>
  )
}
