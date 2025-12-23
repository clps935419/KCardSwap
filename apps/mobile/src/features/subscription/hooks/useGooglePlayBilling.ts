/**
 * Google Play Billing Hook
 * 
 * Hook for managing Google Play Billing operations
 * Uses react-native-iap for in-app purchases
 * 
 * IMPORTANT: Requires Expo Development Build (not supported in Expo Go)
 * 
 * Setup:
 * 1. npm install react-native-iap
 * 2. Configure Google Play Console with products
 * 3. Build with EAS: eas build --profile development --platform android
 */
import { useEffect, useState, useCallback } from 'react';
import { Platform, Alert } from 'react-native';
import type { Purchase, PurchaseProduct } from '../types';

// Note: This is a placeholder. Actual implementation requires:
// 1. npm install react-native-iap
// 2. Expo Development Build
// 3. Google Play Console configuration
const iapPlaceholder = {
  initConnection: async () => {
    console.log('[IAP] initConnection called (placeholder)');
    return Promise.resolve();
  },
  endConnection: async () => {
    console.log('[IAP] endConnection called (placeholder)');
    return Promise.resolve();
  },
  getSubscriptions: async (skus: string[]) => {
    console.log('[IAP] getSubscriptions called (placeholder)', skus);
    return Promise.resolve([]);
  },
  requestSubscription: async (sku: string) => {
    console.log('[IAP] requestSubscription called (placeholder)', sku);
    throw new Error('Google Play Billing not available. Requires Expo Development Build.');
  },
  getAvailablePurchases: async () => {
    console.log('[IAP] getAvailablePurchases called (placeholder)');
    return Promise.resolve([]);
  },
};

// Product IDs (configure these in Google Play Console)
export const SUBSCRIPTION_SKUS = {
  PREMIUM_MONTHLY: 'premium_monthly',
  PREMIUM_YEARLY: 'premium_yearly',
} as const;

interface UseGooglePlayBillingReturn {
  products: PurchaseProduct[];
  isLoading: boolean;
  error: string | null;
  purchaseSubscription: (productId: string) => Promise<Purchase | null>;
  restorePurchases: () => Promise<Purchase[]>;
  isInitialized: boolean;
}

/**
 * Hook for Google Play Billing
 * 
 * Usage:
 * ```tsx
 * const { products, purchaseSubscription, restorePurchases } = useGooglePlayBilling();
 * 
 * // Purchase
 * const handlePurchase = async () => {
 *   const purchase = await purchaseSubscription(SUBSCRIPTION_SKUS.PREMIUM_MONTHLY);
 *   if (purchase) {
 *     // Verify with backend
 *   }
 * };
 * ```
 */
export function useGooglePlayBilling(): UseGooglePlayBillingReturn {
  const [products, setProducts] = useState<PurchaseProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize connection
  useEffect(() => {
    if (Platform.OS !== 'android') {
      setError('Google Play Billing is only available on Android');
      setIsLoading(false);
      return;
    }

    const initialize = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Initialize IAP connection
        await iapPlaceholder.initConnection();
        setIsInitialized(true);

        // Get available subscriptions
        const productIds = Object.values(SUBSCRIPTION_SKUS);
        const availableProducts = await iapPlaceholder.getSubscriptions(productIds);
        
        setProducts(availableProducts as PurchaseProduct[]);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to initialize billing';
        setError(errorMessage);
        console.error('[GooglePlayBilling] Initialization failed:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initialize();

    // Cleanup
    return () => {
      iapPlaceholder.endConnection().catch(console.error);
    };
  }, []);

  /**
   * Purchase a subscription
   */
  const purchaseSubscription = useCallback(async (productId: string): Promise<Purchase | null> => {
    if (!isInitialized) {
      Alert.alert('錯誤', 'Google Play Billing 尚未初始化');
      return null;
    }

    try {
      setError(null);
      
      // Request subscription purchase
      const purchase = await iapPlaceholder.requestSubscription(productId);
      
      if (purchase) {
        return purchase as Purchase;
      }
      
      return null;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '購買失敗';
      setError(errorMessage);
      
      // User cancelled or error
      if (errorMessage.includes('cancelled') || errorMessage.includes('canceled')) {
        // User cancelled - don't show error
        return null;
      }
      
      Alert.alert('購買失敗', errorMessage);
      return null;
    }
  }, [isInitialized]);

  /**
   * Restore previous purchases
   * Used when user reinstalls app or switches devices
   */
  const restorePurchases = useCallback(async (): Promise<Purchase[]> => {
    if (!isInitialized) {
      throw new Error('Google Play Billing not initialized');
    }

    try {
      setError(null);
      const purchases = await iapPlaceholder.getAvailablePurchases();
      return purchases as Purchase[];
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to restore purchases';
      setError(errorMessage);
      throw err;
    }
  }, [isInitialized]);

  return {
    products,
    isLoading,
    error,
    purchaseSubscription,
    restorePurchases,
    isInitialized,
  };
}

/**
 * Check if Google Play Billing is available
 * (requires Expo Development Build)
 */
export function isGooglePlayBillingAvailable(): boolean {
  if (Platform.OS !== 'android') {
    return false;
  }
  
  // Check if running in Expo Go (which doesn't support IAP)
  // In Expo Go, native modules are not available
  // @ts-ignore
  if (global.__DEV__ && !global.__fbBatchedBridge) {
    return false;
  }
  
  return true;
}
