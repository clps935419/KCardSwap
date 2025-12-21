/**
 * Phase 6 SDK Functions - Manual Implementation
 * 
 * This file contains manually implemented SDK functions for Phase 6 endpoints
 * (friends, chats, ratings, reports) as a workaround for the @hey-api/openapi-ts
 * generator issue that only generated 15/32 functions.
 * 
 * These functions follow the same pattern as the auto-generated SDK and can be
 * used with TanStack Query hooks.
 * 
 * TODO: Once SDK generator issue is resolved, these can be removed in favor of
 * auto-generated functions.
 */

import { client } from './generated/client.gen';

// ============================================================================
// Friends API
// ============================================================================

export interface SendFriendRequestRequest {
  friend_id: string;
}

export interface AcceptFriendRequestRequest {
  friendship_id: string;
}

export interface BlockUserRequest {
  user_id: string;
}

export interface FriendshipResponse {
  id: string;
  user_id: string;
  friend_id: string;
  status: 'pending' | 'accepted' | 'blocked';
  created_at: string;
  updated_at: string;
}

export interface FriendListItemResponse {
  friendship_id: string;
  user_id: string;
  nickname: string;
  avatar_url: string | null;
  status: 'pending' | 'accepted' | 'blocked';
  created_at: string;
}

export interface FriendListResponse {
  friends: FriendListItemResponse[];
}

/**
 * Send friend request
 * POST /api/v1/friends/request
 */
export const sendFriendRequest = async (data: SendFriendRequestRequest) =>
  client.post<FriendshipResponse>({
    url: '/api/v1/friends/request',
    body: data,
    headers: { 'Content-Type': 'application/json' },
  });

/**
 * Accept friend request
 * POST /api/v1/friends/{friendship_id}/accept
 */
export const acceptFriendRequest = async (friendshipId: string) =>
  client.post<FriendshipResponse>({
    url: `/api/v1/friends/${friendshipId}/accept`,
  });

/**
 * Block user
 * POST /api/v1/friends/block
 */
export const blockUser = async (data: BlockUserRequest) =>
  client.post<FriendshipResponse>({
    url: '/api/v1/friends/block',
    body: data,
    headers: { 'Content-Type': 'application/json' },
  });

/**
 * Get friends list
 * GET /api/v1/friends?status=accepted
 */
export const getFriends = async (params?: { status?: 'pending' | 'accepted' | 'blocked' }) =>
  client.get<FriendListResponse>({
    url: '/api/v1/friends',
    query: params,
  });

// ============================================================================
// Chat API
// ============================================================================

export interface ChatRoomResponse {
  id: string;
  participant_ids: string[];
  created_at: string;
}

export interface MessageResponse {
  id: string;
  room_id: string;
  sender_id: string;
  content: string;
  status: 'sent' | 'delivered' | 'read';
  created_at: string;
  updated_at: string;
}

export interface SendMessageRequest {
  content: string;
}

export interface GetMessagesParams {
  after_message_id?: string;
  limit?: number;
}

/**
 * Get chat rooms list
 * GET /api/v1/chats
 */
export const getChatRooms = async () =>
  client.get<ChatRoomResponse[]>({
    url: '/api/v1/chats',
  });

/**
 * Get messages in a chat room (with cursor-based pagination)
 * GET /api/v1/chats/{room_id}/messages?after_message_id={id}&limit=50
 */
export const getMessages = async (roomId: string, params?: GetMessagesParams) =>
  client.get<MessageResponse[]>({
    url: `/api/v1/chats/${roomId}/messages`,
    query: params,
  });

/**
 * Send message in a chat room
 * POST /api/v1/chats/{room_id}/messages
 */
export const sendMessage = async (roomId: string, data: SendMessageRequest) =>
  client.post<MessageResponse>({
    url: `/api/v1/chats/${roomId}/messages`,
    body: data,
    headers: { 'Content-Type': 'application/json' },
  });

/**
 * Mark message as read
 * POST /api/v1/chats/{room_id}/messages/{message_id}/read
 */
export const markMessageAsRead = async (roomId: string, messageId: string) =>
  client.post<MessageResponse>({
    url: `/api/v1/chats/${roomId}/messages/${messageId}/read`,
  });

// ============================================================================
// Ratings API
// ============================================================================

export interface RatingRequest {
  rated_user_id: string;
  trade_id: string;
  score: number; // 1-5
  comment?: string;
}

export interface RatingResponse {
  id: string;
  rater_id: string;
  rated_user_id: string;
  trade_id: string;
  score: number;
  comment: string | null;
  created_at: string;
}

export interface RatingListResponse {
  ratings: RatingResponse[];
}

export interface AverageRatingResponse {
  user_id: string;
  average_rating: number | null;
  total_ratings: number;
}

/**
 * Submit rating
 * POST /api/v1/ratings
 */
export const submitRating = async (data: RatingRequest) =>
  client.post<RatingResponse>({
    url: '/api/v1/ratings',
    body: data,
    headers: { 'Content-Type': 'application/json' },
  });

/**
 * Get user ratings
 * GET /api/v1/ratings/user/{user_id}
 */
export const getUserRatings = async (userId: string, params?: { limit?: number }) =>
  client.get<RatingListResponse>({
    url: `/api/v1/ratings/user/${userId}`,
    query: params,
  });

/**
 * Get user average rating
 * GET /api/v1/ratings/user/{user_id}/average
 */
export const getUserAverageRating = async (userId: string) =>
  client.get<AverageRatingResponse>({
    url: `/api/v1/ratings/user/${userId}/average`,
  });

// ============================================================================
// Reports API
// ============================================================================

export interface ReportRequest {
  reported_user_id: string;
  reason: 'fraud' | 'fake_card' | 'harassment' | 'inappropriate_content' | 'spam' | 'other';
  detail?: string;
}

export interface ReportResponse {
  id: string;
  reporter_id: string;
  reported_user_id: string;
  reason: string;
  detail: string | null;
  created_at: string;
  resolved: boolean;
  resolved_at: string | null;
}

export interface ReportListResponse {
  reports: ReportResponse[];
}

/**
 * Submit report
 * POST /api/v1/reports
 */
export const submitReport = async (data: ReportRequest) =>
  client.post<ReportResponse>({
    url: '/api/v1/reports',
    body: data,
    headers: { 'Content-Type': 'application/json' },
  });

/**
 * Get my reports
 * GET /api/v1/reports
 */
export const getMyReports = async () =>
  client.get<ReportListResponse>({
    url: '/api/v1/reports',
  });
