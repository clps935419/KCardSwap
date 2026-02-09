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
          <CardTitle className="text-2xl">User Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">User ID: {userId}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Gallery Cards</CardTitle>
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
              <p>Failed to load gallery cards. Please try again later.</p>
            </div>
          )}

          {data && <GalleryGrid cards={data.items || []} isOwner={false} />}
        </CardContent>
      </Card>
    </div>
  )
}
