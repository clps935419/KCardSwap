/**
 * Posts Hooks
 * React Query hooks for posts management
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type {
  Post,
  PostInterest,
  CreatePostRequest,
  AcceptInterestResponse,
} from '../types';
import {
  createPost,
  fetchBoardPosts,
  expressInterest,
  acceptInterest,
  rejectInterest,
  closePost,
  fetchPostInterests,
} from '../api';

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
    queryFn: () => fetchBoardPosts(params),
    enabled: !!params.city_code, // 只有當 city_code 存在時才執行
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
    mutationFn: (data: CreatePostRequest) => createPost(data),
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
    mutationFn: (postId: string) => expressInterest(postId),
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
    mutationFn: ({ postId, interestId }: { postId: string; interestId: string }) =>
      acceptInterest(postId, interestId),
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
    mutationFn: ({ postId, interestId }: { postId: string; interestId: string }) =>
      rejectInterest(postId, interestId),
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
    mutationFn: (postId: string) => closePost(postId),
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
 */
export function usePostInterests(postId: string) {
  return useQuery({
    queryKey: postsKeys.interests(postId),
    queryFn: () => fetchPostInterests(postId),
    enabled: !!postId,
    staleTime: 1000 * 60, // 1 分鐘內不重新請求
  });
}
