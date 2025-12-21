# Phase 6 Mobile Implementation Guide (M401-M404)

## Overview

This guide covers the implementation of Phase 6 mobile features: Friends, Chat, Ratings, and Reports.

## Prerequisites

✅ **Completed**:
- Backend API endpoints (all 13 Phase 6 endpoints)
- OpenAPI specification generated
- Manual SDK functions (`src/shared/api/phase6-sdk.ts`)
- TanStack Query hooks (`src/shared/api/phase6-hooks.ts`)

## Architecture

### Folder Structure
```
src/features/
├── friends/              # M401: Friends feature
│   ├── components/
│   ├── hooks/
│   ├── screens/
│   └── types.ts
├── chat/                 # M402-M403: Chat feature with polling
│   ├── components/
│   ├── hooks/
│   ├── screens/
│   ├── services/        # M403: Polling strategy
│   └── types.ts
└── notifications/        # M404: Push notifications
    ├── hooks/
    ├── services/
    └── types.ts
```

---

## M401: Friends Feature (好友邀請/接受/封鎖頁面)

### Screens to Implement

#### 1. Friends List Screen (`src/features/friends/screens/FriendsListScreen.tsx`)
**Route**: `/friends`

**Features**:
- Tab navigation: "Friends" | "Pending" | "Blocked"
- List of friends with avatar, nickname, online status
- Pull-to-refresh
- Search/filter friends

**Hooks to use**:
```typescript
import { useFriends } from '@/src/shared/api/phase6-hooks';

const { data, isLoading } = useFriends({ status: 'accepted' });
```

**UI Components** (Gluestack):
- `Box` - Container
- `FlatList` - List rendering
- `Avatar` - User avatar
- `Text` - User name
- `Badge` - Online status
- `Pressable` - Clickable items

#### 2. Friend Profile Screen (`src/features/friends/screens/FriendProfileScreen.tsx`)
**Route**: `/friends/[userId]`

**Features**:
- Friend's profile information
- Action buttons: "Send Message" | "Block User" | "Remove Friend"
- Rating display
- Trade history

**Hooks to use**:
```typescript
import { useBlockUser } from '@/src/shared/api/phase6-hooks';
import { useUserAverageRating } from '@/src/shared/api/phase6-hooks';

const { mutate: blockUser } = useBlockUser();
const { data: rating } = useUserAverageRating(userId);
```

#### 3. Send Friend Request Screen (`src/features/friends/screens/SendRequestScreen.tsx`)
**Route**: `/friends/add`

**Features**:
- Search user by ID or nickname
- Display user preview
- "Send Friend Request" button

**Hooks to use**:
```typescript
import { useSendFriendRequest } from '@/src/shared/api/phase6-hooks';

const { mutate: sendRequest, isPending } = useSendFriendRequest();
```

### Key Implementation Details

**Friend Request Flow**:
1. User searches for another user
2. Tap "Send Friend Request"
3. Request sent → status becomes "pending"
4. Recipient sees in "Pending" tab
5. Recipient accepts → chat room auto-created (backend)
6. Both users see each other in "Friends" tab

**Block User Flow**:
1. Tap "Block" on user profile
2. Show confirmation dialog
3. Block user → update friends list
4. Blocked user moves to "Blocked" tab
5. All interactions prevented (messages, trades, etc.)

---

## M402: Chat Feature (聊天室 UI 與輪詢)

### Screens to Implement

#### 1. Chat Rooms List Screen (`src/features/chat/screens/ChatRoomsScreen.tsx`)
**Route**: `/chat`

**Features**:
- List of all chat rooms
- Last message preview
- Unread message count badge
- Pull-to-refresh

**Hooks to use**:
```typescript
import { useChatRooms } from '@/src/shared/api/phase6-hooks';

const { data: rooms, isLoading } = useChatRooms();
```

**UI Components**:
- `FlatList` - Room list
- `Box` - Room item container
- `Avatar` - Other participant's avatar
- `Text` - Last message preview
- `Badge` - Unread count

#### 2. Chat Room Screen (`src/features/chat/screens/ChatRoomScreen.tsx`)
**Route**: `/chat/[roomId]`

