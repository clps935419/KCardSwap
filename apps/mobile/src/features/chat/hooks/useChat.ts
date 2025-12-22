/**
 * Chat Hooks
 * 
 * Custom hooks for chat functionality using TanStack Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getChatRoomsApiV1ChatsGetOptions,
  getMessagesApiV1ChatsRoomIdMessagesGetOptions,
  sendMessageApiV1ChatsRoomIdMessagesPostMutation,
} from '@/src/shared/api/generated/@tanstack/react-query.gen';

/**
 * Hook to fetch all chat rooms
 */
export const useChatRooms = () => {
  return useQuery({
    ...getChatRoomsApiV1ChatsGetOptions(),
  });
};

/**
 * Hook to fetch messages from a chat room
 * 
 * @param roomId - Chat room ID
 * @param afterMessageId - Optional cursor for pagination
 * @param options - TanStack Query options (e.g., refetchInterval for polling)
 */
export const useMessages = (
  roomId: string,
  afterMessageId?: string,
  options?: {
    enabled?: boolean;
    refetchInterval?: number | false;
  }
) => {
  const result = useQuery({
    ...getMessagesApiV1ChatsRoomIdMessagesGetOptions({
      path: { room_id: roomId },
      query: afterMessageId ? { after_message_id: afterMessageId, limit: 50 } : { limit: 50 },
    }),
    enabled: options?.enabled !== false && !!roomId,
    refetchInterval: options?.refetchInterval,
  });

  // Transform the response to extract messages array
  return {
    ...result,
    data: result.data?.messages || [],
  };
};

/**
 * Hook to send a message
 * 
 * @param roomId - Chat room ID
 */
export const useSendMessage = (roomId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    ...sendMessageApiV1ChatsRoomIdMessagesPostMutation(),
    onSuccess: () => {
      // Invalidate messages to refetch
      queryClient.invalidateQueries({
        queryKey: ['getMessagesApiV1ChatsRoomIdMessagesGet', { path: { room_id: roomId } }],
      });
    },
  });
};
