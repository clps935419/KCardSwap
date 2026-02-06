/**
 * SDK Configuration
 *
 * Configures the generated OpenAPI SDK to use our custom axios client
 * with proper authentication and base URL settings.
 */

import { apiClient } from '@/lib/api/axios'
import { client } from './generated/client.gen'

/**
 * Initialize SDK configuration
 *
 * This must be called before using any SDK methods.
 * It configures the SDK to use our axios client instance.
 */
export function initializeSDK() {
  // Get base URL from environment
  const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // Configure hey-api client
  client.setConfig({
    axios: apiClient,
    baseURL,
    withCredentials: true,
  })
}

// Initialize SDK on module load
initializeSDK()
