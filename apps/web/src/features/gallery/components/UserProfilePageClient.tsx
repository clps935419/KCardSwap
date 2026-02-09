'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { GalleryGrid } from '@/features/gallery/components/GalleryGrid'
import { useUserGalleryCards } from '@/shared/api/hooks/gallery'

interface UserProfilePageClientProps {
  userId: string
}

export function UserProfilePageClient({ userId }: UserProfilePageClientProps) {
  const { data, isLoading, error } = useUserGalleryCards(userId)

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-2xl">使用者檔案</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">使用者代碼：{userId}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">相簿小卡</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <div key={`skeleton-${i}`} className="space-y-2">
                  <Skeleton className="aspect-[3/4] w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="text-center py-8 text-destructive">
              <p>載入相簿小卡時發生錯誤，請稍後再試。</p>
            </div>
          )}

          {data && <GalleryGrid cards={data.items || []} isOwner={false} />}
        </CardContent>
      </Card>
    </div>
  )
}
