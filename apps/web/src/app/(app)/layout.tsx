import { dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { createServerQueryClient } from '@/lib/query-client'
import { getMyProfileApiV1ProfileMeGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'
import { AppLayoutClient } from './AppLayoutClient'

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const queryClient = createServerQueryClient()

  await queryClient.prefetchQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
  })

  const dehydratedState = dehydrate(queryClient)

  return (
    <HydrationBoundary state={dehydratedState}>
      <AppLayoutClient>{children}</AppLayoutClient>
    </HydrationBoundary>
  )
}
