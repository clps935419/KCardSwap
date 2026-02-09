import { dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { UserProfilePageClient } from '@/features/gallery/components/UserProfilePageClient'
import { createServerQueryClient } from '@/lib/query-client'
import { getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

interface UserProfilePageProps {
  params: {
    userId: string
  }
}

export default async function UserProfilePage({ params }: UserProfilePageProps) {
  const queryClient = createServerQueryClient()

  await queryClient.prefetchQuery({
    ...getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions({
      path: {
        user_id: params.userId,
      },
    }),
  })

  const dehydratedState = dehydrate(queryClient)

  return (
    <HydrationBoundary state={dehydratedState}>
      <UserProfilePageClient userId={params.userId} />
    </HydrationBoundary>
  )
}
