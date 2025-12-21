/**
 * Phase 6 TanStack Query Hooks
 * 
 * Custom hooks wrapping Phase 6 SDK functions with TanStack Query.
 * These provide the same pattern as auto-generated hooks but for manually
 * implemented Phase 6 endpoints.
 * 
 * Usage:
 * - Queries: const { data, isLoading, error } = useFriends();
 * - Mutations: const { mutate } = useSendFriendRequest();
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as phase6SDK from './phase6-sdk';

// ============================================================================
// Query Keys
// ============================================================================

export const phase6QueryKeys = {
  friends: ['friends'] as const,
  friendsWithStatus: (status?: string) => ['friends', { status }] as const,
  chatRooms: ['chatRooms'] as const,
  messages: (roomId: string) => ['messages', roomId] as const,
  messagesWithCursor: (roomId: string, afterMessageId?: string) =>
    ['messages', roomId, { afterMessageId }] as const,
  userRatings: (userId: string) => ['ratings', 'user', userId] as const,
  userAverageRating: (userId: string) => ['ratings', 'average', userId] as const,
  myReports: ['reports', 'my'] as const,
};

// ============================================================================
// Friends Hooks
// ============================================================================

/**
 * Get friends list
 */
export const useFriends = (params?: { status?: 'pending' | 'accepted' | 'blocked' }) => {
  return useQuery({
    queryKey: params?.status
      ? phase6QueryKeys.friendsWithStatus(params.status)
      : phase6QueryKeys.friends,
    queryFn: () => phase6SDK.getFriends(params),
  });
};

/**
 * Send friend request mutation
 */
export const useSendFriendRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: phase6SDK.sendFriendRequest,
    onSuccess: () => {
      // Invalidate friends list to refetch
      queryClient.invalidateQueries({ queryKey: phase6QueryKeys.friends });
    },
  });
};

/**
 * Accept friend request mutation
 */
export const useAcceptFriendRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (friendshipId: string) => phase6SDK.acceptFriendRequest(friendshipId),
    onSuccess: () => {
      // Invalidate friends and chat rooms
      queryClient.invalidateQueries({ queryKey: phase6QueryKeys.friends });
      queryClient.invalidateQueries({ queryKey: phase6QueryKeys.chatRooms });
    },
  });
};

/**
 * Block user mutation
 */
export const useBlockUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: phase6SDK.blockUser,
    onSuccess: () => {
      // Invalidate friends list
      queryClient.invalidateQueries({ queryKey: phase6QueryKeys.friends });
    },
  });
};

// ============================================================================
// Chat Hooks
// ============================================================================

/**
 * Get chat rooms list
 */
export const useChatRooms = () => {
  return useQuery({
    queryKey: phase6QueryKeys.chatRooms,
    queryFn: phase6SDK.getChatRooms,
  });
};

/**
 * Get messages in a chat room
 * 
 * @param roomId - Chat room ID
 * @param params - Query parameters (after_message_id for cursor pagination)
 * @param options - TanStack Query options (e.g., refetchInterval for polling)
 */
export const useMessages = (
  roomId: string,
  params?: { after_message_id?: string; limit?: number },
  options?: { enabled?: boolean; refetchInterval?: number | false }
) => {
  return useQuery({
    queryKey: phase6QueryKeys.messagesWithCursor(roomId, params?.after_message_id),
    queryFn: () => phase6SDK.getMessages(roomId, params),
    ...options,
  });
};

/**
 * Send message mutation
 */
export const useSendMessage = (roomId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (content: string) => phase6SDK.sendMessage(roomId, { content }),
    onSuccess: () => {
      // Invalidate messages to refetch
      queryClient.invalidateQueries({ queryKey: phase6QueryKeys.messages(roomId) });
    },
  });
};

/**
 * Mark message as read mutation
 */
export const useMarkMessageAsRead = (roomId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (messageId: string) => phase6SDK.markMessageAsRead(roomId, messageId),
    onSuccess: () => {
      // Invalidate messages to refetch
      queryClient.invalidateQueries({ queryKey: phase6QueryKeys.messages(roomId) });
    },
  });
};

// ============================================================================
// Ratings Hooks
// ============================================================================

/**
 * Get user ratings
 */
export const useUserRatings = (userId: string, params?: { limit?: number }) => {
  return useQuery({
    queryKey: phase6QueryKeys.userRatings(userId),
    queryFn: () => phase6SDK.getUserRatings(userId, params),
  });
};

/**
 * Get user average rating
 */
export const useUserAverageRating = (userId: string) => {
  return useQuery({
    queryKey: phase6QueryKeys.userAverageRating(userId),
    queryFn: () => phase6SDK.getUserAverageRating(userId),
  });
};

/**
 * Submit rating mutation
 */
export const useSubmitRating = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: phase6SDK.submitRating,
    onSuccess: (_, variables) => {
      // Invalidate the rated user's ratings and average
      queryClient.invalidateQueries({
        queryKey: phase6QueryKeys.userRatings(variables.rated_user_id),
      });
      queryClient.invalidateQueries({
        queryKey: phase6QueryKeys.userAverageRating(variables.rated_user_id),
      });
    },
  });
};

// ============================================================================
// Reports Hooks
// ============================================================================

/**
 * Get my reports
 */
export const useMyReports = () => {
  return useQuery({
    queryKey: phase6QueryKeys.myReports,
    queryFn: phase6SDK.getMyReports,
  });
};

/**
 * Submit report mutation
 */
export const useSubmitReport = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: phase6SDK.submitReport,
    onSuccess: () => {
      // Invalidate my reports list
      queryClient.invalidateQueries({ queryKey: phase6QueryKeys.myReports });
    },
  });
};
