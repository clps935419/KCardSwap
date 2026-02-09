import { QueryClient } from '@tanstack/react-query'

const defaultOptions = {
  queries: {
    staleTime: 1000 * 60, // 1 minute
    refetchOnWindowFocus: false,
    retry: 1,
  },
  mutations: {
    retry: false,
  },
}

export const queryClient = new QueryClient({
  defaultOptions,
})

export function createServerQueryClient() {
  return new QueryClient({
    defaultOptions,
  })
}
