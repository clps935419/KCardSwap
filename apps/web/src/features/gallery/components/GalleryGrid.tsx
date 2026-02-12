'use client'

import { Trash2, X } from 'lucide-react'
import Image from 'next/image'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { useReadMediaUrls } from '@/features/media/hooks/useReadMediaUrls'
import { cn } from '@/lib/utils'
import type { GalleryCardResponse } from '@/shared/api/generated'

const BLUR_DATA_URL =
  'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNlZWVlZWUiLz48L3N2Zz4='

interface GalleryGridProps {
  cards: GalleryCardResponse[]
  isOwner?: boolean
  onDelete?: (cardId: string) => void
  variant?: 'cards' | 'wall'
}

function getDisplayText(value?: string | null, fallback = '未填寫') {
  const normalized = value?.trim()
  return normalized && normalized.length > 0 ? normalized : fallback
}

function formatDateTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function clampText(value: string, maxLength: number) {
  if (value.length <= maxLength) return value
  return `${value.slice(0, Math.max(0, maxLength - 1))}…`
}

export function GalleryGrid({
  cards,
  isOwner = false,
  onDelete,
  variant = 'cards',
}: GalleryGridProps) {
  const mediaAssetIds = cards
    .map(card => card.media_asset_id)
    .filter((mediaId): mediaId is string => Boolean(mediaId))
  const mediaUrlsQuery = useReadMediaUrls(mediaAssetIds)
  const mediaUrls = mediaUrlsQuery.data?.data?.urls ?? {}
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<GalleryCardResponse | null>(null)
  const [thumbnailLoadedMap, setThumbnailLoadedMap] = useState<Record<string, boolean>>({})
  const [modalImageLoaded, setModalImageLoaded] = useState(false)
  const [isDialogInfoCollapsed, setIsDialogInfoCollapsed] = useState(false)
  const [dialogImageNaturalSize, setDialogImageNaturalSize] = useState<{
    width: number
    height: number
  } | null>(null)
  const [dialogInfoShiftPx, setDialogInfoShiftPx] = useState(0)
  const dialogImageContainerRef = useRef<HTMLDivElement | null>(null)
  const dialogInfoPanelRef = useRef<HTMLDivElement | null>(null)
  const selectedCard = useMemo(
    () => cards.find(card => card.id === selectedCardId) || null,
    [cards, selectedCardId]
  )
  const selectedMediaUrl = selectedCard?.media_asset_id
    ? mediaUrls[selectedCard.media_asset_id]
    : null

  const handleConfirmDelete = () => {
    if (!deleteTarget || !onDelete) return
    onDelete(deleteTarget.id)
    setDeleteTarget(null)
  }

  useEffect(() => {
    const recalculateDialogInfoShift = () => {
      if (
        !dialogImageNaturalSize ||
        !dialogImageContainerRef.current ||
        !dialogInfoPanelRef.current
      ) {
        setDialogInfoShiftPx(0)
        return
      }

      const containerWidth = dialogImageContainerRef.current.clientWidth
      const containerHeight = dialogImageContainerRef.current.clientHeight
      const panelHeight = dialogInfoPanelRef.current.offsetHeight

      if (containerWidth <= 0 || containerHeight <= 0 || panelHeight <= 0) {
        setDialogInfoShiftPx(0)
        return
      }

      const widthScale = containerWidth / dialogImageNaturalSize.width
      const heightScale = containerHeight / dialogImageNaturalSize.height
      const scale = Math.min(widthScale, heightScale)
      const displayedImageHeight = dialogImageNaturalSize.height * scale
      const visibleImageHeightWhenPanelOpen = containerHeight - panelHeight
      const overlapHeight = Math.max(0, displayedImageHeight - visibleImageHeightWhenPanelOpen)

      setDialogInfoShiftPx(Math.min(overlapHeight, panelHeight))
    }

    recalculateDialogInfoShift()

    const resizeObserver = new ResizeObserver(() => {
      recalculateDialogInfoShift()
    })

    if (dialogImageContainerRef.current) {
      resizeObserver.observe(dialogImageContainerRef.current)
    }

    if (dialogInfoPanelRef.current) {
      resizeObserver.observe(dialogInfoPanelRef.current)
    }

    window.addEventListener('resize', recalculateDialogInfoShift)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', recalculateDialogInfoShift)
    }
  }, [dialogImageNaturalSize])

  if (cards.length === 0) {
    return <div className="text-center text-muted-foreground text-sm py-12">相簿目前沒有內容</div>
  }

  return (
    <>
      <div
        className={cn(
          'grid',
          variant === 'wall'
            ? 'grid-cols-3 gap-px'
            : 'grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3'
        )}
      >
        {cards.map((card, _idx) => {
          const thumbnailUrl = card.media_asset_id ? mediaUrls[card.media_asset_id] : null
          const isThumbnailLoaded = thumbnailLoadedMap[card.id]
          return (
            <button
              key={card.id}
              type="button"
              onClick={() => {
                setModalImageLoaded(false)
                setIsDialogInfoCollapsed(false)
                setDialogImageNaturalSize(null)
                setSelectedCardId(card.id)
              }}
              className={cn(
                'group h-auto w-full text-left',
                variant === 'wall' &&
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card'
              )}
            >
              <Card
                className={cn(
                  'overflow-hidden',
                  variant === 'wall'
                    ? 'rounded-none border border-border/20 bg-card shadow-none'
                    : 'rounded-2xl border border-border/30 bg-card shadow-sm transition-transform duration-200 group-hover:-translate-y-0.5'
                )}
              >
                <div
                  className={cn(
                    'relative bg-muted/60',
                    variant === 'wall' ? 'aspect-square' : 'aspect-[4/5]'
                  )}
                >
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
                  {variant === 'cards' && (
                    <>
                      <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-black/60 to-transparent" />
                      <div className="absolute bottom-3 left-3 right-3">
                        <p className="text-[11px] font-black text-white truncate">{card.title}</p>
                        <p className="text-[10px] text-white/70 truncate">
                          {card.idol_name || '—'}
                        </p>
                      </div>
                    </>
                  )}
                </div>
                {variant === 'cards' && (
                  <div className="px-3 py-2 flex items-center justify-between">
                    <span className="text-[10px] font-bold text-muted-foreground">&nbsp;</span>
                    {isOwner && onDelete && (
                      <Button
                        onClick={event => {
                          event.stopPropagation()
                          setDeleteTarget(card)
                        }}
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8  p-0 text-rose-700 hover:bg-rose-100"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        <span className="sr-only">刪除</span>
                      </Button>
                    )}
                  </div>
                )}
              </Card>
            </button>
          )
        })}
      </div>

      {selectedCard && (
        <Dialog
          open={!!selectedCard}
          onOpenChange={open => {
            if (!open) {
              setModalImageLoaded(false)
              setIsDialogInfoCollapsed(false)
              setDialogImageNaturalSize(null)
              setDialogInfoShiftPx(0)
              setSelectedCardId(null)
            }
          }}
        >
          <DialogContent className="!fixed !inset-0 !left-0 !top-0 !translate-x-0 !translate-y-0 !w-screen !h-screen !max-w-none !max-h-none !rounded-none !border-0 !bg-background !p-0 !gap-0 !overflow-hidden !flex !flex-col sm:!static sm:!inset-auto sm:!w-[92vw] sm:!max-w-[520px] sm:!h-auto sm:!max-h-[80vh] sm:!rounded-2xl sm:!border sm:!border-border">
            <DialogClose className="absolute right-3 top-3 z-20 rounded-full bg-white/90 p-2 text-foreground shadow-md transition hover:bg-white">
              <X className="h-4 w-4" />
              <span className="sr-only">關閉</span>
            </DialogClose>
            <DialogTitle className="sr-only">{selectedCard.title}</DialogTitle>
            <DialogDescription className="sr-only">圖片預覽</DialogDescription>
            <div ref={dialogImageContainerRef} className="relative flex-1 min-h-0 overflow-hidden">
              <div className="absolute inset-0 bg-muted">
                {selectedMediaUrl ? (
                  <>
                    {!modalImageLoaded && (
                      <Skeleton className="absolute inset-0 h-full w-full rounded-none" />
                    )}
                    <Image
                      src={selectedMediaUrl}
                      alt={selectedCard.title}
                      fill
                      className="object-contain object-top"
                      sizes="(max-width: 640px) 100vw, 520px"
                      unoptimized
                      placeholder="blur"
                      blurDataURL={BLUR_DATA_URL}
                      onLoadingComplete={img => {
                        setDialogImageNaturalSize({
                          width: img.naturalWidth,
                          height: img.naturalHeight,
                        })
                      }}
                      onLoad={() => setModalImageLoaded(true)}
                    />
                  </>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-3xl text-muted-foreground">
                    {selectedCard.media_asset_id ? '🖼️' : '🃏'}
                  </div>
                )}
              </div>

              {!isDialogInfoCollapsed && (
                <button
                  type="button"
                  onClick={() => setIsDialogInfoCollapsed(true)}
                  className="absolute inset-0 z-10"
                  aria-label="將資訊欄下移以顯示更多圖片"
                />
              )}

              <div
                ref={dialogInfoPanelRef}
                className="absolute inset-x-0 bottom-0 z-20 border-t border-border bg-background/95 backdrop-blur transition-transform duration-300 ease-out"
                style={{
                  transform: `translateY(${isDialogInfoCollapsed ? dialogInfoShiftPx : 0}px)`,
                }}
              >
                {isDialogInfoCollapsed && (
                  <button
                    type="button"
                    onClick={() => setIsDialogInfoCollapsed(false)}
                    className="absolute inset-0 z-10"
                    aria-label="將資訊欄移回原本位置"
                  />
                )}

                <div className="h-1 w-10 rounded-full bg-border/70 mx-auto my-2" />

                <div className="h-[50vh] overflow-auto px-4 pb-4 pt-1">
                  <div className="space-y-3">
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-foreground">標題</p>
                      <p className="text-sm text-muted-foreground">
                        {getDisplayText(selectedCard.title, '未命名卡片')}
                      </p>
                    </div>

                    <div className="space-y-1">
                      <p className="text-xs font-medium text-foreground">偶像名稱</p>
                      <p className="text-sm text-muted-foreground">
                        {getDisplayText(selectedCard.idol_name)}
                      </p>
                    </div>

                    <div className="space-y-1">
                      <p className="text-xs font-medium text-foreground">時期</p>
                      <p className="text-sm text-muted-foreground">
                        {getDisplayText(selectedCard.era)}
                      </p>
                    </div>

                    <div className="space-y-1">
                      <p className="text-xs font-medium text-foreground">備註內容</p>
                      <p className="whitespace-pre-wrap break-words text-sm text-muted-foreground">
                        {getDisplayText(selectedCard.description, '尚未新增備註')}
                      </p>
                    </div>

                    <div className="space-y-1">
                      <p className="text-xs font-medium text-foreground">建立與更新時間</p>
                      <p className="text-xs text-muted-foreground">
                        建立：{formatDateTime(selectedCard.created_at)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        更新：{formatDateTime(selectedCard.updated_at)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      <Dialog open={!!deleteTarget} onOpenChange={open => !open && setDeleteTarget(null)}>
        <DialogContent className="max-w-sm rounded-3xl border border-border/60 bg-card/95 p-6">
          <DialogHeader className="text-center">
            <DialogTitle className="text-lg font-black leading-snug">
              刪除「{clampText(getDisplayText(deleteTarget?.title, '這張卡片'), 22)}」？
            </DialogTitle>
          </DialogHeader>
          <DialogFooter className="flex-col gap-2 sm:flex-col sm:space-x-0">
            <Button
              type="button"
              variant="destructive"
              onClick={handleConfirmDelete}
              className="h-11 w-full rounded-2xl text-sm font-black"
            >
              確認刪除
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setDeleteTarget(null)}
              className="h-11 w-full rounded-2xl text-sm font-black"
            >
              取消
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
