/**
 * Friends Feature Types
 * 
 * Type definitions for friend management functionality
 */

/**
 * Friendship status enum
 */
export type FriendshipStatus = 'pending' | 'accepted' | 'blocked';

/**
 * Tab filter for friends list
 */
export type FriendsTab = 'all' | 'pending' | 'blocked';

/**
 * Friend item in the list
 */
export interface FriendItem {
  id: string;
  friendship_id: string;
  user_id: string;
  friend_id: string;
  status: FriendshipStatus;
  created_at: string;
  nickname?: string;
  bio?: string;
  avatar_url?: string;
}

/**
 * Friend request payload
 */
export interface SendFriendRequestInput {
  friend_id: string;
}

/**
 * Block user payload
 */
export interface BlockUserInput {
  blocked_user_id: string;
}
