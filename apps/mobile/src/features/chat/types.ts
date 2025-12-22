/**
 * Chat Feature Types
 * 
 * Type definitions for chat and messaging functionality
 */

/**
 * Message status enum
 */
export type MessageStatus = 'sent' | 'delivered' | 'read';

/**
 * Chat room with participants and last message
 */
export interface ChatRoom {
  id: string;
  participant_ids: string[];
  created_at: string;
  last_message?: Message;
  unread_count?: number;
  other_participant?: {
    id: string;
    nickname?: string;
    avatar_url?: string;
  };
}

/**
 * Chat message
 */
export interface Message {
  id: string;
  room_id: string;
  sender_id: string;
  content: string;
  status: MessageStatus;
  created_at: string;
}

/**
 * Send message payload
 */
export interface SendMessageInput {
  content: string;
}

/**
 * Get messages query params
 */
export interface GetMessagesParams {
  after_message_id?: string;
  limit?: number;
}
