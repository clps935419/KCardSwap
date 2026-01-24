/**
 * Thread Page - Shows messages in a conversation thread
 */
"use client";

import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageList } from "@/features/inbox/components/MessageList";
import { SendMessageForm } from "@/features/inbox/components/SendMessageForm";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function ThreadPage() {
  const params = useParams();
  const threadId = params.threadId as string;

  return (
    <div className="container max-w-4xl py-8">
      <div className="mb-4">
        <Button variant="ghost" asChild>
          <Link href="/inbox">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Inbox
          </Link>
        </Button>
      </div>

      <Card className="flex flex-col h-[calc(100vh-12rem)]">
        <CardHeader>
          <CardTitle>Conversation</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto mb-4">
            <MessageList threadId={threadId} />
          </div>
          <div className="border-t pt-4">
            <SendMessageForm threadId={threadId} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
