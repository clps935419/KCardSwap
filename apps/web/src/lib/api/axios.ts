import axios, { type AxiosInstance } from 'axios'

/**
 * API Client Configuration
 *
 * Axios instance configured for backend API communication with:
 * - Cookie-based authentication (httpOnly cookies)
 * - Automatic credentials (withCredentials: true)
 * - Base URL from environment variable
 */

const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  withCredentials: true, // Enable cookies for cross-origin requests
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor (for logging, etc.)
apiClient.interceptors.request.use(
  config => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor (for global error handling)
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (process.env.NODE_ENV === 'development') {
      console.error('[API Error]', error.response?.status, error.response?.data)
    }
    return Promise.reject(error)
  }
)

export default apiClient
