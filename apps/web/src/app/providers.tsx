'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import dynamic from 'next/dynamic'
import { queryClient } from '@/lib/query-client'
import '@/shared/api/sdk-config'

const ReactQueryDevtools = dynamic(
  () => import('@tanstack/react-query-devtools').then(module => module.ReactQueryDevtools),
  {
    ssr: false,
  }
)

export function Providers({ children }: { children: React.ReactNode }) {
  const isDevelopment = process.env.NODE_ENV === 'development'

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {isDevelopment ? <ReactQueryDevtools initialIsOpen={false} /> : null}
    </QueryClientProvider>
  )
}
