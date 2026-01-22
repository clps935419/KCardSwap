/**
 * Idol Groups Hooks
 * 用於獲取偶像團體列表的 Hook
 */

import { useQuery } from '@tanstack/react-query';
import { getIdolGroupsApiV1IdolsGroupsGetOptions } from '@/src/shared/api/generated/@tanstack/react-query.gen';
import type { IdolGroupResponse } from '@/src/shared/api/generated/types.gen';

/**
 * Fetch all idol groups from the backend API
 * 從後端 API 獲取所有偶像團體
 * 
 * @returns Query result with idol groups data
 */
export function useIdolGroups() {
  const result = useQuery({
    ...getIdolGroupsApiV1IdolsGroupsGetOptions(),
    // Cache for 1 hour since idol groups data rarely changes
    staleTime: 1000 * 60 * 60,
    // Keep in cache for 24 hours
    gcTime: 1000 * 60 * 60 * 24,
  });

  // Extract groups from envelope format
  return {
    ...result,
    data: result.data?.data.groups || [],
  };
}

/**
 * Type alias for idol group from API
 */
export type IdolGroup = IdolGroupResponse;
