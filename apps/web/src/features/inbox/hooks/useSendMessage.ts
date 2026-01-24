/**
 * Custom hook for sending messages
 * 
 * TODO: Replace with generated SDK mutation after OpenAPI generation
 */
"use client";

import { useState } from "react";

interface SendMessageParams {
  threadId: string;
  content: string;
  postId?: string;
}

export function useSendMessage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendMessage = async (params: SendMessageParams) => {
    setLoading(true);
    setError(null);

    try {
      // TODO: Replace with generated SDK call
      // const response = await client.POST('/api/v1/threads/{thread_id}/messages', {
      //   params: { path: { thread_id: params.threadId } },
      //   body: {
      //     content: params.content,
      //     post_id: params.postId,
      //   },
      // });
      
      // For now, return mock response
      return {
        id: "mock-id",
        thread_id: params.threadId,
        sender_id: "current-user",
        content: params.content,
        post_id: params.postId,
        created_at: new Date().toISOString(),
      };
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    sendMessage,
    loading,
    error,
  };
}
