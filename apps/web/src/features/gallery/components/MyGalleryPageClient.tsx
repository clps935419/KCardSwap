'use client'

import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/components/ui/use-toast'
import { GalleryCreateCardForm } from '@/features/gallery/components/GalleryCreateCardForm'
import { GalleryGrid } from '@/features/gallery/components/GalleryGrid'
import { useDeleteGalleryCard, useMyGalleryCards } from '@/shared/api/hooks/gallery'

export function MyGalleryPageClient() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const { data, isLoading, error } = useMyGalleryCards()

  const deleteMutation = useDeleteGalleryCard({
    onSuccess: () => {
      toast({
        title: '已刪除',
        description: '相簿小卡已移除',
      })
    },
    onError: error => {
      toast({
        title: '錯誤',
        description: `無法刪除: ${error.message}`,
        variant: 'destructive',
      })
    },
  })

  const handleDelete = (cardId: string) => {
    deleteMutation.mutate(cardId)
  }

  const handleCreateSuccess = () => {
    setIsCreateDialogOpen(false)
    queryClient.invalidateQueries({ queryKey: ['my-gallery'] })
    toast({
      title: '已新增',
      description: '相簿小卡已加入清單',
    })
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      {/* Gallery Header */}
      <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-black text-foreground">相簿小卡</p>
          </div>
        </div>

        <div className="mt-4">
          <Button
            onClick={() => setIsCreateDialogOpen(true)}
            className="w-full h-12 rounded-2xl bg-slate-900 text-white font-black shadow-xl hover:bg-slate-800"
          >
            新增小卡
          </Button>
        </div>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card
              key={`skeleton-${i}`}
              className="rounded-2xl border border-border/30 bg-card shadow-sm overflow-hidden"
            >
              <div className="relative aspect-[4/5] bg-muted/60">
                <Skeleton className="absolute inset-0 h-full w-full rounded-none" />
              </div>
              <div className="px-3 py-2 flex items-center justify-between">
                <div className="space-y-2">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-3 w-12" />
                </div>
                <Skeleton className="h-8 w-14 rounded-full" />
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="text-center py-8 text-destructive">
          <p>載入相簿卡片時發生錯誤，請稍後再試</p>
        </div>
      )}

      {/* Gallery Cards */}
      {data &&
        (data.items.length > 0 ? (
          <GalleryGrid cards={data.items} isOwner={true} onDelete={handleDelete} />
        ) : (
          <div className="text-center text-muted-foreground text-sm py-12">相簿目前沒有內容</div>
        ))}

      {/* Create Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="sm:max-w-[500px] max-h-[85vh] rounded-2xl p-0 overflow-hidden flex flex-col">
          <DialogHeader className="px-6 pt-6 pb-3 border-b border-border/30">
            <DialogTitle>新增相簿小卡</DialogTitle>
          </DialogHeader>
          <div className="px-6 pb-6 overflow-y-auto flex-1 min-h-0">
            <GalleryCreateCardForm onSuccess={handleCreateSuccess} />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
