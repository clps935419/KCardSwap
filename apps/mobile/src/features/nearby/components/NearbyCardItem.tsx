/**
 * Nearby Card Item Component
 * 顯示附近搜尋結果中的單一卡片
 */

import React from 'react';
import { Box, Text, Pressable } from '@/src/shared/ui/components';
import { Image } from 'react-native';
import type { NearbyCard } from '@/src/features/nearby/hooks';

interface NearbyCardItemProps {
  card: NearbyCard;
  onPress?: (card: NearbyCard) => void;
}

export function NearbyCardItem({ card, onPress }: NearbyCardItemProps) {
  const handlePress = () => {
    if (onPress) {
      onPress(card);
    }
  };

  const formatDistance = (km: number): string => {
    if (km < 1) {
      return `${Math.round(km * 1000)} 公尺`;
    }
    return `${km.toFixed(1)} 公里`;
  };

  const getRarityColor = (rarity?: string): string => {
    switch (rarity) {
      case 'legendary':
        return 'text-yellow-500';
      case 'epic':
        return 'text-purple-500';
      case 'rare':
        return 'text-blue-500';
      case 'common':
      default:
        return 'text-gray-500';
    }
  };

  const getRarityBadge = (rarity?: string): string => {
    switch (rarity) {
      case 'legendary':
        return '傳說';
      case 'epic':
        return '史詩';
      case 'rare':
        return '稀有';
      case 'common':
      default:
        return '普通';
    }
  };

  return (
    <Pressable onPress={handlePress}>
      <Box className="flex-row bg-white border border-gray-200 rounded-lg p-3 mb-3 shadow-sm">
        {/* Card Image */}
        {card.image_url ? (
          <Image
            source={{ uri: card.image_url }}
            className="w-20 h-28 rounded-md mr-3"
            resizeMode="cover"
          />
        ) : (
          <Box className="w-20 h-28 bg-gray-200 rounded-md mr-3 items-center justify-center">
            <Text className="text-gray-400 text-xs">無圖片</Text>
          </Box>
        )}

        {/* Card Info */}
        <Box className="flex-1">
          {/* Idol Name */}
          <Text className="text-base font-bold text-gray-900 mb-1" numberOfLines={1}>
            {card.idol || '未知偶像'}
          </Text>

          {/* Group */}
          {card.idol_group && (
            <Text className="text-sm text-gray-600 mb-1" numberOfLines={1}>
              {card.idol_group}
            </Text>
          )}

          {/* Album */}
          {card.album && (
            <Text className="text-xs text-gray-500 mb-1" numberOfLines={1}>
              專輯：{card.album}
            </Text>
          )}

          {/* Rarity Badge */}
          {card.rarity && (
            <Box className="flex-row items-center mb-2">
              <Text className={`text-xs font-semibold ${getRarityColor(card.rarity)}`}>
                {getRarityBadge(card.rarity)}
              </Text>
            </Box>
          )}

          {/* Owner and Distance */}
          <Box className="flex-row items-center justify-between mt-auto">
            <Text className="text-xs text-gray-500" numberOfLines={1}>
              擁有者：{card.owner_nickname || '匿名'}
            </Text>
            <Text className="text-xs font-semibold text-blue-500">
              {formatDistance(card.distance_km)}
            </Text>
          </Box>
        </Box>
      </Box>
    </Pressable>
  );
}
