/**
 * Cities Hook
 * React Query hook for fetching city list using generated SDK
 * M705: 建立 useCities hook
 */

import { useQuery } from '@tanstack/react-query';
import { getCitiesApiV1LocationsCitiesGet } from '@/src/shared/api/sdk';
import type { City } from '../types';

// Query keys
export const citiesKeys = {
  all: ['cities'] as const,
};

/**
 * Hook: 取得所有可用的台灣城市列表
 * 用於建立貼文頁面的城市下拉選單
 * 
 * Features:
 * - 無需認證即可存取（公開資源）
 * - 包含城市代碼、英文名稱、中文名稱
 * - 長時間快取（城市列表不常變動）
 * 
 * @returns Query result containing list of cities
 * 
 * @example
 * ```tsx
 * const { data: cities, isLoading } = useCities();
 * 
 * // 在下拉選單中使用
 * cities?.map(city => (
 *   <option key={city.code} value={city.code}>
 *     {city.name_zh} ({city.code})
 *   </option>
 * ))
 * ```
 */
export function useCities() {
  return useQuery({
    queryKey: citiesKeys.all,
    queryFn: async () => {
      const response = await getCitiesApiV1LocationsCitiesGet();
      // Extract data from envelope format
      return (response.data?.data?.cities || []) as City[];
    },
    staleTime: 1000 * 60 * 60 * 24, // 24 小時內不重新請求（城市列表不常變動）
    gcTime: 1000 * 60 * 60 * 24 * 7, // 7 天後清除快取
    retry: 3, // 失敗時重試 3 次
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // 指數退避
  });
}
