/**
 * CardGrid Component
 * Instagram-style photo grid for displaying gallery cards
 */

import React from 'react';
import { FlatList, Image, Pressable, Dimensions } from 'react-native';
import { Box, Text, Spinner } from '@/src/shared/ui/components';
import type { GalleryCardResponse } from '@/src/shared/api/sdk';

interface CardGridProps {
  cards: GalleryCardResponse[];
  onCardPress?: (card: GalleryCardResponse) => void;
  isLoading?: boolean;
}

export function CardGrid({ cards, onCardPress, isLoading }: CardGridProps) {
  const screenWidth = Dimensions.get('window').width;
  const numColumns = 3;
  const spacing = 2;
  const cardSize = (screenWidth - spacing * (numColumns + 1)) / numColumns;

  if (isLoading) {
    return (
      <Box className="flex-1 items-center justify-center py-12">
        <Spinner size="large" />
        <Text className="mt-4 text-gray-600">載入小卡中...</Text>
      </Box>
    );
  }

  if (cards.length === 0) {
    return (
      <Box className="flex-1 items-center justify-center py-12">
        <Text className="text-6xl mb-4">📦</Text>
        <Text className="text-gray-600 text-center px-4">
          尚無小卡
        </Text>
      </Box>
    );
  }

  return (
    <FlatList
      data={cards}
      numColumns={numColumns}
      keyExtractor={(item) => item.id}
      contentContainerStyle={{ padding: spacing }}
      columnWrapperStyle={{ gap: spacing }}
      renderItem={({ item }) => (
        <Pressable
          onPress={() => onCardPress?.(item)}
          style={{
            width: cardSize,
            height: cardSize,
            marginBottom: spacing,
          }}
        >
          <Box
            className="w-full h-full bg-gray-200 rounded-sm overflow-hidden"
            style={{ borderRadius: 2 }}
          >
            {/* 
              TODO: Replace placeholder with actual media asset image
              Currently using solid background color as gradient is not supported in React Native
              Future: Integrate with media asset service to display card images
            */}
            <Box className="w-full h-full items-center justify-center bg-purple-400">
              <Text className="text-white text-xs font-bold text-center px-1">
                {item.idol_name}
              </Text>
              {item.era && (
                <Text className="text-white text-xs mt-1">
                  {item.era}
                </Text>
              )}
            </Box>
          </Box>
        </Pressable>
      )}
      ListFooterComponent={
        <Box className="py-4 items-center">
          <Text className="text-gray-500 text-sm">
            共 {cards.length} 張小卡
          </Text>
        </Box>
      }
    />
  );
}
