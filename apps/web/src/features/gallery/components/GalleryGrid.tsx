"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { GalleryCardResponse } from "@/shared/api/generated";

interface GalleryGridProps {
  cards: GalleryCardResponse[];
  isOwner?: boolean;
  onDelete?: (cardId: string) => void;
}

export function GalleryGrid({ cards, isOwner = false, onDelete }: GalleryGridProps) {
  if (cards.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No cards in gallery yet.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.id} className="overflow-hidden hover:shadow-lg transition-shadow">
          <div className="aspect-[3/4] relative bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900">
            {card.media_asset_id ? (
              <img
                src={`/api/v1/media/${card.media_asset_id}/download`}
                alt={card.title}
                className="object-cover w-full h-full"
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <span className="text-4xl">🎴</span>
              </div>
            )}
          </div>
          
          <div className="p-4 space-y-2">
            <h3 className="font-semibold text-lg truncate">{card.title}</h3>
            
            <div className="flex flex-wrap gap-1">
              <Badge variant="secondary">{card.idol_name}</Badge>
              {card.era && <Badge variant="outline">{card.era}</Badge>}
            </div>
            
            {card.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {card.description}
              </p>
            )}
            
            {isOwner && onDelete && (
              <button
                onClick={() => onDelete(card.id)}
                className="text-sm text-destructive hover:underline mt-2"
              >
                Delete
              </button>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}
