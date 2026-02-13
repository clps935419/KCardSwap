/**
 * PostImages - Component to display images attached to a post (Web)
 * Phase 9: Uses signed read URLs for secure image access
 */
'use client'

import { Loader2 } from 'lucide-react'
import Image from 'next/image'
import { useReadMediaUrls } from '@/features/media/hooks/useReadMediaUrls'

const BLUR_DATA_URL =
  'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNlZWVlZWUiLz48L3N2Zz4='

interface PostImagesProps {
  mediaAssetIds: string[]
  maxDisplay?: number
  preloadedUrls?: Record<string, string>
  isPreloadedUrlsLoading?: boolean
  hasPreloadedUrlsError?: boolean
}

/**
 * Component to display images from a post using signed URLs
 *
 * @param mediaAssetIds - Array of media asset IDs to display
 * @param maxDisplay - Maximum number of images to display (default: 4)
 *
 * @example
 * ```tsx
 * <PostImages mediaAssetIds={post.media_asset_ids} maxDisplay={4} />
 * ```
 */
export function PostImages({
  mediaAssetIds,
  maxDisplay = 4,
  preloadedUrls,
  isPreloadedUrlsLoading = false,
  hasPreloadedUrlsError = false,
}: PostImagesProps) {
  const usingPreloadedUrls = typeof preloadedUrls !== 'undefined'
  const { data, isLoading, error } = useReadMediaUrls(mediaAssetIds, {
    enabled: !usingPreloadedUrls,
  })

  // Don't render if no media
  if (!mediaAssetIds || mediaAssetIds.length === 0) {
    return null
  }

  const loading = usingPreloadedUrls ? isPreloadedUrlsLoading : isLoading
  const hasError = usingPreloadedUrls ? hasPreloadedUrlsError : !!error

  // Show loading state
  if (loading) {
    return (
      <div className="h-48 flex items-center justify-center bg-muted/30 rounded-lg">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        <span className="ml-2 text-sm text-muted-foreground">載入圖片中...</span>
      </div>
    )
  }

  // Show error state
  if (hasError) {
    return (
      <div className="h-48 flex items-center justify-center bg-destructive/10 rounded-lg">
        <span className="text-sm text-destructive">無法載入圖片</span>
      </div>
    )
  }

  const urls = preloadedUrls ?? data?.data?.urls ?? {}
  const imagesToShow = mediaAssetIds.slice(0, maxDisplay)
  const remainingCount = mediaAssetIds.length - maxDisplay
  const isSingle = imagesToShow.length === 1
  const imageWidth = isSingle ? 320 : 156
  const imageHeight = isSingle ? 240 : 120

  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {imagesToShow.map((mediaId, index) => {
        const imageUrl = urls[mediaId]

        if (!imageUrl) {
          return null
        }

        // Show count overlay on last image if there are more
        const isLast = index === imagesToShow.length - 1
        const showOverlay = isLast && remainingCount > 0

        return (
          <div key={mediaId} className="relative">
            <Image
              src={imageUrl}
              alt={`附件 ${index + 1}`}
              width={imageWidth}
              height={imageHeight}
              sizes={isSingle ? '320px' : '156px'}
              className="rounded-lg object-cover"
              unoptimized
              placeholder="blur"
              blurDataURL={BLUR_DATA_URL}
            />
            {showOverlay && (
              <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl font-bold">+{remainingCount}</span>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
