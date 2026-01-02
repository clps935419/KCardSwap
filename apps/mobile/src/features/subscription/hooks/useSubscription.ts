/**
 * Subscription Hook
 * 
 * Hook for managing subscription state and operations
 * Integrates with backend API and Google Play Billing
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { AppState, AppStateStatus } from 'react-native';

import {
  getSubscriptionStatusApiV1SubscriptionsStatusGet,
  verifyReceiptApiV1SubscriptionsVerifyReceiptPostMutation,
  type VerifyReceiptApiV1SubscriptionsVerifyReceiptPostData,
  type GetSubscriptionStatusApiV1SubscriptionsStatusGetResponse,
} from '@/src/shared/api/generated';

import type { SubscriptionInfo } from '../types';

/**
 * Hook for subscription status
 * Auto-refreshes when app returns to foreground
 */
export function useSubscriptionStatus() {
  const queryClient = useQueryClient();
  
  const query = useQuery({
    queryKey: ['subscription', 'status'],
    queryFn: async () => {
      const response = await getSubscriptionStatusApiV1SubscriptionsStatusGet();
      // Extract data from envelope format
      return response.data?.data as SubscriptionInfo;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  // Refresh subscription status when app comes to foreground
  useEffect(() => {
    const subscription = AppState.addEventListener('change', (nextAppState: AppStateStatus) => {
      if (nextAppState === 'active') {
        queryClient.invalidateQueries({ queryKey: ['subscription', 'status'] });
      }
    });

    return () => {
      subscription.remove();
    };
  }, [queryClient]);

  return {
    subscription: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    isPremium: query.data?.entitlement_active ?? false,
    plan: query.data?.plan ?? 'free',
  };
}

/**
 * Hook for verifying purchase receipt
 */
export function useVerifyReceipt() {
  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    ...verifyReceiptApiV1SubscriptionsVerifyReceiptPostMutation(),
    onSuccess: (response) => {
      // Extract data from envelope and update subscription status cache
      const data = response?.data;
      queryClient.setQueryData(['subscription', 'status'], data);
    },
  });

  return {
    verifyReceipt: mutation.mutate,
    verifyReceiptAsync: mutation.mutateAsync,
    isVerifying: mutation.isPending,
    isSuccess: mutation.isSuccess,
    isError: mutation.isError,
    error: mutation.error,
    data: mutation.data?.data as SubscriptionInfo | undefined,
  };
}

/**
 * Helper hook to check if user has premium access
 */
export function useIsPremium(): boolean {
  const { isPremium } = useSubscriptionStatus();
  return isPremium;
}

/**
 * Helper hook to get subscription plan
 */
export function useSubscriptionPlan(): 'free' | 'premium' {
  const { plan } = useSubscriptionStatus();
  return plan;
}
