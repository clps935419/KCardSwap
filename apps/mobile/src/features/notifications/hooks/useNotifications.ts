/**
 * Notifications Hook
 * 
 * Custom hook to handle push notifications:
 * - Register FCM token on app launch
 * - Listen for foreground/background notifications
 * - Handle notification taps (navigation)
 */

import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import * as Notifications from 'expo-notifications';
import {
  getFCMToken,
  registerFCMToken,
  parseNotificationData,
} from '../services/fcm';

/**
 * Initialize push notifications
 * 
 * Call this hook in the root layout to:
 * - Request permissions
 * - Register FCM token
 * - Setup notification listeners
 */
export const useNotifications = () => {
  const router = useRouter();

  useEffect(() => {
    // 1. Request permissions and register token
    const setupNotifications = async () => {
      try {
        const token = await getFCMToken();

        if (token) {
          await registerFCMToken(token);
          console.log('✅ Push notifications initialized');
        } else {
          console.warn('⚠️ Failed to get FCM token');
        }
      } catch (error) {
        console.error('❌ Error setting up notifications:', error);
      }
    };

    setupNotifications();

    // 2. Listen for notifications received while app is in foreground
    const notificationListener = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('📬 Notification received (foreground):', notification);

        const data = parseNotificationData(notification);

        // Show in-app notification toast (optional)
        // You can implement custom toast UI here
        console.log('Notification data:', data);
      }
    );

    // 3. Listen for notification taps (navigation)
    const responseListener = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('👆 Notification tapped:', response);

        const data = parseNotificationData(response.notification);

        if (!data) return;

        // Navigate based on notification type
        switch (data.type) {
          case 'chat_message':
            if (data.room_id) {
              router.push(`/chat/${data.room_id}`);
            }
            break;

          case 'friend_request':
            router.push('/friends');
            break;

          case 'trade_proposal':
            if (data.trade_id) {
              router.push(`/trade/${data.trade_id}`);
            }
            break;

          case 'rating':
            router.push('/profile');
            break;

          default:
            console.warn('Unknown notification type:', data.type);
        }
      }
    );

    // 4. Cleanup listeners on unmount
    return () => {
      Notifications.removeNotificationSubscription(notificationListener);
      Notifications.removeNotificationSubscription(responseListener);
    };
  }, [router]);
};

/**
 * Hook to handle notification badge count
 * 
 * Call this to update the app icon badge
 */
export const useBadgeCount = () => {
  const setBadge = async (count: number) => {
    await Notifications.setBadgeCountAsync(count);
  };

  const clearBadge = async () => {
    await Notifications.setBadgeCountAsync(0);
  };

  return { setBadge, clearBadge };
};
