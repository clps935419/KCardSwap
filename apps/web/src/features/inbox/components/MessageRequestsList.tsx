/**
 * MessageRequestsList Component
 * 
 * Displays pending message requests for the current user
 */
"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

// TODO: Replace with generated SDK hooks after OpenAPI generation
interface MessageRequest {
  id: string;
  sender_id: string;
  recipient_id: string;
  initial_message: string;
  post_id?: string;
  status: string;
  created_at: string;
}

export function MessageRequestsList() {
  const { toast } = useToast();
  const [requests, setRequests] = useState<MessageRequest[]>([]);
  const [loading, setLoading] = useState(false);

  // TODO: Replace with generated SDK hook
  // const { data, isLoading } = useGetMyMessageRequests({ status_filter: "pending" });

  const handleAccept = async (requestId: string) => {
    setLoading(true);
    try {
      // TODO: Call accept endpoint using generated SDK
      // await acceptMessageRequest({ request_id: requestId });
      
      toast({
        title: "已接受",
        description: "已建立對話，已移到「聊天」",
      });
      
      // Refresh list
      // queryClient.invalidateQueries(['message-requests']);
    } catch (error) {
      toast({
        title: "錯誤",
        description: "無法接受請求",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDecline = async (requestId: string) => {
    setLoading(true);
    try {
      // TODO: Call decline endpoint using generated SDK
      // await declineMessageRequest({ request_id: requestId });
      
      toast({
        title: "已拒絕",
        description: "此請求已標記為「拒絕」",
      });
      
      // Refresh list
      // queryClient.invalidateQueries(['message-requests']);
    } catch (error) {
      toast({
        title: "錯誤",
        description: "無法拒絕請求",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (requests.length === 0) {
    return (
      <div className="text-center text-muted-foreground text-sm py-12">
        目前沒有請求
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {requests.map((request) => (
        <Card key={request.id} className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-black text-foreground">來自 User {request.sender_id.slice(0, 8)}</p>
              <p className="text-[11px] text-muted-foreground">引用貼文：{request.post_id || '—'}</p>
              <p className="text-[11px] text-foreground/80 mt-2">{request.initial_message}</p>
            </div>
            <span className="bg-amber-50 text-amber-700 text-[10px] px-2 py-1 rounded-full font-black">待處理</span>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <Button
              onClick={() => handleAccept(request.id)}
              disabled={loading}
              className="h-11 rounded-2xl bg-slate-900 text-white font-black hover:bg-slate-800"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : '接受'}
            </Button>
            <Button
              variant="outline"
              onClick={() => handleDecline(request.id)}
              disabled={loading}
              className="h-11 rounded-2xl border border-border bg-card font-black hover:bg-muted"
            >
              拒絕
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}