**Features**:
- Message list (scrollable, inverted)
- Message input field
- Send button
- Auto-scroll to bottom on new messages
- **Polling** (M403): Refresh every 3-5 seconds when screen active

**Hooks to use**:
```typescript
import { useMessages, useSendMessage } from '@/src/shared/api/phase6-hooks';

// Polling with refetchInterval
const { data: messages } = useMessages(
  roomId,
  { after_message_id: lastMessageId },
  { refetchInterval: 3000 } // Poll every 3 seconds
);

const { mutate: sendMessage } = useSendMessage(roomId);
```

**UI Components**:
- `FlatList` - Message list (inverted)
- `Box` - Message bubble
- `Input` - Message input
- `Button` - Send button
- `Text` - Message content

### Message List Implementation

**Key Points**:
1. Use `FlatList` with `inverted` prop for bottom-to-top rendering
2. Auto-scroll to bottom when new message arrives
3. Show sender avatar and name
4. Different bubble color for self vs. other
5. Message status indicator (sent/delivered/read)

```typescript
<FlatList
  inverted
  data={messages}
  renderItem={({ item }) => (
    <MessageBubble message={item} isOwnMessage={item.sender_id === currentUserId} />
  )}
  keyExtractor={(item) => item.id}
/>
```

---

## M403: Polling Strategy (前景輪詢策略)

### Implementation: `src/features/chat/services/polling.ts`

**Requirements**:
- Poll messages every 3-5 seconds when chat screen is active
- Use `after_message_id` cursor for incremental updates
- Backoff: Increase interval if no new messages for N polls
- Stop polling when screen inactive (background)

### Polling Hook Example

```typescript
// src/features/chat/hooks/useMessagePolling.ts
import { useEffect, useRef, useState } from 'react';
import { useMessages } from '@/src/shared/api/phase6-hooks';
import { AppState, AppStateStatus } from 'react-native';

export const useMessagePolling = (roomId: string) => {
  const [lastMessageId, setLastMessageId] = useState<string | undefined>();
  const [pollInterval, setPollInterval] = useState(3000); // Start with 3s
  const [isActive, setIsActive] = useState(true);

  // Listen to app state changes
  useEffect(() => {
    const subscription = AppState.addEventListener('change', (nextAppState: AppStateStatus) => {
      setIsActive(nextAppState === 'active');
    });

    return () => subscription.remove();
  }, []);

  // Fetch messages with polling
  const { data: messages, refetch } = useMessages(
    roomId,
    { after_message_id: lastMessageId, limit: 50 },
    {
      enabled: isActive, // Only poll when app is active
      refetchInterval: isActive ? pollInterval : false, // Stop when inactive
    }
  );

  // Update lastMessageId when new messages arrive
  useEffect(() => {
    if (messages && messages.length > 0) {
      const newestMessage = messages[messages.length - 1];
      setLastMessageId(newestMessage.id);

      // Reset interval to 3s when new messages arrive
      setPollInterval(3000);
    } else if (messages && messages.length === 0) {
      // No new messages - implement backoff
      setPollInterval((prev) => Math.min(prev * 1.5, 10000)); // Max 10s
    }
  }, [messages]);

  return { messages, refetch };
};
```

### Backoff Strategy

**Progressive Backoff**:
- Initial: 3 seconds
- After 5 empty polls: 4.5 seconds
- After 10 empty polls: 6.8 seconds
- Maximum: 10 seconds

**Reset triggers**:
- New message received
- User sends a message
- Screen re-focused

---

## M404: Push Notifications (推播接收與導頁)

### Implementation: `src/features/notifications/services/fcm.ts`

**Requirements**:
- Register FCM token on app launch
- Listen for notifications (foreground & background)
- Navigate to chat room when notification tapped
- Show in-app notification when in foreground

### Setup Steps

#### 1. Configure Push Notifications

