/**
 * Subscription Plans Screen (Paywall)
 * 
 * Shows available subscription plans and allows users to upgrade
 */
import React, { useState } from 'react';
import { ScrollView, Alert } from 'react-native';
import { Box, Text, Button, ButtonText, Heading, Spinner } from '@/src/shared/ui/components';

import { useSubscriptionStatus, useVerifyReceipt } from '../hooks/useSubscription';
import { useGooglePlayBilling, SUBSCRIPTION_SKUS } from '../hooks/useGooglePlayBilling';
import type { PlanDetails } from '../types';

// Plan configurations
const PLANS: PlanDetails[] = [
  {
    id: 'free',
    name: '免費方案',
    price: '免費',
    features: [
      { name: '每日上傳 2 張卡片', included: true },
      { name: '總容量 100MB', included: true },
      { name: '每張卡片最大 2MB', included: true },
      { name: '每日搜尋 5 次', included: true },
      { name: '每日發文 2 則', included: true },
    ],
  },
  {
    id: 'premium',
    name: '付費方案',
    price: 'NT$ 120',
    pricePerMonth: '每月',
    productId: SUBSCRIPTION_SKUS.PREMIUM_MONTHLY,
    highlighted: true,
    features: [
      { name: '無限上傳卡片', included: true },
      { name: '總容量 1GB', included: true },
      { name: '每張卡片最大 5MB', included: true },
      { name: '無限搜尋', included: true },
      { name: '無限發文', included: true },
      { name: '優先客服支援', included: true },
    ],
  },
];

export default function SubscriptionPlansScreen() {
  const { subscription, isLoading: statusLoading } = useSubscriptionStatus();
  const { verifyReceiptAsync, isVerifying } = useVerifyReceipt();
  const { 
    products, 
    isLoading: billingLoading, 
    purchaseSubscription,
    isInitialized 
  } = useGooglePlayBilling();
  
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const currentPlan = subscription?.plan ?? 'free';
  const isPremium = subscription?.entitlement_active ?? false;

  const handlePurchase = async (productId: string) => {
    if (!productId) {
      Alert.alert('錯誤', '無效的產品 ID');
      return;
    }

    setSelectedPlan(productId);

    try {
      // Step 1: Purchase via Google Play
      const purchase = await purchaseSubscription(productId);
      
      if (!purchase) {
        // User cancelled or error
        setSelectedPlan(null);
        return;
      }

      // Step 2: Verify with backend
      const result = await verifyReceiptAsync({
        platform: 'android',
        purchase_token: purchase.purchaseToken,
        product_id: productId,
      });

      // Step 3: Check if entitlement is active
      if (result.entitlement_active) {
        Alert.alert(
          '訂閱成功',
          '您已成功訂閱付費方案！',
          [{ text: '確定', onPress: () => setSelectedPlan(null) }]
        );
      } else if (result.status === 'pending') {
        Alert.alert(
          '處理中',
          '您的訂閱正在處理中，請稍後再試。',
          [{ text: '確定', onPress: () => setSelectedPlan(null) }]
        );
      } else {
        throw new Error('驗證失敗');
      }
    } catch (error) {
      console.error('[SubscriptionPlans] Purchase failed:', error);
      
      const errorMessage = error instanceof Error ? error.message : '購買失敗';
      
      // Handle specific errors
      if (errorMessage.includes('PURCHASE_TOKEN_ALREADY_USED')) {
        Alert.alert('錯誤', '此購買已被其他帳號使用');
      } else if (errorMessage.includes('GOOGLE_PLAY_UNAVAILABLE')) {
        Alert.alert('錯誤', '驗證暫時失敗，請稍後再試');
      } else {
        Alert.alert('購買失敗', errorMessage);
      }
      
      setSelectedPlan(null);
    }
  };

  if (statusLoading || billingLoading) {
    return (
      <Box className="flex-1 items-center justify-center">
        <Spinner size="large" />
        <Text className="mt-4">載入中...</Text>
      </Box>
    );
  }

  return (
    <ScrollView className="flex-1 bg-white">
      <Box className="p-4">
        <Heading className="text-2xl font-bold mb-2">選擇方案</Heading>
        <Text className="text-gray-600 mb-6">
          升級到付費方案，解鎖更多功能
        </Text>

        {/* Current Plan Status */}
        {isPremium && (
          <Box className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <Text className="text-blue-800 font-semibold">
              ✓ 您目前使用付費方案
            </Text>
            {subscription?.expires_at && (
              <Text className="text-blue-600 text-sm mt-1">
                到期日：{new Date(subscription.expires_at).toLocaleDateString('zh-TW')}
              </Text>
            )}
          </Box>
        )}

        {/* Plans */}
        {PLANS.map((plan) => (
          <Box
            key={plan.id}
            className={`mb-4 p-4 border-2 rounded-lg ${
              plan.highlighted
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-white'
            }`}
          >
            <Box className="flex-row justify-between items-center mb-3">
              <Box>
                <Text className="text-xl font-bold">{plan.name}</Text>
                <Box className="flex-row items-baseline mt-1">
                  <Text className="text-2xl font-bold text-blue-600">
                    {plan.price}
                  </Text>
                  {plan.pricePerMonth && (
                    <Text className="text-gray-600 ml-2">
                      {plan.pricePerMonth}
                    </Text>
                  )}
                </Box>
              </Box>
              {plan.id === currentPlan && (
                <Box className="bg-green-500 rounded-full px-3 py-1">
                  <Text className="text-white font-semibold text-sm">
                    目前方案
                  </Text>
                </Box>
              )}
            </Box>

            {/* Features */}
            <Box className="mb-4">
              {plan.features.map((feature, index) => (
                <Box key={index} className="flex-row items-start mb-2">
                  <Text className="text-green-600 mr-2">✓</Text>
                  <Text className="flex-1 text-gray-700">{feature.name}</Text>
                </Box>
              ))}
            </Box>

            {/* Action Button */}
            {plan.id === 'premium' && !isPremium && (
              <Button
                onPress={() => plan.productId && handlePurchase(plan.productId)}
                disabled={!isInitialized || isVerifying || selectedPlan === plan.productId}
                className={`${
                  isVerifying && selectedPlan === plan.productId
                    ? 'bg-gray-400'
                    : 'bg-blue-600'
                }`}
              >
                {isVerifying && selectedPlan === plan.productId ? (
                  <Box className="flex-row items-center">
                    <Spinner size="small" />
                    <ButtonText className="ml-2">處理中...</ButtonText>
                  </Box>
                ) : (
                  <ButtonText>立即訂閱</ButtonText>
                )}
              </Button>
            )}
          </Box>
        ))}

        {/* Note about Expo Development Build */}
        {!isInitialized && (
          <Box className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 mt-4">
            <Text className="text-yellow-800 font-semibold mb-2">
              ⚠️ 注意
            </Text>
            <Text className="text-yellow-700 text-sm">
              Google Play 內購功能需要 Expo Development Build。
              在 Expo Go 中無法使用。
            </Text>
          </Box>
        )}
      </Box>
    </ScrollView>
  );
}
