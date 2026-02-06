import { logoutApiV1AuthLogoutPost, refreshTokenApiV1AuthRefreshPost } from '@/shared/api/generated'

/**
 * Auth Refresh Module
 *
 * Handles token refresh by calling the backend refresh endpoint.
 * The backend will:
 * 1. Read the refresh token from httpOnly cookie
 * 2. Validate it
 * 3. Issue a new access token in httpOnly cookie
 * 4. Return success/failure
 */

/**
 * Refresh the access token using the refresh token cookie.
 *
 * @throws Error if refresh fails
 */
export async function refreshAccessToken(): Promise<void> {
  try {
    // Call refresh endpoint using SDK
    // Backend will read refresh_token from httpOnly cookie
    // and set new access_token in httpOnly cookie
    await refreshTokenApiV1AuthRefreshPost()

    // Success - new access token is now in cookie
    return
  } catch (error) {
    console.error('[Auth Refresh] Failed to refresh token:', error)
    throw error
  }
}

/**
 * Logout by clearing cookies and redirecting to login.
 */
export async function logout(): Promise<void> {
  try {
    // Call logout endpoint to clear cookies on server side using SDK
    await logoutApiV1AuthLogoutPost()
  } catch (error) {
    console.error('[Auth] Logout error:', error)
  } finally {
    // Redirect to login regardless of API call result
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  }
}
