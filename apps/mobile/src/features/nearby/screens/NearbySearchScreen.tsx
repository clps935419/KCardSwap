/**
 * Nearby Search Screen
 * M302: 附近搜尋頁 & M303: 限次錯誤處理
 * 
 * 功能：
 * - 取得使用者當前位置
 * - 搜尋附近的小卡
 * - 顯示搜尋結果（按距離排序）
 * - 處理 429 限制錯誤並提示升級
 * - 處理定位權限拒絕
 * 
 * 使用 Gluestack UI 元件
 */

import React, { useState, useEffect } from 'react';
import { FlatList, RefreshControl, Alert, Linking } from 'react-native';
import { Box, Text, Button, ButtonText, Spinner } from '@/src/shared/ui/components';
import { useLocation, useNearbySearch, useUpdateLocation, isRateLimitError } from '@/src/features/nearby/hooks';
import { NearbyCardItem } from '@/src/features/nearby/components';
import type { NearbyCard } from '@/src/features/nearby/hooks';

export function NearbySearchScreen() {
  const [searchEnabled, setSearchEnabled] = useState(false);
  const [searchParams, setSearchParams] = useState<{ lat: number; lng: number } | null>(null);

  const {
    location,
    error: locationError,
    isLoading: isLoadingLocation,
    requestLocation,
    hasPermission,
  } = useLocation();

  const updateLocation = useUpdateLocation();

  const {
    data: searchResults,
    isLoading: isSearching,
    error: searchError,
    refetch: refetchSearch,
    isRefetching,
  } = useNearbySearch(searchParams, searchEnabled);

  // Auto-request location on mount if permission already granted
  useEffect(() => {
    if (hasPermission === true && !location) {
      requestLocation();
    }
  }, [hasPermission]);

  // When location is obtained, update backend and prepare search
  useEffect(() => {
    if (location && !updateLocation.isPending) {
      updateLocation.mutate(location);
      setSearchParams({
        lat: location.latitude,
        lng: location.longitude,
      });
    }
  }, [location]);

  const handleSearchNearby = async () => {
    if (!location) {
      await requestLocation();
      return;
    }

    setSearchEnabled(true);
    setSearchParams({
      lat: location.latitude,
      lng: location.longitude,
    });

    // Manually trigger search
    setTimeout(() => {
      refetchSearch();
    }, 100);
  };

  const handleCardPress = (card: NearbyCard) => {
    // TODO: Navigate to card detail or chat with owner
    Alert.alert('卡片詳情', `${card.idol} - ${card.idol_group}\n擁有者：${card.owner_nickname}`);
  };

  const handleOpenSettings = () => {
    Linking.openSettings();
  };

  const handleUpgrade = () => {
    // TODO: Navigate to subscription/upgrade screen
    Alert.alert('升級方案', '升級至付費會員可享有無限次搜尋！');
  };

  // Permission denied view
  if (hasPermission === false && locationError?.code === 'PERMISSION_DENIED') {
    return (
      <Box className="flex-1 items-center justify-center p-6 bg-white">
        <Text className="text-6xl mb-4">📍</Text>
        <Text className="text-lg font-bold text-gray-900 mb-2 text-center">
          需要定位權限
        </Text>
        <Text className="text-sm text-gray-600 mb-6 text-center">
          請允許應用程式存取您的位置，才能搜尋附近的小卡
        </Text>
        <Button onPress={requestLocation} className="mb-3">
          <ButtonText>授予定位權限</ButtonText>
        </Button>
        <Button onPress={handleOpenSettings} variant="outline">
          <ButtonText>開啟設定</ButtonText>
        </Button>
      </Box>
    );
  }

  // Rate limit error view (M303)
  if (searchError && isRateLimitError(searchError)) {
    return (
      <Box className="flex-1 items-center justify-center p-6 bg-white">
        <Text className="text-6xl mb-4">⏰</Text>
        <Text className="text-lg font-bold text-gray-900 mb-2 text-center">
          今日搜尋次數已達上限
        </Text>
        <Text className="text-sm text-gray-600 mb-2 text-center">
          {searchError.message}
        </Text>
        <Text className="text-xs text-gray-500 mb-6 text-center">
          已使用 {searchError.current_count} / {searchError.limit} 次
        </Text>
        <Button onPress={handleUpgrade} className="mb-3">
          <ButtonText>升級至付費會員（無限次搜尋）</ButtonText>
        </Button>
        <Button
          onPress={() => {
            setSearchEnabled(false);
            setSearchParams(null);
          }}
          variant="outline"
        >
          <ButtonText>返回</ButtonText>
        </Button>
      </Box>
    );
  }

  // General error view
  if (locationError && locationError.code !== 'PERMISSION_DENIED') {
    return (
      <Box className="flex-1 items-center justify-center p-6 bg-white">
        <Text className="text-6xl mb-4">❌</Text>
        <Text className="text-lg font-bold text-gray-900 mb-2 text-center">
          無法取得位置
        </Text>
        <Text className="text-sm text-gray-600 mb-6 text-center">
          {locationError.message}
        </Text>
        <Button onPress={requestLocation}>
          <ButtonText>重試</ButtonText>
        </Button>
      </Box>
    );
  }

  // Loading location view
  if (isLoadingLocation || (hasPermission === null && !locationError)) {
    return (
      <Box className="flex-1 items-center justify-center bg-white">
        <Spinner size="large" />
        <Text className="text-sm text-gray-600 mt-4">正在取得位置...</Text>
      </Box>
    );
  }

  // Main search view
  return (
    <Box className="flex-1 bg-white">
      {/* Header */}
      <Box className="p-4 border-b border-gray-200">
        <Text className="text-xl font-bold text-gray-900 mb-2">附近的小卡</Text>
        <Text className="text-sm text-gray-600 mb-4">
          搜尋您附近的小卡收藏
        </Text>

        {/* Search Button */}
        <Button
          onPress={handleSearchNearby}
          isDisabled={!location || isSearching}
          className="w-full"
        >
          {isSearching ? (
            <>
              <Spinner size="small" color="white" />
              <ButtonText className="ml-2">搜尋中...</ButtonText>
            </>
          ) : (
            <ButtonText>🔍 搜尋附近小卡</ButtonText>
          )}
        </Button>

        {location && (
          <Text className="text-xs text-gray-500 mt-2 text-center">
            目前位置：{location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
          </Text>
        )}
      </Box>

      {/* Results */}
      {searchResults && (
        <Box className="flex-1">
          {searchResults.count === 0 ? (
            <Box className="flex-1 items-center justify-center p-6">
              <Text className="text-6xl mb-4">🔍</Text>
              <Text className="text-lg font-bold text-gray-900 mb-2 text-center">
                附近沒有小卡
              </Text>
              <Text className="text-sm text-gray-600 text-center">
                嘗試擴大搜尋範圍或稍後再試
              </Text>
            </Box>
          ) : (
            <FlatList
              data={searchResults.results}
              keyExtractor={(item) => item.card_id}
              renderItem={({ item }) => (
                <NearbyCardItem card={item} onPress={handleCardPress} />
              )}
              contentContainerStyle={{ padding: 16 }}
              ListHeaderComponent={
                <Box className="mb-3">
                  <Text className="text-sm font-semibold text-gray-900">
                    找到 {searchResults.count} 張小卡
                  </Text>
                  <Text className="text-xs text-gray-500">
                    按距離由近到遠排序
                  </Text>
                </Box>
              }
              refreshControl={
                <RefreshControl
                  refreshing={isRefetching}
                  onRefresh={refetchSearch}
                />
              }
            />
          )}
        </Box>
      )}

      {/* Empty state before search */}
      {!searchResults && !isSearching && (
        <Box className="flex-1 items-center justify-center p-6">
          <Text className="text-6xl mb-4">📍</Text>
          <Text className="text-lg font-bold text-gray-900 mb-2 text-center">
            開始搜尋
          </Text>
          <Text className="text-sm text-gray-600 text-center">
            點擊上方按鈕搜尋附近的小卡
          </Text>
        </Box>
      )}
    </Box>
  );
}