```typescript
// src/features/notifications/hooks/useNotifications.ts
import * as Notifications from 'expo-notifications';
import { useEffect } from 'react';
import { useRouter } from 'expo-router';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export const useNotifications = () => {
  const router = useRouter();

  useEffect(() => {
    // 1. Request permissions
    const requestPermissions = async () => {
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== 'granted') {
        console.warn('Push notification permissions not granted');
        return;
      }

      // 2. Get FCM token
      const token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log('FCM Token:', token);

      // TODO: Send token to backend for storage
      // await sendFCMToken(token);
    };

    requestPermissions();

    // 3. Listen for notifications (foreground)
    const notificationListener = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('Notification received:', notification);
        // Show in-app banner if needed
      }
    );

    // 4. Listen for notification taps (navigation)
    const responseListener = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        const data = response.notification.request.content.data;

        if (data.type === 'chat_message' && data.room_id) {
          // Navigate to chat room
          router.push(`/chat/${data.room_id}`);
        }
      }
    );

    return () => {
      Notifications.removeNotificationSubscription(notificationListener);
      Notifications.removeNotificationSubscription(responseListener);
    };
  }, [router]);
};
```

#### 2. Register Hook in App Root

```typescript
// app/_layout.tsx
import { useNotifications } from '@/src/features/notifications/hooks/useNotifications';

export default function RootLayout() {
  useNotifications(); // Initialize push notifications

  return (
    <GluestackUIProvider>
      <QueryClientProvider client={queryClient}>
        <Stack />
      </QueryClientProvider>
    </GluestackUIProvider>
  );
}
```

### Notification Payload Structure

Backend sends FCM notification with:
```json
{
  "title": "New message",
  "body": "John: Hello, how are you?",
  "data": {
    "type": "chat_message",
    "room_id": "uuid-123",
    "message_id": "uuid-456"
  }
}
```

### Navigation Flows

**From notification tap**:
1. User taps notification
2. App opens (or comes to foreground)
3. Navigate to `/chat/[roomId]`
4. Chat room loads messages
5. Mark messages as read

**From foreground notification**:
1. Notification received while app is open
2. Show in-app banner (Gluestack Toast)
3. User taps banner → navigate to chat room
4. Or dismiss banner → notification stays in tray

---

## Testing Checklist

### M401: Friends
- [ ] Send friend request to another user
- [ ] Accept friend request
- [ ] Reject friend request
- [ ] Block user
- [ ] Unblock user
- [ ] View friend list (accepted)
- [ ] View pending requests
- [ ] View blocked users
- [ ] Search friends

### M402: Chat
- [ ] View chat rooms list
- [ ] Open chat room
- [ ] Send message
- [ ] Receive message (polling)
- [ ] Scroll through message history
- [ ] Auto-scroll to bottom on new message
- [ ] Message status indicators

### M403: Polling
- [ ] Polling starts when chat screen opens
- [ ] Polling stops when chat screen closes
- [ ] Polling stops when app goes to background
- [ ] Polling resumes when app returns to foreground
- [ ] Backoff works (interval increases with no messages)
- [ ] Backoff resets on new message

### M404: Notifications
- [ ] FCM token registered on app launch
- [ ] Receive notification in foreground
- [ ] Receive notification in background
- [ ] Tap notification navigates to chat room
- [ ] Notification sound plays
- [ ] Badge count updates

---

## Next Steps

1. **Create feature directories** and basic screens
2. **Implement M401 (Friends)** first - simplest feature
3. **Implement M402 (Chat UI)** - core messaging functionality
4. **Add M403 (Polling)** - enhance chat with real-time updates
5. **Integrate M404 (Push)** - complete with background notifications
6. **Test end-to-end** - full friend → chat → notification flow
7. **Polish UI/UX** - animations, error handling, loading states

---

## Additional Resources

- **Gluestack UI Docs**: https://gluestack.io/ui/docs/
- **TanStack Query Docs**: https://tanstack.com/query/latest
- **Expo Notifications**: https://docs.expo.dev/versions/latest/sdk/notifications/
- **Expo Router**: https://docs.expo.dev/router/introduction/

---

## Notes

- All API calls use TanStack Query hooks (never direct SDK calls)
- Follow existing patterns in `src/features/cards` and `src/features/profile`
- Use Gluestack UI components (no native RN components like `View`, `Text`)
- Use `@/` path alias for imports
- TypeScript strict mode enabled
