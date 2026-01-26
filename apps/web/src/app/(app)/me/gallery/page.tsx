'use client'

import { logout } from '@/lib/google-oauth'
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

export default function MyGalleryPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [allowStrangerDM, setAllowStrangerDM] = useState(true)
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
        description: '無法刪除: ' + error.message,
        variant: 'destructive',
      })
    },
  })

  const handleDelete = (cardId: string) => {
    if (confirm('確定要刪除這張小卡嗎？')) {
      deleteMutation.mutate(cardId)
    }
  }

  const handleCreateSuccess = () => {
    setIsCreateDialogOpen(false)
    queryClient.invalidateQueries({ queryKey: ['my-gallery'] })
    toast({
      title: '已新增',
      description: '相簿小卡已加入清單',
    })
  }

  const toggleStrangerDM = () => {
    setAllowStrangerDM(!allowStrangerDM)
    toast({
      title: '隱私設定',
      description: `陌生人私訊：${!allowStrangerDM ? '開啟' : '關閉'}`,
    })
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      {/* Header Card */}
      <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-black text-foreground">相簿小卡</p>
            <p className="text-[11px] text-muted-foreground">可新增 / 刪除 / 排序；不含交換狀態</p>
          </div>
          <span className="bg-primary-50 text-primary-700 text-[10px] px-2 py-1 rounded-full font-black">
            V2
          </span>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3">
          <Button
            onClick={toggleStrangerDM}
            variant="outline"
            className="h-12 rounded-2xl border-border bg-card font-black hover:bg-muted"
          >
            陌生人私訊：
            <span className={allowStrangerDM ? 'text-emerald-600' : 'text-rose-600'}>
              {allowStrangerDM ? '開' : '關'}
            </span>
          </Button>
          <Button
            onClick={() => setIsCreateDialogOpen(true)}
            className="h-12 rounded-2xl bg-slate-900 text-white font-black shadow-xl hover:bg-slate-800"
          >
            新增小卡
          </Button>
        </div>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="p-4 rounded-2xl">
              <div className="flex items-start gap-3">
                <Skeleton className="w-11 h-11 rounded-2xl" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
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
      {data && (
        <>
          {data.items && data.items.length > 0 ? (
            <GalleryGrid cards={data.items || []} isOwner={true} onDelete={handleDelete} />
          ) : (
            <div className="text-center text-muted-foreground text-sm py-12">相簿目前沒有內容</div>
          )}
        </>
      )}

      {/* Logout Section */}
      <Card className="p-5 rounded-2xl border border-border/30 bg-card shadow-sm">
        <div className="space-y-3">
          <div>
            <p className="text-sm font-black text-foreground">帳號管理</p>
            <p className="text-[11px] text-muted-foreground">登出後需重新登入才能使用</p>
          </div>
          <Button
            onClick={() => logout()}
            variant="outline"
            className="w-full h-12 rounded-2xl border-border bg-card font-black hover:bg-muted hover:text-destructive"
          >
            登出
          </Button>
        </div>
      </Card>

      {/* Create Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="sm:max-w-[500px] rounded-2xl">
          <DialogHeader>
            <DialogTitle>新增相簿小卡</DialogTitle>
          </DialogHeader>
          <GalleryCreateCardForm onSuccess={handleCreateSuccess} />
        </DialogContent>
      </Dialog>
    </div>
  )
}
