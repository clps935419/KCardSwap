'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { GalleryGrid } from '@/features/gallery/components/GalleryGrid'
import { ProfileHeader } from '@/features/profile/components'
import { useUserGalleryCards } from '@/shared/api/hooks/gallery'
import { useUserProfile } from '@/shared/api/hooks/profile'

interface UserProfilePageClientProps {
  userId: string
}

export function UserProfilePageClient({ userId }: UserProfilePageClientProps) {
  const {
    data: profileData,
    isLoading: isLoadingProfile,
    error: profileError,
  } = useUserProfile(userId)
  const {
    data: galleryData,
    isLoading: isLoadingGallery,
    error: galleryError,
  } = useUserGalleryCards(userId)

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Profile Header Section */}
      {isLoadingProfile && (
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center space-y-4">
              <Skeleton className="h-24 w-24 rounded-full" />
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-16 w-full max-w-md" />
            </div>
          </CardContent>
        </Card>
      )}

      {profileError && (
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="text-center text-destructive">
              <p>載入使用者資料時發生錯誤，請稍後再試。</p>
            </div>
          </CardContent>
        </Card>
      )}

      {profileData?.data && (
        <div className="mb-8">
          <ProfileHeader profile={profileData.data} />
        </div>
      )}

      {/* Gallery Cards Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">相簿小卡 📸</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingGallery && (
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

          {galleryError && (
            <div className="text-center py-8 text-destructive">
              <p>載入相簿小卡時發生錯誤，請稍後再試。</p>
            </div>
          )}

          {galleryData && <GalleryGrid cards={galleryData.items || []} isOwner={false} />}
        </CardContent>
      </Card>
    </div>
  )
}
