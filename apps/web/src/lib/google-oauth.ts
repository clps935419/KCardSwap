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
        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || process.env.GOOGLE_CLIENT_ID

        if (!clientId) {
          reject(new Error('Google Client ID not configured'))
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
 * Send Google ID token to backend
 */
async function handleGoogleCallback(idToken: string): Promise<void> {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  console.log('[Google OAuth] Sending ID token to backend')

  const response = await fetch(`${backendUrl}/api/v1/auth/google-login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Important: includes cookies in request/response
    body: JSON.stringify({
      google_token: idToken,
    }),
  })

  if (!response.ok) {
    const error = await response.text()
    console.error('[Google OAuth] Backend login failed:', error)
    throw new Error('登入失敗，請稍後再試')
  }

  const data = await response.json()
  console.log('[Google OAuth] Login successful:', data.data?.email)

  // Backend has set httpOnly cookies (access_token, refresh_token)
  // Browser will automatically include them in future requests
}

/**
 * Check if user is authenticated by testing if cookies work
 */
export async function checkAuth(): Promise<boolean> {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  try {
    // Try to fetch a protected endpoint
    // If we get 401, user is not authenticated
    const response = await fetch(`${backendUrl}/api/v1/users/me`, {
      method: 'GET',
      credentials: 'include',
    })

    return response.ok
  } catch (_error) {
    return false
  }
}

/**
 * Logout by calling backend logout endpoint
 */
export async function logout(): Promise<void> {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  await fetch(`${backendUrl}/api/v1/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })

  // Redirect to login page
  window.location.href = '/login'
}
