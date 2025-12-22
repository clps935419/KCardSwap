/**
 * Message Polling Service
 * 
 * Implements intelligent polling strategy for chat messages:
 * - Polls every 3-5 seconds when active
 * - Uses after_message_id cursor for incremental updates
 * - Implements backoff when no new messages
 * - Stops polling when app goes to background
 */

import { useEffect, useRef, useState } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { useMessages } from '../hooks/useChat';

/**
 * Configuration for polling behavior
 */
interface PollingConfig {
  /** Initial polling interval in milliseconds */
  initialInterval: number;
  /** Maximum polling interval in milliseconds */
  maxInterval: number;
  /** Backoff multiplier when no messages received */
  backoffMultiplier: number;
  /** Number of empty polls before applying backoff */
  emptyPollsBeforeBackoff: number;
}

const DEFAULT_CONFIG: PollingConfig = {
  initialInterval: 3000, // 3 seconds
  maxInterval: 10000, // 10 seconds
  backoffMultiplier: 1.5,
  emptyPollsBeforeBackoff: 3,
};

/**
 * Custom hook for message polling with intelligent backoff
 * 
 * @param roomId - Chat room ID to poll messages from
 * @param config - Optional polling configuration
 * @returns Messages array and refetch function
 */
export const useMessagePolling = (
  roomId: string,
  config: Partial<PollingConfig> = {}
) => {
  const fullConfig = { ...DEFAULT_CONFIG, ...config };

  const [lastMessageId, setLastMessageId] = useState<string | undefined>();
  const [pollInterval, setPollInterval] = useState(fullConfig.initialInterval);
  const [isActive, setIsActive] = useState(true);
  const emptyPollCountRef = useRef(0);

  // Listen to app state changes
  useEffect(() => {
    const subscription = AppState.addEventListener('change', (nextAppState: AppStateStatus) => {
      const isAppActive = nextAppState === 'active';
      setIsActive(isAppActive);

      // Reset interval when returning to foreground
      if (isAppActive) {
        setPollInterval(fullConfig.initialInterval);
        emptyPollCountRef.current = 0;
      }
    });

    return () => subscription.remove();
  }, [fullConfig.initialInterval]);

  // Fetch messages with polling
  const {
    data: messages,
    refetch,
    isLoading,
  } = useMessages(roomId, lastMessageId, {
    enabled: isActive && !!roomId,
    refetchInterval: isActive ? pollInterval : false,
  });

  // Update lastMessageId and handle backoff
  useEffect(() => {
    if (!messages) return;

    const messageArray = Array.isArray(messages) ? messages : [];

    if (messageArray.length > 0) {
      // New messages received - reset backoff
      const newestMessage = messageArray[messageArray.length - 1];
      setLastMessageId(newestMessage.id);
      setPollInterval(fullConfig.initialInterval);
      emptyPollCountRef.current = 0;
    } else {
      // No new messages - increment empty poll counter
      emptyPollCountRef.current += 1;

      // Apply backoff after threshold
      if (emptyPollCountRef.current >= fullConfig.emptyPollsBeforeBackoff) {
        setPollInterval((prev) =>
          Math.min(prev * fullConfig.backoffMultiplier, fullConfig.maxInterval)
        );
      }
    }
  }, [messages, fullConfig]);

  /**
   * Manual refetch with interval reset
   * Useful when user sends a message
   */
  const refetchAndReset = () => {
    setPollInterval(fullConfig.initialInterval);
    emptyPollCountRef.current = 0;
    refetch();
  };

  return {
    messages: messages || [],
    refetch: refetchAndReset,
    isLoading,
    pollInterval,
    isActive,
  };
};

/**
 * Get polling stats for debugging
 */
export const getPollingStats = (
  pollInterval: number,
  isActive: boolean,
  messageCount: number
) => {
  return {
    currentInterval: `${pollInterval / 1000}s`,
    isActive,
    messageCount,
    status: !isActive
      ? 'paused (background)'
      : pollInterval <= 3000
      ? 'active (fast)'
      : pollInterval <= 6000
      ? 'active (medium)'
      : 'active (slow)',
  };
};
