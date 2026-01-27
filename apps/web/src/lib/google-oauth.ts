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
            new Error('Google Client ID 未設定，請聯絡管理員')
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
            reject(new Error('Google One Tap 無法使用。請確認：\n1. 瀏覽器允許第三方 Cookie\n2. 未封鎖彈出視窗\n3. 使用 Chrome、Edge 或 Safari 瀏覽器'))
          }
        })
      }
    }, 100)

    // Timeout after 5 seconds
    setTimeout(() => {
      clearInterval(checkGoogleLoaded)
      reject(new Error('Google 登入服務載入逾時，請重新整理頁面後再試'))
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
    
    // Extract detailed error message from backend response
    const errorMessage = 
      error?.body?.error?.message ||
      error?.response?.data?.error?.message ||
      error?.message ||
      '登入失敗，請稍後再試'
    
    // Provide specific error messages for common issues
    if (errorMessage.includes('token') || errorMessage.includes('invalid')) {
      throw new Error('Google 驗證失敗，請重新嘗試登入')
    } else if (errorMessage.includes('network') || errorMessage.includes('timeout')) {
      throw new Error('網路連線問題，請檢查您的網路連線')
    } else if (errorMessage.includes('not found') || errorMessage.includes('user')) {
      throw new Error('無法找到使用者資訊，請聯絡管理員')
    } else {
      throw new Error(`登入失敗：${errorMessage}`)
    }
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
