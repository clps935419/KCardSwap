import { useQuery } from '@tanstack/react-query'
import {
  getMyProfileApiV1ProfileMeGetOptions,
  getUserProfileApiV1ProfileUserIdGetOptions,
} from '@/shared/api/generated/@tanstack/react-query.gen'

export function useMyProfile() {
  return useQuery({
    ...getMyProfileApiV1ProfileMeGetOptions(),
    staleTime: 1000 * 60 * 5,
  })
}

export function useUserProfile(userId: string) {
  return useQuery({
    ...getUserProfileApiV1ProfileUserIdGetOptions({
      path: { user_id: userId },
    }),
    staleTime: 1000 * 60 * 5,
  })
}
