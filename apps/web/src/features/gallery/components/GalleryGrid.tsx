"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { GalleryCardResponse } from "@/shared/api/generated";

interface GalleryGridProps {
  cards: GalleryCardResponse[];
  isOwner?: boolean;
  onDelete?: (cardId: string) => void;
  onMoveUp?: (index: number) => void;
  onMoveDown?: (index: number) => void;
}

export function GalleryGrid({ cards, isOwner = false, onDelete, onMoveUp, onMoveDown }: GalleryGridProps) {
  if (cards.length === 0) {
    return (
      <div className="text-center text-muted-foreground text-sm py-12">
        相簿目前沒有內容
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {cards.map((card, idx) => (
        <Card key={card.id} className="p-4 rounded-2xl shadow-sm border border-border/30 bg-card">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className="w-11 h-11 bg-primary-50 rounded-2xl flex items-center justify-center text-xl">
                {card.media_asset_id ? '🖼️' : '🃏'}
              </div>
              <div>
                <p className="text-sm font-black text-foreground">{card.title}</p>
                <p className="text-[11px] text-muted-foreground">{card.idol_name || '—'}</p>
                <p className="text-[10px] text-muted-foreground font-bold uppercase mt-1">
                  順序：{idx + 1}
                </p>
              </div>
            </div>
            
            {isOwner && (onMoveUp || onMoveDown) && (
              <div className="flex flex-col gap-2">
                {onMoveUp && (
                  <Button
                    onClick={() => onMoveUp(idx)}
                    disabled={idx === 0}
                    variant="outline"
                    size="sm"
                    className="w-10 h-10 rounded-2xl border-border bg-card font-black p-0"
                  >
                    ↑
                  </Button>
                )}
                {onMoveDown && (
                  <Button
                    onClick={() => onMoveDown(idx)}
                    disabled={idx === cards.length - 1}
                    variant="outline"
                    size="sm"
                    className="w-10 h-10 rounded-2xl border-border bg-card font-black p-0"
                  >
                    ↓
                  </Button>
                )}
              </div>
            )}
          </div>

          {isOwner && onDelete && (
            <div className="mt-3 flex items-center justify-end">
              <Button
                onClick={() => onDelete(card.id)}
                variant="outline"
                size="sm"
                className="px-3 py-2 rounded-xl bg-rose-50 border-rose-200 text-rose-700 text-[11px] font-black hover:bg-rose-100"
              >
                刪除
              </Button>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}
