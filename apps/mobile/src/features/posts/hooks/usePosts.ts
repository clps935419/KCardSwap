/**
 * Posts Hooks
 * React Query hooks for posts management using generated SDK
 * 
 * Exports:
 * - useBoardPosts: 取得城市看板貼文列表
 * - useCreatePost: 建立貼文
 * - useExpressInterest: 表達興趣
 * - useAcceptInterest: 接受興趣
 * - useRejectInterest: 拒絕興趣
 * - useClosePost: 關閉貼文
 * - usePostInterests: 取得貼文的興趣清單
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listPostsApiV1PostsGet,
  createPostApiV1PostsPost,
  expressInterestApiV1PostsPostIdInterestPost,
  acceptInterestApiV1PostsPostIdInterestsInterestIdAcceptPost,
  rejectInterestApiV1PostsPostIdInterestsInterestIdRejectPost,
  closePostApiV1PostsPostIdClosePost,
  listPostInterestsApiV1PostsPostIdInterestsGet,
  getPostInterestApiV1PostsPostIdInterestsInterestIdGet,
} from '@/src/shared/api/sdk';
import type {
  Post,
  PostInterest,
  CreatePostRequest,
  PostListResponse,
  AcceptInterestResponse,
} from '../types';

// Query keys
export const postsKeys = {
  all: ['posts'] as const,
  board: (cityCode: string, filters?: { idol?: string; idol_group?: string }) =>
    ['posts', 'board', cityCode, filters] as const,
  interests: (postId: string) => ['posts', 'interests', postId] as const,
};

/**
 * Hook: 取得城市看板貼文列表
 * M701: 城市看板列表
 */
export function useBoardPosts(params: {
  city_code: string;
  idol?: string;
  idol_group?: string;
}) {
  return useQuery({
    queryKey: postsKeys.board(params.city_code, {
      idol: params.idol,
      idol_group: params.idol_group,
    }),
    queryFn: async () => {
      const response = await listPostsApiV1PostsGet({
        query: {
          city_code: params.city_code,
          idol: params.idol,
          idol_group: params.idol_group,
        },
      });
      return response.data as PostListResponse;
    },
    enabled: !!params.city_code,
    staleTime: 1000 * 60 * 2, // 2 分鐘內不重新請求
  });
}

/**
 * Hook: 建立貼文
 * M702: 建立貼文頁
 */
export function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreatePostRequest) => {
      const response = await createPostApiV1PostsPost({
        body: data,
      });
      return response.data as Post;
    },
    onSuccess: (newPost) => {
      // 使該城市的看板列表失效，強制重新載入
      queryClient.invalidateQueries({
        queryKey: ['posts', 'board', newPost.city_code],
      });
    },
  });
}

/**
 * Hook: 表達興趣
 * M703: 貼文詳情與「有興趣」
 */
export function useExpressInterest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: string) => {
      const response = await expressInterestApiV1PostsPostIdInterestPost({
        path: { post_id: postId },
      });
      return response.data as PostInterest;
    },
    onSuccess: (_, postId) => {
      // 使該貼文的興趣清單失效
      queryClient.invalidateQueries({
        queryKey: postsKeys.interests(postId),
      });
    },
  });
}

/**
 * Hook: 接受興趣
 * M704: 作者端興趣清單與接受導流
 */
export function useAcceptInterest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ postId, interestId }: { postId: string; interestId: string }) => {
      const response = await acceptInterestApiV1PostsPostIdInterestsInterestIdAcceptPost({
        path: { post_id: postId, interest_id: interestId },
      });
      return response.data as AcceptInterestResponse;
    },
    onSuccess: (_, { postId }) => {
      // 使該貼文的興趣清單失效
      queryClient.invalidateQueries({
        queryKey: postsKeys.interests(postId),
      });
      // 使好友列表失效（因為可能新增了好友）
      queryClient.invalidateQueries({
        queryKey: ['friends'],
      });
      // 使聊天室列表失效（因為可能新增了聊天室）
      queryClient.invalidateQueries({
        queryKey: ['chatRooms'],
      });
    },
  });
}

/**
 * Hook: 拒絕興趣
 * M704: 作者端興趣清單與接受導流
 */
export function useRejectInterest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ postId, interestId }: { postId: string; interestId: string }) => {
      const response = await rejectInterestApiV1PostsPostIdInterestsInterestIdRejectPost({
        path: { post_id: postId, interest_id: interestId },
      });
      return response.data;
    },
    onSuccess: (_, { postId }) => {
      // 使該貼文的興趣清單失效
      queryClient.invalidateQueries({
        queryKey: postsKeys.interests(postId),
      });
    },
  });
}

/**
 * Hook: 關閉貼文
 */
export function useClosePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: string) => {
      const response = await closePostApiV1PostsPostIdClosePost({
        path: { post_id: postId },
      });
      return response.data;
    },
    onSuccess: () => {
      // 使所有看板列表失效
      queryClient.invalidateQueries({
        queryKey: ['posts', 'board'],
      });
    },
  });
}

/**
 * Hook: 取得貼文的興趣清單
 * M704: 作者端興趣清單與接受導流
 * T1301-T1304: 實作後端 API endpoint 並整合到前端
 * 
 * 功能：
 * - 僅貼文作者可查看
 * - 支援 status 篩選 (pending, accepted, rejected)
 * - 支援分頁
 */
export function usePostInterests(
  postId: string,
  filters?: {
    status?: 'pending' | 'accepted' | 'rejected';
    limit?: number;
    offset?: number;
  }
) {
  return useQuery({
    queryKey: postsKeys.interests(postId),
    queryFn: async () => {
      const response = await listPostInterestsApiV1PostsPostIdInterestsGet({
        path: { post_id: postId },
        query: {
          status: filters?.status,
          limit: filters?.limit || 50,
          offset: filters?.offset || 0,
        },
      });
      return response.data?.interests || [];
    },
    enabled: !!postId,
    staleTime: 1000 * 60, // 1 分鐘內不重新請求
  });
}

/**
 * Hook: 取得單一貼文興趣詳情
 * T1301-T1304: 新增功能
 * 
 * 功能：
 * - 僅貼文作者可查看
 * - 取得特定興趣的詳細資訊
 */
export function usePostInterest(postId: string, interestId: string) {
  return useQuery({
    queryKey: [...postsKeys.interests(postId), interestId] as const,
    queryFn: async () => {
      const response = await getPostInterestApiV1PostsPostIdInterestsInterestIdGet({
        path: { post_id: postId, interest_id: interestId },
      });
      return response.data as PostInterest;
    },
    enabled: !!postId && !!interestId,
    staleTime: 1000 * 60 * 5, // 5 分鐘內不重新請求
  });
}
