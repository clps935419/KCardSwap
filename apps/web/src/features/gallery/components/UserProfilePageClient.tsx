'use client'

import { Skeleton } from '@/components/ui/skeleton'
import { UserAvatar } from '@/components/ui/user-avatar'
import { GalleryGrid } from '@/features/gallery/components/GalleryGrid'
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
    <div className="mx-auto w-full max-w-3xl min-h-screen bg-background">
      {/* IG-style Profile Header */}
      {isLoadingProfile && (
        <div className="flex items-start gap-4 border-b border-border/30 px-5 py-5 sm:px-6">
          <Skeleton className="h-20 w-20 rounded-full" />
          <div className="flex-1 space-y-2 pt-1">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-4 w-full max-w-md" />
            <Skeleton className="h-4 w-2/3 max-w-sm" />
          </div>
        </div>
      )}

      {profileError && (
        <div className="px-5 py-4 sm:px-6">
          <div className="rounded-2xl border border-destructive/20 bg-destructive/5 px-4 py-3 text-destructive">
            <p className="text-sm font-semibold">載入使用者資料時發生錯誤</p>
            <p className="text-xs mt-1">
              {profileError instanceof Error ? profileError.message : '請稍後再試或聯繫技術支援'}
            </p>
          </div>
        </div>
      )}

      {profileData?.data && (
        <header className="border-b border-border/30 px-5 py-5 sm:px-6">
          <div className="flex items-start gap-4">
            <UserAvatar
              avatarUrl={profileData.data.avatar_url || undefined}
              nickname={profileData.data.nickname || undefined}
              userId={profileData.data.user_id}
              size="lg"
              className="h-20 w-20 text-xl"
            />

            <div className="min-w-0 flex-1 pt-1">
              <h1 className="text-2xl font-bold leading-tight truncate">
                {profileData.data.nickname || 'Anonymous'}
              </h1>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground whitespace-pre-line">
                {profileData.data.bio?.trim() || '尚未填寫個人簡介'}
              </p>
            </div>
          </div>
        </header>
      )}

      <div>
        {isLoadingGallery && (
          <div className="grid grid-cols-3 gap-px bg-border/20">
            {Array.from({ length: 12 }).map((_, i) => (
              <Skeleton
                key={`skeleton-${i}`}
                className="aspect-square w-full rounded-none bg-muted/40"
              />
            ))}
          </div>
        )}

        {galleryError && (
          <div className="px-5 py-4 sm:px-6">
            <div className="text-center py-8 text-destructive">
              <p className="font-semibold mb-2">載入相簿小卡時發生錯誤</p>
              <p className="text-sm">
                {galleryError instanceof Error ? galleryError.message : '請稍後再試或聯繫技術支援'}
              </p>
            </div>
          </div>
        )}

        {galleryData && (
          <GalleryGrid cards={galleryData.data.items || []} isOwner={false} variant="wall" />
        )}
      </div>
    </div>
  )
}
