/**
 * SDK Configuration
 * 
 * Configures the generated OpenAPI SDK to use our custom axios client
 * with proper authentication and base URL settings.
 */

import { OpenAPI } from './generated';
import { apiClient } from '@/lib/api/axios';

/**
 * Initialize SDK configuration
 * 
 * This must be called before using any SDK methods.
 * It configures the SDK to use our axios client instance.
 */
export function initializeSDK() {
  // Get base URL from environment
  const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  // Configure OpenAPI SDK
  OpenAPI.BASE = baseURL;
  OpenAPI.WITH_CREDENTIALS = true;
  OpenAPI.CREDENTIALS = 'include';
}

/**
 * Get the configured axios client for SDK usage
 */
export function getAxiosClient() {
  return apiClient;
}

// Initialize SDK on module load
initializeSDK();
