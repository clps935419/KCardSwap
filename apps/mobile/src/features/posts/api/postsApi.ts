/**
 * Posts API Client
 * API functions for city board posts
 */

import { apiClient } from '@/src/shared/api/client';
import type {
  Post,
  PostInterest,
  CreatePostRequest,
  PostListResponse,
  AcceptInterestResponse,
} from '../types';

const BASE_URL = '/posts';

/**
 * 建立貼文
 * POST /api/v1/posts
 */
export async function createPost(data: CreatePostRequest): Promise<Post> {
  const response = await apiClient.post<Post>(BASE_URL, data);
  return response.data;
}

/**
 * 取得城市看板貼文列表
 * GET /api/v1/posts?city_code=xxx&idol=xxx&idol_group=xxx
 */
export async function fetchBoardPosts(params: {
  city_code: string;
  idol?: string;
  idol_group?: string;
}): Promise<PostListResponse> {
  const response = await apiClient.get<PostListResponse>(BASE_URL, { params });
  return response.data;
}

/**
 * 表達興趣
 * POST /api/v1/posts/{id}/interest
 */
export async function expressInterest(postId: string): Promise<PostInterest> {
  const response = await apiClient.post<PostInterest>(`${BASE_URL}/${postId}/interest`);
  return response.data;
}

/**
 * 接受興趣 (作者操作)
 * POST /api/v1/posts/{id}/interests/{interest_id}/accept
 */
export async function acceptInterest(
  postId: string,
  interestId: string
): Promise<AcceptInterestResponse> {
  const response = await apiClient.post<AcceptInterestResponse>(
    `${BASE_URL}/${postId}/interests/${interestId}/accept`
  );
  return response.data;
}

/**
 * 拒絕興趣 (作者操作)
 * POST /api/v1/posts/{id}/interests/{interest_id}/reject
 */
export async function rejectInterest(
  postId: string,
  interestId: string
): Promise<{ success: boolean }> {
  const response = await apiClient.post<{ success: boolean}>(
    `${BASE_URL}/${postId}/interests/${interestId}/reject`
  );
  return response.data;
}

/**
 * 關閉貼文
 * POST /api/v1/posts/{id}/close
 */
export async function closePost(postId: string): Promise<{ success: boolean }> {
  const response = await apiClient.post<{ success: boolean }>(`${BASE_URL}/${postId}/close`);
  return response.data;
}

/**
 * 取得貼文的興趣清單 (作者查看)
 * GET /api/v1/posts/{id}/interests
 */
export async function fetchPostInterests(postId: string): Promise<PostInterest[]> {
  const response = await apiClient.get<PostInterest[]>(`${BASE_URL}/${postId}/interests`);
  return response.data;
}
