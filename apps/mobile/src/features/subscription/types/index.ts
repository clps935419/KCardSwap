/**
 * Subscription Types
 * 
 * Type definitions for subscription management
 */

export type SubscriptionPlan = 'free' | 'premium';

export type SubscriptionStatus = 'active' | 'inactive' | 'expired' | 'pending';

export interface SubscriptionInfo {
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  expires_at: string | null;
  entitlement_active: boolean;
  source: 'google_play';
}

export interface VerifyReceiptRequest {
  platform: 'android' | 'ios';
  purchase_token: string;
  product_id: string;
}

export interface PurchaseProduct {
  productId: string;
  title: string;
  description: string;
  price: string;
  currency: string;
  type: 'subs'; // Subscription type
}

export interface Purchase {
  transactionId: string;
  productId: string;
  transactionDate: number;
  transactionReceipt: string;
  purchaseToken: string;
  dataAndroid?: string;
  signatureAndroid?: string;
  autoRenewingAndroid?: boolean;
  isAcknowledgedAndroid?: boolean;
  purchaseStateAndroid?: number;
  originalTransactionDateIOS?: string;
  originalTransactionIdentifierIOS?: string;
}

export interface PlanFeature {
  name: string;
  included: boolean;
  description?: string;
}

export interface PlanDetails {
  id: SubscriptionPlan;
  name: string;
  price: string;
  pricePerMonth?: string;
  features: PlanFeature[];
  productId?: string; // Google Play product ID
  highlighted?: boolean;
}
