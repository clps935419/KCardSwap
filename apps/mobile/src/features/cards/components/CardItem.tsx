/**
 * Card Item Component
 * 卡片列表項目元件
 * M204: 列表顯示，優先使用本機縮圖
 */

import React, { useState, useEffect } from 'react';
import { View, Text, Image, TouchableOpacity, ActivityIndicator, StyleSheet } from 'react-native';
import { getThumbnailFromCache } from '../services/thumbnailService';
import type { Card } from '../types';

interface CardItemProps {
  card: Card;
  onPress?: (card: Card) => void;
  onDelete?: (card: Card) => void;
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

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={() => onPress?.(card)}
      activeOpacity={0.7}
    >
      <View style={styles.imageContainer}>
        {loading ? (
          <View style={styles.placeholder}>
            <ActivityIndicator size="small" color="#666" />
          </View>
        ) : error ? (
          <TouchableOpacity style={styles.placeholder} onPress={handleRetry}>
            <Text style={styles.errorText}>載入失敗</Text>
            <Text style={styles.retryText}>點擊重試</Text>
          </TouchableOpacity>
        ) : (
          <Image
            source={{ uri: imageUri || undefined }}
            style={styles.image}
            resizeMode="cover"
            onError={() => setError(true)}
          />
        )}
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.idol} numberOfLines={1}>
          {card.idol}
        </Text>
        {card.idol_group && (
          <Text style={styles.group} numberOfLines={1}>
            {card.idol_group}
          </Text>
        )}
        {card.album && (
          <Text style={styles.album} numberOfLines={1}>
            {card.album}
          </Text>
        )}
        <View style={styles.footer}>
          <View style={[styles.rarityBadge, styles[`rarity_${card.rarity}`]]}>
            <Text style={styles.rarityText}>{card.rarity}</Text>
          </View>
          <View style={[styles.statusBadge, styles[`status_${card.status}`]]}>
            <Text style={styles.statusText}>{getStatusLabel(card.status)}</Text>
          </View>
        </View>
      </View>

      {onDelete && card.status === 'available' && (
        <TouchableOpacity
          style={styles.deleteButton}
          onPress={(e) => {
            e.stopPropagation();
            onDelete(card);
          }}
        >
          <Text style={styles.deleteText}>✕</Text>
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    available: '可交換',
    trading: '交易中',
    traded: '已交換',
  };
  return labels[status] || status;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  imageContainer: {
    width: 80,
    height: 100,
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#f0f0f0',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  placeholder: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
  },
  errorText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  retryText: {
    fontSize: 10,
    color: '#007AFF',
  },
  infoContainer: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'space-between',
  },
  idol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  group: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  album: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  footer: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  rarityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  rarity_common: {
    backgroundColor: '#e0e0e0',
  },
  rarity_rare: {
    backgroundColor: '#64B5F6',
  },
  rarity_epic: {
    backgroundColor: '#AB47BC',
  },
  rarity_legendary: {
    backgroundColor: '#FFB74D',
  },
  rarityText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#fff',
    textTransform: 'uppercase',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  status_available: {
    backgroundColor: '#4CAF50',
  },
  status_trading: {
    backgroundColor: '#FF9800',
  },
  status_traded: {
    backgroundColor: '#9E9E9E',
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#fff',
  },
  deleteButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FF5252',
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'flex-start',
  },
  deleteText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: 'bold',
  },
});
