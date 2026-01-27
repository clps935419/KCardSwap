/**
 * Client-side Google OAuth utilities
 *
 * This module handles browser-side Google OAuth login flow:
 * 1. User clicks login button
 * 2. Browser opens Google OAuth popup/redirect
 * 3. Google returns ID token to browser
 * 4. Browser sends ID token to backend /api/v1/auth/google-login
 * 5. Backend sets httpOnly cookies (access_token, refresh_token)
 * 6. Browser redirects to app
 */

import { AuthenticationService, ProfileService } from '@/shared/api/generated'

/**
 * Initialize Google OAuth client
 * This should be called once when the app loads
 */
export function initGoogleOAuth() {
  // Load Google Identity Services script if not already loaded
  if (typeof window === 'undefined') return

  if (!document.getElementById('google-identity-services')) {
    const script = document.createElement('script')
    script.id = 'google-identity-services'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    document.head.appendChild(script)
  }
}

/**
 * Google OAuth login using One Tap
 * Browser receives the ID token and sends it to backend
 *
 * Note: This implementation only supports One Tap flow.
 * If One Tap is not available, user should try again or check browser settings.
 */
export async function loginWithGoogle(): Promise<void> {
  return new Promise((resolve, reject) => {
    // Wait for Google Identity Services to load
    const checkGoogleLoaded = setInterval(() => {
      if (typeof window !== 'undefined' && (window as any).google) {
        clearInterval(checkGoogleLoaded)

        const google = (window as any).google
        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID

        if (!clientId) {
          reject(
            new Error('Google Client ID not configured. Please set NEXT_PUBLIC_GOOGLE_CLIENT_ID')
          )
          return
        }

        // Initialize Google OAuth client
        google.accounts.id.initialize({
          client_id: clientId,
          callback: async (response: any) => {
            try {
              // Send ID token to backend
              await handleGoogleCallback(response.credential)
              resolve()
            } catch (error) {
              reject(error)
            }
          },
          auto_select: false,
          cancel_on_tap_outside: true,
        })

        // Show One Tap prompt
        google.accounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            // One Tap not available
            reject(new Error('Google One Tap 無法使用，請檢查瀏覽器設定或稍後再試'))
          }
        })
      }
    }, 100)

    // Timeout after 5 seconds
    setTimeout(() => {
      clearInterval(checkGoogleLoaded)
      reject(new Error('Google Identity Services failed to load'))
    }, 5000)
  })
}

/**
 * Send Google ID token to backend using SDK
 */
async function handleGoogleCallback(idToken: string): Promise<void> {
  console.log('[Google OAuth] Sending ID token to backend')

  try {
    const response = await AuthenticationService.googleLoginApiV1AuthGoogleLoginPost({
      requestBody: {
        google_token: idToken,
      },
    })

    console.log('[Google OAuth] Login successful:', response.data?.email)

    // Backend has set httpOnly cookies (access_token, refresh_token)
    // Browser will automatically include them in future requests
  } catch (error: any) {
    console.error('[Google OAuth] Backend login failed:', error)
    throw new Error('登入失敗，請稍後再試')
  }
}

/**
 * Check if user is authenticated by testing if cookies work
 */
export async function checkAuth(): Promise<boolean> {
  try {
    // Try to fetch a protected endpoint using SDK
    // If we get 401, user is not authenticated
    await ProfileService.getMyProfileApiV1ProfileMeGet()
    return true
  } catch (_error) {
    return false
  }
}

/**
 * Logout by calling backend logout endpoint using SDK
 */
export async function logout(): Promise<void> {
  try {
    await AuthenticationService.logoutApiV1AuthLogoutPost()
  } catch (_error) {
    // Ignore errors on logout
  }

  // Redirect to login page
  window.location.href = '/login'
}
