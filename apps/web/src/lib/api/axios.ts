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

apiClient.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

apiClient.interceptors.response.use(
  response => response,
  error => Promise.reject(error)
)

export default apiClient
