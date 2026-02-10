import { dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { createServerQueryClient } from '@/lib/query-client'
import { getMyProfileApiV1ProfileMeGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'
import { MeSettingsPageClient } from './MeSettingsPageClient'

export default async function MeSettingsPage() {
  const queryClient = createServerQueryClient()

  await queryClient.prefetchQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
  })

  const dehydratedState = dehydrate(queryClient)

  return (
    <HydrationBoundary state={dehydratedState}>
      <MeSettingsPageClient />
    </HydrationBoundary>
  )
}
