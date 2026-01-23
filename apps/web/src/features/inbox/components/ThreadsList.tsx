/**
 * ThreadsList Component
 * 
 * Displays list of message threads for the current user
 */
"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { MessageCircle } from "lucide-react";
import Link from "next/link";

// TODO: Replace with generated SDK types after OpenAPI generation
interface MessageThread {
  id: string;
  user_a_id: string;
  user_b_id: string;
  created_at: string;
  updated_at: string;
  last_message_at?: string;
}

export function ThreadsList() {
  const [threads, setThreads] = useState<MessageThread[]>([]);

  // TODO: Replace with generated SDK hook
  // const { data, isLoading } = useGetMyThreads();

  if (threads.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <MessageCircle className="mx-auto h-12 w-12 mb-4 opacity-50" />
        <p>No conversations yet</p>
        <p className="text-sm mt-2">Start a conversation by messaging someone from a post</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {threads.map((thread) => (
        <Link key={thread.id} href={`/inbox/threads/${thread.id}`}>
          <Card className="p-4 hover:bg-accent transition-colors cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Conversation</p>
                <p className="text-sm text-muted-foreground">
                  {thread.last_message_at
                    ? new Date(thread.last_message_at).toLocaleDateString()
                    : "No messages yet"}
                </p>
              </div>
              <MessageCircle className="h-5 w-5 text-muted-foreground" />
            </div>
          </Card>
        </Link>
      ))}
    </div>
  );
}
