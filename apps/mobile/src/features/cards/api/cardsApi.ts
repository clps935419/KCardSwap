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
} from '@/src/shared/api/sdk';

// Re-export SDK TanStack Query options
export {
  getMyCardsOptions,
  getMyCardsQueryKey,
} from '@/src/shared/api/sdk';

// Re-export types
export type { GetMyCardsResponse, GetMyCardsData };

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
 * Upload URL request
 * 
 * **Note**: This type will be replaced by SDK-generated type once the endpoint is added to OpenAPI spec.
 * TODO: Use SDK type when available: `GetUploadUrlData`
 */
export interface UploadUrlRequest {
  file_name: string;
  file_size: number;
  content_type: 'image/jpeg' | 'image/png';
}

/**
 * Upload URL response
 * 
 * **Note**: This type will be replaced by SDK-generated type once the endpoint is added to OpenAPI spec.
 * TODO: Use SDK type when available: `GetUploadUrlResponse`
 */
export interface UploadUrlResponse {
  upload_url: string;
  method: 'PUT' | 'POST';
  required_headers: Record<string, string>;
  image_url: string;
  expires_at: string;
  card_id: string;
}

/**
 * Confirm upload response
 * 
 * **Note**: This type will be replaced by SDK-generated type once the endpoint is added to OpenAPI spec.
 * TODO: Use SDK type when available: `ConfirmCardUploadResponse`
 */
export interface ConfirmUploadResponse {
  message: string;
  card_id: string;
}

/**
 * Quota status
 * 
 * **Note**: This type will be replaced by SDK-generated type once the endpoint is added to OpenAPI spec.
 */
export interface QuotaStatus {
  daily_uploads_used: number;
  daily_uploads_limit: number;
  total_storage_used: number;
  total_storage_limit: number;
}

/**
 * TODO M202: Once `/cards/upload-url` is added to OpenAPI spec:
 * 1. Regenerate SDK: `npm run sdk:generate`
 * 2. Replace this comment with:
 *    ```
 *    export { getUploadUrlMutation, getUploadUrlMutationKey } from '@/src/shared/api/sdk';
 *    ```
 * 3. Update UploadUrlRequest and UploadUrlResponse types to use SDK types
 * 4. Remove the temporary implementation below
 */

/**
 * TODO M205: Once `/cards/{id}` DELETE is added to OpenAPI spec:
 * 1. Regenerate SDK: `npm run sdk:generate`
 * 2. Replace this comment with:
 *    ```
 *    export { deleteCardMutation, deleteCardMutationKey } from '@/src/shared/api/sdk';
 *    ```
 */

/**
 * Upload file to Signed URL (M203)
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
 * Example usage:
 * 
 * ```typescript
 * import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
 * import { getMyCardsOptions, getMyCardsQueryKey, uploadToSignedUrlWithRetry, confirmCardUpload } from './cardsApi';
 * 
 * function UploadCardScreen() {
 *   const queryClient = useQueryClient();
 *   
 *   // 1. Get my cards
 *   const { data: cards } = useQuery(getMyCardsOptions());
 *   
 *   // 2. Upload process (TODO: Replace with SDK mutation when available)
 *   const handleUpload = async (file: Blob) => {
 *     // Step 1: Get signed URL from backend (TODO: Use SDK mutation)
 *     const uploadUrlResponse = await getUploadUrl(file);
 *     
 *     // Step 2: Upload to signed URL (independent fetch)
 *     await uploadToSignedUrlWithRetry(
 *       uploadUrlResponse.upload_url,
 *       file,
 *       uploadUrlResponse.method,
 *       uploadUrlResponse.required_headers
 *     );
 *     
 *     // Step 3: Confirm upload (M203B)
 *     await confirmCardUpload(uploadUrlResponse.card_id);
 *     
 *     // Step 4: Refresh card list
 *     queryClient.invalidateQueries({ queryKey: getMyCardsQueryKey() });
 *   };
 * }
 * ```
 */

/**
 * TODO M203B: Once `/cards/{id}/confirm-upload` is added to OpenAPI spec:
 * 1. Regenerate SDK: `npm run sdk:generate`
 * 2. Replace this implementation with SDK mutation:
 *    ```
 *    export { confirmCardUploadMutation, confirmCardUploadMutationKey } from '@/src/shared/api/sdk';
 *    ```
 */

import { client } from '@/src/shared/api/sdk';

/**
 * Temporary implementation: Get upload URL (M202)
 * Will be replaced by SDK-generated mutation once OpenAPI spec is updated
 */
export async function getUploadUrl(request: {
  content_type: string;
  file_size_bytes: number;
  idol?: string;
  idol_group?: string;
  album?: string;
  version?: string;
  rarity?: string;
}): Promise<UploadUrlResponse> {
  const response = await client.POST('/api/v1/cards/upload-url', {
    body: request,
  });

  if (response.error) {
    throw new Error(response.error.message || 'Failed to get upload URL');
  }

  return response.data as unknown as UploadUrlResponse;
}

/**
 * Confirm card upload (M203B)
 * 
 * Call this after successfully uploading the file to the signed URL.
 * This prevents "ghost records" where cards are created but images are never uploaded.
 * 
 * @param cardId - The card ID returned from get upload URL response
 * @returns Promise<ConfirmUploadResponse>
 * @throws Error if confirmation fails
 * 
 * **Error Codes**:
 * - 404: Card not found or image not found in storage
 * - 403: Not authorized to confirm this card
 * - 400: Invalid request (already confirmed, no image, etc.)
 * 
 * **Important**: Always call this after uploadToSignedUrlWithRetry succeeds.
 * If this fails, the card will remain in "pending" status and won't appear in the user's card list.
 */
export async function confirmCardUpload(cardId: string): Promise<ConfirmUploadResponse> {
  try {
    const response = await client.POST('/api/v1/cards/{card_id}/confirm-upload', {
      params: {
        path: {
          card_id: cardId,
        },
      },
    });

    if (response.error) {
      // Handle specific error codes
      if (response.error.code === 'IMAGE_NOT_FOUND') {
        throw new Error('Image not found in storage. Please try uploading again.');
      } else if (response.error.code === 'CARD_NOT_FOUND') {
        throw new Error('Card not found. Please try uploading again.');
      } else if (response.error.code === 'FORBIDDEN') {
        throw new Error('Not authorized to confirm this card upload.');
      } else if (response.error.code === 'VALIDATION_ERROR') {
        throw new Error(response.error.message || 'Upload already confirmed or invalid.');
      }
      
      throw new Error(response.error.message || 'Failed to confirm upload');
    }

    return response.data as unknown as ConfirmUploadResponse;
  } catch (error: any) {
    // Handle network errors
    if (error.message?.includes('network') || error.message?.includes('timeout')) {
      throw new Error('Network error. Please check your connection and try again.');
    }
    
    throw error;
  }
}
