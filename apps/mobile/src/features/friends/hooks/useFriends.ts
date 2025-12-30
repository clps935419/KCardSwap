/**
 * Friends Hooks
 * 
 * Custom hooks for friend management using TanStack Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getFriendsApiV1FriendsGetOptions,
  sendFriendRequestApiV1FriendsRequestPostMutation,
  acceptFriendRequestApiV1FriendsFriendshipIdAcceptPostMutation,
  blockUserApiV1FriendsBlockPostMutation,
  unblockUserApiV1FriendsUnblockPostMutation,
} from '@/src/shared/api/generated/@tanstack/react-query.gen';
import type { FriendshipStatus } from '../types';

/**
 * Hook to fetch friends list
 * 
 * @param status - Optional filter by friendship status
 */
export const useFriendsList = (status?: FriendshipStatus) => {
  return useQuery({
    ...getFriendsApiV1FriendsGetOptions({
      query: status ? { status } : undefined,
    }),
  });
};

/**
 * Hook to send friend request
 */
export const useSendFriendRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...sendFriendRequestApiV1FriendsRequestPostMutation(),
    onSuccess: () => {
      // Invalidate friends list to refetch
      queryClient.invalidateQueries({
        queryKey: ['getFriendsApiV1FriendsGet'],
      });
    },
  });
};

/**
 * Hook to accept friend request
 */
export const useAcceptFriendRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...acceptFriendRequestApiV1FriendsFriendshipIdAcceptPostMutation(),
    onSuccess: () => {
      // Invalidate friends list to refetch
      queryClient.invalidateQueries({
        queryKey: ['getFriendsApiV1FriendsGet'],
      });
    },
  });
};

/**
 * Hook to block user
 */
export const useBlockUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...blockUserApiV1FriendsBlockPostMutation(),
    onSuccess: () => {
      // Invalidate friends list to refetch
      queryClient.invalidateQueries({
        queryKey: ['getFriendsApiV1FriendsGet'],
      });
    },
  });
};

/**
 * Hook to unblock user
 */
export const useUnblockUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...unblockUserApiV1FriendsUnblockPostMutation(),
    onSuccess: () => {
      // Invalidate friends list to refetch
      queryClient.invalidateQueries({
        queryKey: ['getFriendsApiV1FriendsGet'],
      });
    },
  });
};
