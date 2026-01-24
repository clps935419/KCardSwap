/**
 * Custom hook for creating message requests
 * 
 * TODO: Replace with generated SDK mutation after OpenAPI generation
 */
"use client";

import { useState } from "react";

interface CreateMessageRequestParams {
  recipientId: string;
  initialMessage: string;
  postId?: string;
}

export function useCreateMessageRequest() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const createRequest = async (params: CreateMessageRequestParams) => {
    setLoading(true);
    setError(null);

    try {
      // TODO: Replace with generated SDK call
      // const response = await client.POST('/api/v1/message-requests', {
      //   body: {
      //     recipient_id: params.recipientId,
      //     initial_message: params.initialMessage,
      //     post_id: params.postId,
      //   },
      // });
      
      // For now, return mock response
      return {
        id: "mock-request-id",
        sender_id: "current-user",
        recipient_id: params.recipientId,
        initial_message: params.initialMessage,
        post_id: params.postId,
        status: "pending",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
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
    createRequest,
    loading,
    error,
  };
}
