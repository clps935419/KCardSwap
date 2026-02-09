import { dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { UserProfilePageClient } from '@/features/gallery/components/UserProfilePageClient'
import { createServerQueryClient } from '@/lib/query-client'
import { getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

interface UserProfilePageProps {
  params: Promise<{
    userId: string
  }>
}

export default async function UserProfilePage({ params }: UserProfilePageProps) {
  const resolvedParams = await params
  const userId = resolvedParams.userId
  const queryClient = createServerQueryClient()

  await queryClient.prefetchQuery({
    ...getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions({
      path: {
        user_id: userId,
      },
    }),
  })

  const dehydratedState = dehydrate(queryClient)

  return (
    <HydrationBoundary state={dehydratedState}>
      <UserProfilePageClient userId={userId} />
    </HydrationBoundary>
  )
}
