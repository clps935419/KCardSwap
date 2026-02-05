/**
 * PostImages - Component to display images attached to a post
 * Phase 9: Uses signed read URLs for secure image access
 */
import React from 'react';
import { Image, ActivityIndicator } from 'react-native';

import { Box, Text } from '@/src/shared/ui/components';
import { useReadMediaUrls } from '@/src/features/media/hooks/useReadMediaUrls';

interface PostImagesProps {
  mediaAssetIds: string[];
  maxDisplay?: number;
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
  const { data, isLoading, error } = useReadMediaUrls(mediaAssetIds);

  // Don't render if no media
  if (!mediaAssetIds || mediaAssetIds.length === 0) {
    return null;
  }

  // Show loading state
  if (isLoading) {
    return (
      <Box className="h-48 justify-center items-center bg-gray-100 rounded-lg">
        <ActivityIndicator size="large" color="#4F46E5" />
        <Text className="mt-2 text-gray-500">載入圖片中...</Text>
      </Box>
    );
  }

  // Show error state
  if (error) {
    return (
      <Box className="h-48 justify-center items-center bg-red-50 rounded-lg">
        <Text className="text-red-600">無法載入圖片</Text>
      </Box>
    );
  }

  const urls = data?.data?.urls || {};
  const imagesToShow = mediaAssetIds.slice(0, maxDisplay);
  const remainingCount = mediaAssetIds.length - maxDisplay;

  return (
    <Box className="flex-row flex-wrap gap-2 mt-2">
      {imagesToShow.map((mediaId, index) => {
        const imageUrl = urls[mediaId];

        if (!imageUrl) {
          return null;
        }

        // Show count overlay on last image if there are more
        const isLast = index === imagesToShow.length - 1;
        const showOverlay = isLast && remainingCount > 0;

        return (
          <Box key={mediaId} className="relative">
            <Image
              source={{ uri: imageUrl }}
              style={{
                width: imagesToShow.length === 1 ? 320 : 156,
                height: imagesToShow.length === 1 ? 240 : 120,
                borderRadius: 8,
              }}
              resizeMode="cover"
            />
            {showOverlay && (
              <Box
                className="absolute inset-0 bg-black/50 rounded-lg justify-center items-center"
              >
                <Text className="text-white text-xl font-bold">
                  +{remainingCount}
                </Text>
              </Box>
            )}
          </Box>
        );
      })}
    </Box>
  );
}
