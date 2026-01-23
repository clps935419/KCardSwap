/**
 * SendMessageForm Component - Form to send a message in a thread
 */
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface SendMessageFormProps {
  threadId: string;
}

export function SendMessageForm({ threadId }: SendMessageFormProps) {
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      return;
    }

    setLoading(true);
    try {
      // TODO: Call send message endpoint using generated SDK
      // await sendMessage({
      //   thread_id: threadId,
      //   content: content.trim(),
      // });
      
      setContent("");
      
      // Refresh messages
      // queryClient.invalidateQueries(['thread-messages', threadId]);
      
      toast({
        title: "Message sent",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Textarea
        placeholder="Type your message..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="resize-none"
        rows={2}
        disabled={loading}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <Button type="submit" disabled={loading || !content.trim()}>
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
      </Button>
    </form>
  );
}
