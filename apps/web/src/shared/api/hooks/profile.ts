import { useQuery } from '@tanstack/react-query'
import { getMyProfileApiV1ProfileMeGetOptions } from '@/shared/api/generated/@tanstack/react-query.gen'

export function useMyProfile() {
  return useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 1000 * 60 * 5,
  })
}
