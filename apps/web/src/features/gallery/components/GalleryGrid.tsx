'use client'

import { X } from 'lucide-react'
import Image from 'next/image'
import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { useReadMediaUrls } from '@/features/media/hooks/useReadMediaUrls'
import type { GalleryCardResponse } from '@/shared/api/generated'

const BLUR_DATA_URL =
  'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNlZWVlZWUiLz48L3N2Zz4='

interface GalleryGridProps {
  cards: GalleryCardResponse[]
  isOwner?: boolean
  onDelete?: (cardId: string) => void
}

export function GalleryGrid({ cards, isOwner = false, onDelete }: GalleryGridProps) {
  const mediaAssetIds = cards
    .map(card => card.media_asset_id)
    .filter((mediaId): mediaId is string => Boolean(mediaId))
  const mediaUrlsQuery = useReadMediaUrls(mediaAssetIds)
  const mediaUrls = mediaUrlsQuery.data?.data?.urls ?? {}
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null)
  const [thumbnailLoadedMap, setThumbnailLoadedMap] = useState<Record<string, boolean>>({})
  const [modalImageLoaded, setModalImageLoaded] = useState(false)
  const selectedCard = useMemo(
    () => cards.find(card => card.id === selectedCardId) || null,
    [cards, selectedCardId]
  )
  const selectedMediaUrl = selectedCard?.media_asset_id
    ? mediaUrls[selectedCard.media_asset_id]
    : null

  if (cards.length === 0) {
    return <div className="text-center text-muted-foreground text-sm py-12">相簿目前沒有內容</div>
  }

  return (
    <>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card, _idx) => {
          const thumbnailUrl = card.media_asset_id ? mediaUrls[card.media_asset_id] : null
          const isThumbnailLoaded = thumbnailLoadedMap[card.id]
          return (
            <button
              key={card.id}
              type="button"
              onClick={() => {
                setModalImageLoaded(false)
                setSelectedCardId(card.id)
              }}
              className="group h-auto w-full text-left"
            >
              <Card className="rounded-2xl border border-border/30 bg-card shadow-sm overflow-hidden transition-transform duration-200 group-hover:-translate-y-0.5">
                <div className="relative aspect-[4/5] bg-muted/60">
                  {thumbnailUrl ? (
                    <>
                      {!isThumbnailLoaded && (
                        <Skeleton className="absolute inset-0 h-full w-full rounded-none" />
                      )}
                      <Image
                        src={thumbnailUrl}
                        alt={card.title}
                        fill
                        className="object-cover"
                        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                        unoptimized
                        placeholder="blur"
                        blurDataURL={BLUR_DATA_URL}
                        onLoad={() => {
                          setThumbnailLoadedMap(prev => ({ ...prev, [card.id]: true }))
                        }}
                      />
                    </>
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
        <Dialog
          open={!!selectedCard}
          onOpenChange={() => {
            setModalImageLoaded(false)
            setSelectedCardId(null)
          }}
        >
          <DialogContent className="!fixed !inset-0 !left-0 !top-0 !translate-x-0 !translate-y-0 !w-screen !h-screen !max-w-none !max-h-none !rounded-none !border-0 !bg-background !p-0 !gap-0 !overflow-hidden !flex !flex-col sm:!static sm:!inset-auto sm:!w-[92vw] sm:!max-w-[520px] sm:!h-auto sm:!max-h-[80vh] sm:!rounded-2xl sm:!border sm:!border-border">
            <DialogClose className="absolute right-3 top-3 z-20 rounded-full bg-white/90 p-2 text-foreground shadow-md transition hover:bg-white">
              <X className="h-4 w-4" />
              <span className="sr-only">關閉</span>
            </DialogClose>
            <DialogTitle className="sr-only">{selectedCard.title}</DialogTitle>
            <DialogDescription className="sr-only">圖片預覽</DialogDescription>
            <div className="flex-1 min-h-0">
              <div className="relative h-full w-full bg-muted">
                {selectedMediaUrl ? (
                  <>
                    {!modalImageLoaded && (
                      <Skeleton className="absolute inset-0 h-full w-full rounded-none" />
                    )}
                    <Image
                      src={selectedMediaUrl}
                      alt={selectedCard.title}
                      fill
                      className="object-contain"
                      sizes="(max-width: 640px) 100vw, 520px"
                      unoptimized
                      placeholder="blur"
                      blurDataURL={BLUR_DATA_URL}
                      onLoad={() => setModalImageLoaded(true)}
                    />
                  </>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-3xl text-muted-foreground">
                    {selectedCard.media_asset_id ? '🖼️' : '🃏'}
                  </div>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  )
}
