'use client'

import Image from 'next/image'
import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useReadMediaUrls } from '@/features/media/hooks/useReadMediaUrls'
import type { GalleryCardResponse } from '@/shared/api/generated'

interface GalleryGridProps {
  cards: GalleryCardResponse[]
  isOwner?: boolean
  onDelete?: (cardId: string) => void
  onMoveUp?: (index: number) => void
  onMoveDown?: (index: number) => void
}

export function GalleryGrid({
  cards,
  isOwner = false,
  onDelete,
  onMoveUp,
  onMoveDown,
}: GalleryGridProps) {
  if (cards.length === 0) {
    return <div className="text-center text-muted-foreground text-sm py-12">相簿目前沒有內容</div>
  }

  const mediaAssetIds = cards
    .map(card => card.media_asset_id)
    .filter((mediaId): mediaId is string => Boolean(mediaId))
  const mediaUrlsQuery = useReadMediaUrls(mediaAssetIds)
  const mediaUrls = mediaUrlsQuery.data?.data?.urls ?? {}
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null)
  const selectedCard = useMemo(
    () => cards.find(card => card.id === selectedCardId) || null,
    [cards, selectedCardId]
  )
  const selectedMediaUrl = selectedCard?.media_asset_id
    ? mediaUrls[selectedCard.media_asset_id]
    : null

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {cards.map((card, idx) => {
          const thumbnailUrl = card.media_asset_id ? mediaUrls[card.media_asset_id] : null
          return (
            <button
              key={card.id}
              type="button"
              onClick={() => setSelectedCardId(card.id)}
              className="group text-left"
            >
              <Card className="rounded-2xl border border-border/30 bg-card shadow-sm overflow-hidden transition-transform duration-200 group-hover:-translate-y-0.5">
                <div className="relative aspect-square bg-muted/60">
                  {thumbnailUrl ? (
                    <Image
                      src={thumbnailUrl}
                      alt={card.title}
                      fill
                      className="object-cover"
                      sizes="(max-width: 640px) 50vw, 33vw"
                      unoptimized
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-2xl text-muted-foreground">
                      {card.media_asset_id ? '🖼️' : '🃏'}
                    </div>
                  )}
                  <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-black/60 to-transparent" />
                  <div className="absolute bottom-2 left-2 right-2">
                    <p className="text-[11px] font-black text-white truncate">{card.title}</p>
                    <p className="text-[10px] text-white/70 truncate">{card.idol_name || '—'}</p>
                  </div>
                </div>
                <div className="px-3 py-2 flex items-center justify-between">
                  <span className="text-[10px] font-bold text-muted-foreground">&nbsp;</span>
                  {isOwner && onDelete && (
                    <Button
                      onClick={event => {
                        event.stopPropagation()
                        onDelete(card.id)
                      }}
                      variant="outline"
                      size="sm"
                      className="h-8 rounded-full border-rose-200 bg-rose-50 px-3 text-[10px] font-black text-rose-700 hover:bg-rose-100"
                    >
                      刪除
                    </Button>
                  )}
                </div>
              </Card>
            </button>
          )
        })}
      </div>

      {selectedCard && (
        <Dialog open={!!selectedCard} onOpenChange={() => setSelectedCardId(null)}>
          <DialogContent className="sm:max-w-[520px] rounded-2xl p-0 overflow-hidden">
            <DialogHeader className="px-6 pt-6 pb-3 border-b border-border/30">
              <DialogTitle>{selectedCard.title}</DialogTitle>
            </DialogHeader>
            <div className="px-6 pb-6 space-y-4">
              <div className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl border border-border/30 bg-muted">
                {selectedMediaUrl ? (
                  <Image
                    src={selectedMediaUrl}
                    alt={selectedCard.title}
                    fill
                    className="object-cover"
                    sizes="(max-width: 640px) 100vw, 520px"
                    unoptimized
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-3xl text-muted-foreground">
                    {selectedCard.media_asset_id ? '🖼️' : '🃏'}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-slate-900 px-3 py-1 text-[10px] font-black text-white">
                    {selectedCard.idol_name || '未填偶像'}
                  </span>
                  <span className="rounded-full bg-muted px-3 py-1 text-[10px] font-bold text-muted-foreground">
                    {selectedCard.era || '年代未填'}
                  </span>
                </div>
                {selectedCard.description ? (
                  <p className="text-sm text-foreground/80 leading-relaxed">{selectedCard.description}</p>
                ) : (
                  <p className="text-sm text-muted-foreground">尚未填寫描述</p>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  )
}
