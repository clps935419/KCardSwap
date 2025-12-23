/**
 * Subscription Status Screen
 * 
 * Shows current subscription status and allows restore purchases
 */
import React, { useState } from 'react';
import { ScrollView, Alert } from 'react-native';
import { Box, Text, Button, ButtonText, Heading, Spinner } from '@/src/shared/ui/components';

import { useSubscriptionStatus, useVerifyReceipt } from '../hooks/useSubscription';
import { useGooglePlayBilling } from '../hooks/useGooglePlayBilling';
import type { Purchase } from '../types';

export default function SubscriptionStatusScreen() {
  const { subscription, isLoading, refetch } = useSubscriptionStatus();
  const { verifyReceiptAsync } = useVerifyReceipt();
  const { restorePurchases, isInitialized } = useGooglePlayBilling();
  
  const [isRestoring, setIsRestoring] = useState(false);

  const isPremium = subscription?.entitlement_active ?? false;
  const status = subscription?.status ?? 'inactive';

  /**
   * Restore purchases from Google Play
   * Query existing purchases and re-verify with backend
   */
  const handleRestorePurchases = async () => {
    setIsRestoring(true);

    try {
      // Step 1: Get available purchases from Google Play
      const purchases = await restorePurchases();

      if (purchases.length === 0) {
        Alert.alert('未找到購買記錄', '沒有找到可恢復的訂閱');
        setIsRestoring(false);
        return;
      }

      // Step 2: Verify each purchase with backend
      let successCount = 0;
      for (const purchase of purchases) {
        try {
          await verifyReceiptAsync({
            platform: 'android',
            purchase_token: purchase.purchaseToken,
            product_id: purchase.productId,
          });
          successCount++;
        } catch (error) {
          console.error('[Restore] Failed to verify purchase:', purchase.productId, error);
        }
      }

      // Step 3: Refresh subscription status
      await refetch();

      Alert.alert(
        '恢復成功',
        `已恢復 ${successCount} 個訂閱`,
        [{ text: '確定' }]
      );
    } catch (error) {
      console.error('[Restore] Failed:', error);
      Alert.alert('恢復失敗', '無法恢復購買記錄，請稍後再試');
    } finally {
      setIsRestoring(false);
    }
  };

  if (isLoading) {
    return (
      <Box className="flex-1 items-center justify-center">
        <Spinner size="large" />
        <Text className="mt-4">載入中...</Text>
      </Box>
    );
  }

  // Get status color and text
  const getStatusInfo = () => {
    switch (status) {
      case 'active':
        return { color: 'bg-green-500', text: '啟用中', textColor: 'text-green-800' };
      case 'expired':
        return { color: 'bg-red-500', text: '已過期', textColor: 'text-red-800' };
      case 'pending':
        return { color: 'bg-yellow-500', text: '待確認', textColor: 'text-yellow-800' };
      case 'inactive':
      default:
        return { color: 'bg-gray-500', text: '未啟用', textColor: 'text-gray-800' };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <ScrollView className="flex-1 bg-white">
      <Box className="p-4">
        <Heading className="text-2xl font-bold mb-6">訂閱狀態</Heading>

        {/* Current Plan */}
        <Box className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
          <Text className="text-gray-600 text-sm mb-1">目前方案</Text>
          <Text className="text-2xl font-bold mb-3">
            {isPremium ? '付費方案' : '免費方案'}
          </Text>

          {/* Status Badge */}
          <Box className="flex-row items-center">
            <Box className={`${statusInfo.color} rounded-full px-3 py-1`}>
              <Text className="text-white font-semibold text-sm">
                {statusInfo.text}
              </Text>
            </Box>
          </Box>
        </Box>

        {/* Subscription Details */}
        {subscription && (
          <Box className="mb-6">
            <Text className="text-lg font-semibold mb-3">詳細資訊</Text>
            
            <Box className="bg-white border border-gray-200 rounded-lg p-4">
              {/* Plan */}
              <Box className="mb-3">
                <Text className="text-gray-600 text-sm">方案類型</Text>
                <Text className="text-base font-medium">
                  {subscription.plan === 'premium' ? '付費方案' : '免費方案'}
                </Text>
              </Box>

              {/* Status */}
              <Box className="mb-3">
                <Text className="text-gray-600 text-sm">狀態</Text>
                <Text className={`text-base font-medium ${statusInfo.textColor}`}>
                  {statusInfo.text}
                </Text>
              </Box>

              {/* Expiry Date */}
              {subscription.expires_at && (
                <Box className="mb-3">
                  <Text className="text-gray-600 text-sm">到期日</Text>
                  <Text className="text-base font-medium">
                    {new Date(subscription.expires_at).toLocaleDateString('zh-TW', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </Text>
                </Box>
              )}

              {/* Entitlement */}
              <Box>
                <Text className="text-gray-600 text-sm">權限狀態</Text>
                <Text className={`text-base font-medium ${
                  subscription.entitlement_active ? 'text-green-600' : 'text-gray-600'
                }`}>
                  {subscription.entitlement_active ? '✓ 已啟用' : '未啟用'}
                </Text>
              </Box>
            </Box>
          </Box>
        )}

        {/* Status Messages */}
        {status === 'pending' && (
          <Box className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 mb-6">
            <Text className="text-yellow-800 font-semibold mb-2">
              ⏳ 訂閱處理中
            </Text>
            <Text className="text-yellow-700 text-sm">
              您的訂閱正在處理中，通常需要幾分鐘時間。請稍後再檢查狀態。
            </Text>
          </Box>
        )}

        {status === 'expired' && (
          <Box className="bg-red-50 border border-red-300 rounded-lg p-4 mb-6">
            <Text className="text-red-800 font-semibold mb-2">
              ⚠️ 訂閱已過期
            </Text>
            <Text className="text-red-700 text-sm">
              您的訂閱已過期，請續訂以繼續使用付費功能。
            </Text>
          </Box>
        )}

        {!isPremium && status === 'inactive' && (
          <Box className="bg-blue-50 border border-blue-300 rounded-lg p-4 mb-6">
            <Text className="text-blue-800 font-semibold mb-2">
              💡 升級到付費方案
            </Text>
            <Text className="text-blue-700 text-sm">
              升級到付費方案，享受無限上傳、無限搜尋等更多功能。
            </Text>
          </Box>
        )}

        {/* Actions */}
        <Box className="space-y-3">
          {/* Restore Purchases */}
          {isInitialized && (
            <Button
              onPress={handleRestorePurchases}
              disabled={isRestoring}
              className="bg-gray-600"
            >
              {isRestoring ? (
                <Box className="flex-row items-center">
                  <Spinner size="small" />
                  <ButtonText className="ml-2">恢復中...</ButtonText>
                </Box>
              ) : (
                <ButtonText>恢復購買</ButtonText>
              )}
            </Button>
          )}

          {/* Refresh */}
          <Button
            onPress={() => refetch()}
            className="bg-blue-600"
          >
            <ButtonText>重新整理狀態</ButtonText>
          </Button>
        </Box>

        {/* Help Text */}
        <Box className="mt-6 p-4 bg-gray-50 rounded-lg">
          <Text className="text-gray-600 text-sm">
            • 如果您在其他裝置購買，請點擊「恢復購買」
            {'\n'}• 訂閱會自動續訂，可隨時在 Google Play 取消
            {'\n'}• 如有問題，請聯繫客服
          </Text>
        </Box>
      </Box>
    </ScrollView>
  );
}
