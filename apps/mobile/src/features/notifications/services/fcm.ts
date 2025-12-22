/**
 * FCM Push Notification Service
 * 
 * Handles Firebase Cloud Messaging (FCM) push notifications:
 * - Token registration
 * - Permission requests
 * - Foreground/background notification handling
 */

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import type { NotificationData } from '../types';

/**
 * Configure notification handler for foreground notifications
 */
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

/**
 * Request notification permissions
 * 
 * @returns Permission status
 */
export const requestNotificationPermissions = async (): Promise<boolean> => {
  if (!Device.isDevice) {
    console.warn('Push notifications only work on physical devices');
    return false;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.warn('Failed to get push notification permissions');
    return false;
  }

  return true;
};

/**
 * Get Expo Push Token (FCM token)
 * 
 * @returns FCM token or null if failed
 */
export const getFCMToken = async (): Promise<string | null> => {
  try {
    if (!Device.isDevice) {
      console.warn('Push notifications only work on physical devices');
      return null;
    }

    // Request permissions first
    const hasPermission = await requestNotificationPermissions();
    if (!hasPermission) {
      return null;
    }

    // Get token
    const tokenData = await Notifications.getExpoPushTokenAsync({
      projectId: 'your-project-id', // TODO: Replace with actual project ID from app.json
    });

    return tokenData.data;
  } catch (error) {
    console.error('Error getting FCM token:', error);
    return null;
  }
};

/**
 * Register FCM token with backend
 * 
 * @param token - FCM token
 * @returns Success status
 */
export const registerFCMToken = async (token: string): Promise<boolean> => {
  try {
    // TODO: Call backend API to register token
    // await apiClient.post('/api/v1/notifications/register-token', {
    //   fcm_token: token,
    //   device_id: Device.osInternalBuildId || 'unknown',
    //   platform: Platform.OS === 'ios' ? 'ios' : 'android',
    // });

    console.log('FCM Token registered:', token);
    return true;
  } catch (error) {
    console.error('Error registering FCM token:', error);
    return false;
  }
};

/**
 * Parse notification data
 * 
 * @param notification - Raw notification
 * @returns Parsed notification data
 */
export const parseNotificationData = (
  notification: Notifications.Notification
): NotificationData | null => {
  try {
    const data = notification.request.content.data;

    return {
      type: data.type as any,
      title: notification.request.content.title || '',
      body: notification.request.content.body || '',
      room_id: data.room_id,
      message_id: data.message_id,
      user_id: data.user_id,
      trade_id: data.trade_id,
    };
  } catch (error) {
    console.error('Error parsing notification data:', error);
    return null;
  }
};

/**
 * Clear all notifications
 */
export const clearAllNotifications = async () => {
  await Notifications.dismissAllNotificationsAsync();
};

/**
 * Set badge count
 * 
 * @param count - Badge number
 */
export const setBadgeCount = async (count: number) => {
  await Notifications.setBadgeCountAsync(count);
};
