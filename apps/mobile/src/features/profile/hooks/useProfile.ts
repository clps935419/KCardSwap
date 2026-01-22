/**
 * Profile Hooks
 * 使用 TanStack Query 管理個人檔案相關的資料狀態
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getMyProfileOptions,
  getMyProfileQueryKey,
  updateMyProfileMutation,
  type ProfileUpdateRequest,
} from '@/src/features/profile/api/profileApi';

/**
 * Hook: 查詢我的個人檔案
 */
export function useMyProfile() {
  const result = useQuery(getMyProfileOptions());

  // Extract profile from envelope format
  return {
    ...result,
    data: result.data?.data,
  };
}

/**
 * Hook: 更新個人檔案
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    ...updateMyProfileMutation(),
    onSuccess: () => {
      // Invalidate profile query to refetch
      queryClient.invalidateQueries({ queryKey: getMyProfileQueryKey() });
    },
  });
}
