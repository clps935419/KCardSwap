import type { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { refreshAccessToken } from './auth-refresh'
import { apiClient } from './axios'

/**
 * Auth Refresh Interceptor
 *
 * Automatically handles 401 errors by:
 * 1. Attempting to refresh the access token via refresh endpoint
 * 2. Retrying the original request if refresh succeeds
 * 3. Redirecting to login if refresh fails
 */

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: Error | null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve()
    }
  })

  failedQueue = []
}

// Response interceptor for handling 401 and refresh logic
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => {
            return apiClient(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // Attempt to refresh the access token
        await refreshAccessToken()

        // Refresh succeeded, process queued requests
        processQueue(null)
        isRefreshing = false

        // Retry original request
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, reject all queued requests
        processQueue(refreshError as Error)
        isRefreshing = false

        // Redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }

        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export { apiClient }
