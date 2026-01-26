/**
 * MessageList Component
 * 
 * Displays messages in a thread
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

// TODO: Replace with generated SDK types after OpenAPI generation
interface ThreadMessage {
  id: string;
  thread_id: string;
  sender_id: string;
  content: string;
  post_id?: string;
  created_at: string;
}

interface MessageListProps {
  threadId: string;
}

export function MessageList({ threadId }: MessageListProps) {
  const [messages, setMessages] = useState<ThreadMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // TODO: Get current user ID from auth context
  const currentUserId = "current-user-id";

  // TODO: Replace with generated SDK hook
  // const { data, isLoading } = useGetThreadMessages({ thread_id: threadId });

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground text-sm">
        <p>目前沒有訊息</p>
        <p className="text-[11px] mt-2">在下方開始對話</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {messages.map((message) => {
        const isOwnMessage = message.sender_id === currentUserId;
        
        return (
          <div
            key={message.id}
            className={cn(
              "flex",
              isOwnMessage ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[75%] rounded-2xl px-4 py-3",
                isOwnMessage
                  ? "bg-slate-900 text-white"
                  : "bg-card border border-border text-foreground"
              )}
            >
              <p className="text-sm font-bold">{message.content}</p>
              {message.post_id && (
                <p className="text-[10px] opacity-70 mt-1">
                  引用貼文：{message.post_id}
                </p>
              )}
            </div>
          </div>
        );
      })}
      <div ref={messagesEndRef} />
    </div>
  );
}
