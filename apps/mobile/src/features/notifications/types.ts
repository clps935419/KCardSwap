/**
 * Notifications Feature Types
 * 
 * Type definitions for push notifications
 */

/**
 * Notification type enum
 */
export type NotificationType = 'chat_message' | 'friend_request' | 'trade_proposal' | 'rating';

/**
 * Notification data payload
 */
export interface NotificationData {
  type: NotificationType;
  title: string;
  body: string;
  room_id?: string;
  message_id?: string;
  user_id?: string;
  trade_id?: string;
}

/**
 * FCM token registration payload
 */
export interface RegisterTokenInput {
  fcm_token: string;
  device_id: string;
  platform: 'ios' | 'android';
}
