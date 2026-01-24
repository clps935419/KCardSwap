/**
 * Inbox Page - Shows message requests and threads
 * 
 * Implements FR-016: Inbox clearly separates Requests vs Threads
 */
"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageRequestsList } from "@/features/inbox/components/MessageRequestsList";
import { ThreadsList } from "@/features/inbox/components/ThreadsList";

export default function InboxPage() {
  const [activeTab, setActiveTab] = useState<string>("threads");

  return (
    <div className="container max-w-4xl py-8">
      <Card>
        <CardHeader>
          <CardTitle>Inbox</CardTitle>
          <CardDescription>
            Manage your message requests and conversations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="threads">Threads</TabsTrigger>
              <TabsTrigger value="requests">Requests</TabsTrigger>
            </TabsList>
            
            <TabsContent value="threads" className="mt-6">
              <ThreadsList />
            </TabsContent>
            
            <TabsContent value="requests" className="mt-6">
              <MessageRequestsList />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
