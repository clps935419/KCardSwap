/**
 * Posts Feature Types
 * Types for city board posts system
 */

export type PostStatus = 'open' | 'closed' | 'expired' | 'deleted';

export type PostInterestStatus = 'pending' | 'accepted' | 'rejected';

export interface Post {
  id: string;
  owner_id: string;
  city_code: string;
  title: string;
  content: string;
  idol?: string;
  idol_group?: string;
  status: PostStatus;
  expires_at: string;
  created_at: string;
  updated_at: string;
}

export interface PostInterest {
  id: string;
  post_id: string;
  user_id: string;
  status: PostInterestStatus;
  created_at: string;
  updated_at: string;
}

export interface CreatePostRequest {
  city_code: string;
  title: string;
  content: string;
  idol?: string;
  idol_group?: string;
  expires_at?: string;
}

export interface PostListResponse {
  posts: Post[];
  total: number;
}

export interface AcceptInterestResponse {
  success: boolean;
  friendship_created: boolean;
  chat_room_id: string;
  message: string;
}

/**
 * City Type
 * Represents a Taiwan city/county with code and names
 * M705: 城市資料型別定義
 */
export interface City {
  code: string;
  name: string;      // English name
  name_zh: string;   // Chinese name
}
