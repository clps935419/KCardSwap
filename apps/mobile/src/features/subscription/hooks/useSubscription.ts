/**
 * Subscription Hook
 * 
 * Hook for managing subscription state and operations
 * Integrates with backend API and Google Play Billing
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { AppState, AppStateStatus } from 'react-native';

import type { SubscriptionInfo, VerifyReceiptRequest } from '../types';

// Note: These will be replaced with generated SDK after OpenAPI generation
// For now, using placeholder API functions
const subscriptionApi = {
  getStatus: async (): Promise<SubscriptionInfo> => {
    // TODO: Replace with generated SDK
    // return await getSubscriptionsStatusOptions()
    throw new Error('SDK not yet generated. Run: npm run sdk:generate');
  },
  
  verifyReceipt: async (data: VerifyReceiptRequest): Promise<SubscriptionInfo> => {
    // TODO: Replace with generated SDK
    // return await verifyReceiptMutation({ body: data })
    throw new Error('SDK not yet generated. Run: npm run sdk:generate');
  },
};

/**
 * Hook for subscription status
 * Auto-refreshes when app returns to foreground
 */
export function useSubscriptionStatus() {
  const queryClient = useQueryClient();
  
  const query = useQuery({
    queryKey: ['subscription', 'status'],
    queryFn: subscriptionApi.getStatus,
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
    mutationFn: subscriptionApi.verifyReceipt,
    onSuccess: (data) => {
      // Update subscription status cache
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
    data: mutation.data,
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
