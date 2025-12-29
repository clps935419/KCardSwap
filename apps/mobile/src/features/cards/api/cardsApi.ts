/**
 * Cards API Client
 * 
 * Uses hey-api generated TanStack Query options/mutations for card operations.
 * 
 * **Standard Usage**:
 * ```typescript
 * import { useQuery, useMutation } from '@tanstack/react-query';
 * import { getMyCardsOptions, uploadToSignedUrl } from './cardsApi';
 * 
 * function MyCardsScreen() {
 *   const { data, isLoading } = useQuery(getMyCardsOptions());
 *   // ... render cards
 * }
 * ```
 */

import type {
  GetMyCardsResponse,
  GetMyCardsData,
  GetUploadUrlApiV1CardsUploadUrlPostResponse,
  ConfirmCardUploadApiV1CardsCardIdConfirmUploadPostResponse,
} from '@/src/shared/api/sdk';

// Re-export SDK TanStack Query options
export {
  getMyCardsOptions,
  getMyCardsQueryKey,
  getUploadUrlApiV1CardsUploadUrlPostMutation,
  confirmCardUploadApiV1CardsCardIdConfirmUploadPostMutation,
} from '@/src/shared/api/sdk';

// Re-export types
export type { GetMyCardsResponse, GetMyCardsData };

// Export SDK response types with simpler names
export type UploadUrlResponse = GetUploadUrlApiV1CardsUploadUrlPostResponse;
export type ConfirmUploadResponse = ConfirmCardUploadApiV1CardsCardIdConfirmUploadPostResponse;

/**
 * Card data structure
 */
export type CardsData = NonNullable<GetMyCardsResponse['data']>;
export type Card = NonNullable<CardsData['items']>[number];

/**
 * Card status enum
 */
export type CardStatus = 'available' | 'in_trade' | 'traded';

/**
 * Card rarity enum (for type safety)
 */
export type CardRarity = 'common' | 'rare' | 'epic' | 'legendary';

/**
 * Upload to Signed URL (M203)
 * 
 * **Important**: This must use independent `fetch()`, NOT the SDK client.
 * - Do not inject Authorization headers
 * - Must follow `required_headers` from backend exactly
 * - Handle errors separately from backend API errors
 * 
 * @param uploadUrl - The signed URL from backend
 * @param file - The file Blob to upload
 * @param method - HTTP method (PUT or POST)
 * @param requiredHeaders - Headers from backend response
 * @returns Promise<void>
 * @throws Error with status code and message
 */
export async function uploadToSignedUrl(
  uploadUrl: string,
  file: Blob,
  method: 'PUT' | 'POST',
  requiredHeaders: Record<string, string>
): Promise<void> {
  try {
    const response = await fetch(uploadUrl, {
      method,
      headers: requiredHeaders,
      body: file,
    });

    if (!response.ok) {
      // Handle Signed URL upload errors (not backend API errors)
      if (response.status === 403) {
        throw new Error('Upload URL expired or invalid. Please get a new upload URL.');
      } else if (response.status >= 400 && response.status < 500) {
        throw new Error(`Upload failed: ${response.status}. Please check the file and try again.`);
      } else if (response.status >= 500) {
        throw new Error('Cloud storage error. Please try again later.');
      }
      
      throw new Error(`Upload failed with status: ${response.status}`);
    }
  } catch (error: any) {
    // Handle network errors
    if (error.message?.includes('network') || error.message?.includes('timeout')) {
      throw new Error('Network error. Please check your connection and try again.');
    }
    
    // Re-throw with context
    throw error;
  }
}

/**
 * Retry configuration for signed URL upload
 */
export const UPLOAD_RETRY_CONFIG = {
  maxRetries: 3,
  retryableStatuses: [408, 429, 500, 502, 503, 504], // Timeout, rate limit, server errors
  nonRetryableStatuses: [400, 403, 404], // Bad request, forbidden, not found
  retryDelay: (attemptNumber: number) => Math.min(1000 * Math.pow(2, attemptNumber), 10000), // Exponential backoff
};

/**
 * Upload to signed URL with retry logic
 * 
 * @param uploadUrl - The signed URL from backend
 * @param file - The file Blob to upload
 * @param method - HTTP method (PUT or POST)
 * @param requiredHeaders - Headers from backend response
 * @param retryConfig - Optional retry configuration
 * @returns Promise<void>
 */
export async function uploadToSignedUrlWithRetry(
  uploadUrl: string,
  file: Blob,
  method: 'PUT' | 'POST',
  requiredHeaders: Record<string, string>,
  retryConfig = UPLOAD_RETRY_CONFIG
): Promise<void> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
    try {
      await uploadToSignedUrl(uploadUrl, file, method, requiredHeaders);
      return; // Success
    } catch (error: any) {
      lastError = error;
      
      // Check if error is retryable
      const isNetworkError = error.message?.includes('network') || error.message?.includes('timeout');
      const isRetryableStatus = error.status && retryConfig.retryableStatuses.includes(error.status);
      
      if (!isNetworkError && !isRetryableStatus) {
        // Non-retryable error, throw immediately
        throw error;
      }
      
      // Last attempt, throw error
      if (attempt === retryConfig.maxRetries) {
        break;
      }
      
      // Wait before retry
      const delay = retryConfig.retryDelay(attempt);
      console.log(`Upload failed (attempt ${attempt + 1}/${retryConfig.maxRetries + 1}), retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError || new Error('Upload failed after retries');
}

/**
 * Example usage with SDK:
 * 
 * ```typescript
 * import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
 * import { 
 *   getMyCardsOptions, 
 *   getMyCardsQueryKey,
 *   getUploadUrlApiV1CardsUploadUrlPostMutation,
 *   confirmCardUploadApiV1CardsCardIdConfirmUploadPostMutation,
 *   uploadToSignedUrlWithRetry 
 * } from './cardsApi';
 * 
 * function UploadCardScreen() {
 *   const queryClient = useQueryClient();
 *   
 *   // 1. Get my cards
 *   const { data: cards } = useQuery(getMyCardsOptions());
 *   
 *   // 2. Get upload URL mutation
 *   const getUploadUrlMutation = useMutation(getUploadUrlApiV1CardsUploadUrlPostMutation());
 *   
 *   // 3. Confirm upload mutation
 *   const confirmUploadMutation = useMutation(
 *     confirmCardUploadApiV1CardsCardIdConfirmUploadPostMutation()
 *   );
 *   
 *   // 4. Upload process
 *   const handleUpload = async (file: Blob, metadata: any) => {
 *     // Step 1: Get signed URL from backend
 *     const uploadUrlResponse = await getUploadUrlMutation.mutateAsync({
 *       body: {
 *         content_type: 'image/jpeg',
 *         file_size_bytes: file.size,
 *         ...metadata,
 *       },
 *     });
 *     
 *     // Step 2: Upload to signed URL (independent fetch)
 *     await uploadToSignedUrlWithRetry(
 *       uploadUrlResponse.upload_url,
 *       file,
 *       uploadUrlResponse.method,
 *       uploadUrlResponse.required_headers
 *     );
 *     
 *     // Step 3: Confirm upload
 *     await confirmUploadMutation.mutateAsync({
 *       path: { card_id: uploadUrlResponse.card_id },
 *     });
 *     
 *     // Step 4: Refresh card list
 *     queryClient.invalidateQueries({ queryKey: getMyCardsQueryKey() });
 *   };
 * }
 * ```
 */
