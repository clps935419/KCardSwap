"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { GalleryGrid } from "@/features/gallery/components/GalleryGrid";
import { GalleryCreateCardForm } from "@/features/gallery/components/GalleryCreateCardForm";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";

// TODO: Replace with generated SDK hooks once OpenAPI is updated
async function fetchMyGalleryCards() {
  const response = await fetch("/api/v1/gallery/cards/me", {
    credentials: "include",
  });
  
  if (!response.ok) {
    throw new Error("Failed to fetch gallery cards");
  }
  
  return response.json();
}

async function deleteGalleryCard(cardId: string) {
  const response = await fetch(`/api/v1/gallery/cards/${cardId}`, {
    method: "DELETE",
    credentials: "include",
  });
  
  if (!response.ok) {
    throw new Error("Failed to delete gallery card");
  }
  
  return true;
}

export default function MyGalleryPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ["my-gallery"],
    queryFn: fetchMyGalleryCards,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteGalleryCard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-gallery"] });
      toast({
        title: "Success",
        description: "Card deleted successfully",
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to delete card: " + error.message,
        variant: "destructive",
      });
    },
  });

  const handleDelete = (cardId: string) => {
    if (confirm("Are you sure you want to delete this card?")) {
      deleteMutation.mutate(cardId);
    }
  };

  const handleCreateSuccess = () => {
    setIsCreateDialogOpen(false);
    queryClient.invalidateQueries({ queryKey: ["my-gallery"] });
    toast({
      title: "Success",
      description: "Card created successfully",
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-2xl">My Gallery</CardTitle>
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Card
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="aspect-[3/4] w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="text-center py-8 text-destructive">
              <p>Failed to load gallery cards. Please try again later.</p>
            </div>
          )}

          {data && (
            <>
              <div className="mb-4 text-sm text-muted-foreground">
                Total cards: {data.total || 0}
              </div>
              <GalleryGrid 
                cards={data.items || []} 
                isOwner={true}
                onDelete={handleDelete}
              />
            </>
          )}
        </CardContent>
      </Card>

      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Add New Card</DialogTitle>
          </DialogHeader>
          <GalleryCreateCardForm onSuccess={handleCreateSuccess} />
        </DialogContent>
      </Dialog>
    </div>
  );
}
