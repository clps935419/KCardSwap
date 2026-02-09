/**
 * PostImages - Component to display images attached to a post (Web)
 * Phase 9: Uses signed read URLs for secure image access
 */
'use client'

import { Loader2 } from 'lucide-react'
import Image from 'next/image'
import { useReadMediaUrls } from '@/features/media/hooks/useReadMediaUrls'

interface PostImagesProps {
  mediaAssetIds: string[]
  maxDisplay?: number
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
export function PostImages({ mediaAssetIds, maxDisplay = 4 }: PostImagesProps) {
  const { data, isLoading, error } = useReadMediaUrls(mediaAssetIds)

  // Don't render if no media
  if (!mediaAssetIds || mediaAssetIds.length === 0) {
    return null
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="h-48 flex items-center justify-center bg-muted/30 rounded-lg">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        <span className="ml-2 text-sm text-muted-foreground">載入圖片中...</span>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="h-48 flex items-center justify-center bg-destructive/10 rounded-lg">
        <span className="text-sm text-destructive">無法載入圖片</span>
      </div>
    )
  }

  const urls = data?.data?.urls || {}
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
