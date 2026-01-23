/**
 * MessageRequestsList Component
 * 
 * Displays pending message requests for the current user
 */
"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, X, Loader2 } from "lucide-react";
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
        title: "Request accepted",
        description: "You can now chat with this user",
      });
      
      // Refresh list
      // queryClient.invalidateQueries(['message-requests']);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to accept request",
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
        title: "Request declined",
      });
      
      // Refresh list
      // queryClient.invalidateQueries(['message-requests']);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to decline request",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (requests.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No pending message requests</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {requests.map((request) => (
        <Card key={request.id} className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="font-medium">Message Request from User {request.sender_id.slice(0, 8)}</p>
              <p className="text-sm text-muted-foreground mt-2">{request.initial_message}</p>
              <p className="text-xs text-muted-foreground mt-2">
                {new Date(request.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="flex gap-2 ml-4">
              <Button
                size="sm"
                onClick={() => handleAccept(request.id)}
                disabled={loading}
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
                Accept
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleDecline(request.id)}
                disabled={loading}
              >
                <X className="h-4 w-4" />
                Decline
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
