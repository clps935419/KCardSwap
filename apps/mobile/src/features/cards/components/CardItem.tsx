/**
 * Card Item Component
 * 卡片列表項目元件
 * M204: 列表顯示，優先使用本機縮圖
 * 
 * 使用 Gluestack UI 元件
 */

import React, { useState, useEffect } from 'react';
import { Image } from 'react-native';
import { Box, Text, Pressable, Spinner, Card } from '@/src/shared/ui/components';
import { getThumbnailFromCache } from '@/src/features/cards/services/thumbnailService';
import type { Card as CardType } from '@/src/features/cards/types';

interface CardItemProps {
  card: CardType;
  onPress?: (card: CardType) => void;
  onDelete?: (card: CardType) => void;
}

export function CardItem({ card, onPress, onDelete }: CardItemProps) {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // 載入圖片：優先使用縮圖，fallback 到原圖
  useEffect(() => {
    let isMounted = true;

    const loadImage = async () => {
      try {
        setLoading(true);
        setError(false);

        // 嘗試從快取載入縮圖
        const thumbnailUri = await getThumbnailFromCache(card.id, card.image_url);

        if (isMounted) {
          if (thumbnailUri) {
            setImageUri(thumbnailUri);
          } else {
            // 縮圖不存在，使用原圖
            setImageUri(card.image_url);
          }
          setLoading(false);
        }
      } catch (err) {
        console.error('載入圖片失敗', err);
        if (isMounted) {
          setError(true);
          setLoading(false);
        }
      }
    };

    loadImage();

    return () => {
      isMounted = false;
    };
  }, [card.id, card.image_url]);

  const handleRetry = () => {
    setImageUri(card.image_url);
    setError(false);
  };

  const getRarityColor = (rarity: string) => {
    const colors: Record<string, string> = {
      common: '$gray200',
      rare: '$blue400',
      epic: '$purple500',
      legendary: '$amber500',
    };
    return colors[rarity] || '$gray200';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: '$green500',
      trading: '$orange500',
      traded: '$gray500',
    };
    return colors[status] || '$gray500';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      available: '可交換',
      trading: '交易中',
      traded: '已交換',
    };
    return labels[status] || status;
  };

  return (
    <Pressable onPress={() => onPress?.(card)}>
      <Card
        variant="elevated"
        className="flex-row p-3 mx-4 my-2"
      >
        {/* 圖片容器 */}
        <Box className="w-20 h-24 rounded-lg overflow-hidden bg-gray-100">
          {loading ? (
            <Box className="w-full h-full justify-center items-center">
              <Spinner size="small" />
            </Box>
          ) : error ? (
            <Pressable
              className="w-full h-full justify-center items-center"
              onPress={handleRetry}
            >
              <Text className="text-xs text-gray-600 text-center">載入失敗</Text>
              <Text className="text-xs text-blue-500 mt-1">點擊重試</Text>
            </Pressable>
          ) : (
            <Image
              source={{ uri: imageUri || undefined }}
              style={{ width: '100%', height: '100%' }}
              resizeMode="cover"
              onError={() => setError(true)}
            />
          )}
        </Box>

        {/* 資訊容器 */}
        <Box className="flex-1 ml-3 justify-between">
          <Box>
            <Text className="text-base font-bold text-gray-900" numberOfLines={1}>
              {card.idol}
            </Text>
            {card.idol_group && (
              <Text className="text-sm text-gray-600 mt-0.5" numberOfLines={1}>
                {card.idol_group}
              </Text>
            )}
            {card.album && (
              <Text className="text-xs text-gray-400 mt-0.5" numberOfLines={1}>
                {card.album}
              </Text>
            )}
          </Box>

          {/* 標籤 */}
          <Box className="flex-row gap-2 mt-2">
            <Box
              className="px-2 py-1 rounded"
              style={{ backgroundColor: getRarityColor(card.rarity) }}
            >
              <Text className="text-xs font-bold text-white uppercase">
                {card.rarity}
              </Text>
            </Box>
            <Box
              className="px-2 py-1 rounded"
              style={{ backgroundColor: getStatusColor(card.status) }}
            >
              <Text className="text-xs font-semibold text-white">
                {getStatusLabel(card.status)}
              </Text>
            </Box>
          </Box>
        </Box>

        {/* 刪除按鈕 */}
        {onDelete && card.status === 'available' && (
          <Pressable
            className="w-8 h-8 rounded-full bg-red-500 justify-center items-center self-start"
            onPress={(e) => {
              e.stopPropagation();
              onDelete(card);
            }}
          >
            <Text className="text-lg text-white font-bold">✕</Text>
          </Pressable>
        )}
      </Card>
    </Pressable>
  );
}
