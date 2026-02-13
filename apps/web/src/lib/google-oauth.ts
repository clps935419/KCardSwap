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

import {
  getMyProfileApiV1ProfileMeGet,
  googleLoginApiV1AuthGoogleLoginPost,
  logoutApiV1AuthLogoutPost,
} from '@/shared/api/generated'

type GoogleCredentialResponse = {
  credential?: string
}

type GooglePromptNotification = {
  isNotDisplayed: () => boolean
  isSkippedMoment: () => boolean
  getNotDisplayedReason?: () => string
  getSkippedReason?: () => string
}

type GoogleButtonOptions = {
  theme: 'outline' | 'filled_blue' | 'filled_black'
  size: 'large' | 'medium' | 'small'
  shape: 'pill' | 'rect' | 'circle' | 'square'
  text: 'continue_with' | 'signin_with' | 'signup_with'
  width: number
}

type GoogleInitializeConfig = {
  client_id: string
  callback: (response: GoogleCredentialResponse) => void
  auto_select?: boolean
  cancel_on_tap_outside?: boolean
  use_fedcm_for_prompt?: boolean
}

type GoogleIdentity = {
  accounts: {
    id: {
      initialize: (config: GoogleInitializeConfig) => void
      prompt: (callback: (notification: GooglePromptNotification) => void) => void
      renderButton: (container: HTMLElement, options: GoogleButtonOptions) => void
    }
  }
}

function getGoogleIdentityFromWindow(): GoogleIdentity | null {
  const maybeWindow = window as unknown as { google?: GoogleIdentity }
  return maybeWindow.google ?? null
}

function getErrorMessage(error: unknown): string {
  if (error && typeof error === 'object') {
    const err = error as {
      body?: { error?: { message?: string } }
      response?: { data?: { error?: { message?: string } } }
      message?: string
    }
    return (
      err.body?.error?.message ||
      err.response?.data?.error?.message ||
      err.message ||
      '登入失敗，請稍後再試'
    )
  }

  return '登入失敗，請稍後再試'
}

async function waitForGoogleIdentityServices(timeoutMs = 8000): Promise<GoogleIdentity> {
  if (typeof window === 'undefined') {
    throw new Error('window 不存在（可能在 SSR 環境）')
  }

  return new Promise((resolve, reject) => {
    let timeoutId: ReturnType<typeof setTimeout> | null = null

    const checkGoogleLoaded = setInterval(() => {
      const googleIdentity = getGoogleIdentityFromWindow()
      if (googleIdentity) {
        clearInterval(checkGoogleLoaded)
        if (timeoutId) {
          clearTimeout(timeoutId)
          timeoutId = null
        }
        resolve(googleIdentity)
      }
    }, 100)

    timeoutId = setTimeout(() => {
      clearInterval(checkGoogleLoaded)
      reject(new Error('Google 登入服務載入逾時，請重新整理頁面後再試'))
    }, timeoutMs)
  })
}

/**
 * Initialize Google OAuth client
 * This should be called once when the app loads
 */
export function initGoogleOAuth() {
  // Load Google Identity Services script if not already loaded
  if (typeof window === 'undefined') {
    return
  }

  if (!document.getElementById('google-identity-services')) {
    const script = document.createElement('script')
    script.id = 'google-identity-services'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true

    script.onload = () => {}

    script.onerror = () => {
      console.error('[Google OAuth] ❌ Google Identity Services script 載入失敗')
    }

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
    let isSettled = false
    let timeoutId: ReturnType<typeof setTimeout> | null = null

    // Wait for Google Identity Services to load
    const checkGoogleLoaded = setInterval(() => {
      if (typeof window !== 'undefined' && getGoogleIdentityFromWindow()) {
        clearInterval(checkGoogleLoaded)
        if (timeoutId) {
          clearTimeout(timeoutId)
          timeoutId = null
        }

        const google = getGoogleIdentityFromWindow()
        if (!google) {
          reject(new Error('Google 登入服務載入失敗'))
          return
        }
        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID

        if (!clientId) {
          console.error('[Google OAuth] ❌ Step 3-FAIL: Client ID 未設定')
          reject(new Error('Google Client ID 未設定，請聯絡管理員'))
          return
        }

        // Initialize Google OAuth client
        google.accounts.id.initialize({
          client_id: clientId,
          use_fedcm_for_prompt: false,
          callback: async (response: GoogleCredentialResponse) => {
            try {
              // Send ID token to backend
              if (!response.credential) {
                throw new Error('Google 回傳憑證不存在')
              }
              await handleGoogleCallback(response.credential)
              if (!isSettled) {
                isSettled = true
                resolve()
              }
            } catch (error) {
              console.error('[Google OAuth] ❌ Step 6-FAIL: 後端處理失敗', error)
              if (!isSettled) {
                isSettled = true
                reject(error)
              }
            }
          },
          auto_select: false,
          cancel_on_tap_outside: true,
        })

        // Show One Tap prompt
        google.accounts.id.prompt((notification: GooglePromptNotification) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            console.error('[Google OAuth] ❌ Step 5-FAIL: One Tap 無法顯示')
            console.error(
              '[Google OAuth] 原因:',
              notification.getNotDisplayedReason?.() || notification.getSkippedReason?.()
            )
            // One Tap not available
            if (!isSettled) {
              isSettled = true
              reject(
                new Error(
                  'Google One Tap 無法使用。請確認：\n1. 瀏覽器允許第三方 Cookie\n2. 未封鎖彈出視窗\n3. 使用 Chrome、Edge 或 Safari 瀏覽器'
                )
              )
            }
          }
        })
      }
    }, 100)

    // Timeout after 5 seconds
    timeoutId = setTimeout(() => {
      clearInterval(checkGoogleLoaded)
      console.error('[Google OAuth] ❌ Step 3-TIMEOUT: Google Identity Services 載入逾時')
      console.error('[Google OAuth] window.google 存在:', !!getGoogleIdentityFromWindow())
      if (!isSettled) {
        isSettled = true
        reject(new Error('Google 登入服務載入逾時，請重新整理頁面後再試'))
      }
    }, 5000)
  })
}

export async function renderGoogleButton(
  containerId: string,
  onSuccess?: () => void,
  onError?: (error: Error) => void
): Promise<void> {
  try {
    const google = await waitForGoogleIdentityServices()
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID

    if (!clientId) {
      throw new Error('Google Client ID 未設定，請聯絡管理員')
    }

    const container = document.getElementById(containerId)
    if (!container) {
      throw new Error('找不到 Google 按鈕容器')
    }

    if (container.getAttribute('data-google-rendered') === 'true') {
      return
    }

    const rawWidth = container.parentElement?.clientWidth || container.clientWidth || 320
    const buttonWidth = Math.max(200, Math.min(rawWidth, 400))

    google.accounts.id.initialize({
      client_id: clientId,
      callback: async (response: GoogleCredentialResponse) => {
        try {
          if (!response.credential) {
            throw new Error('Google 回傳憑證不存在')
          }
          await handleGoogleCallback(response.credential)
          onSuccess?.()
        } catch (error) {
          const err = error instanceof Error ? error : new Error('Google 登入失敗')
          onError?.(err)
        }
      },
      auto_select: false,
      cancel_on_tap_outside: true,
    })

    container.innerHTML = ''
    google.accounts.id.renderButton(container, {
      theme: 'outline',
      size: 'large',
      shape: 'pill',
      text: 'continue_with',
      width: buttonWidth,
    })

    container.setAttribute('data-google-rendered', 'true')
  } catch (error) {
    const err = error instanceof Error ? error : new Error('Google 登入初始化失敗')
    onError?.(err)
  }
}

/**
 * Send Google ID token to backend using SDK
 */
async function handleGoogleCallback(idToken: string): Promise<void> {
  try {
    const response = await googleLoginApiV1AuthGoogleLoginPost({
      body: {
        google_token: idToken,
      },
      throwOnError: true,
    })

    // Backend has set httpOnly cookies (access_token, refresh_token)
    // Browser will automatically include them in future requests
    void response
  } catch (error: unknown) {
    console.error('[Google OAuth] ❌ Step 6-FAIL: 後端登入失敗')
    console.error('[Google OAuth] 錯誤物件:', error)

    if (error && typeof error === 'object') {
      const err = error as {
        body?: unknown
        response?: unknown
        message?: string
        status?: unknown
      }
      console.error('[Google OAuth] 錯誤 body:', err.body)
      console.error('[Google OAuth] 錯誤 response:', err.response)
      console.error('[Google OAuth] 錯誤 message:', err.message)
      console.error('[Google OAuth] 錯誤 status:', err.status)
    }

    // Extract detailed error message from backend response
    const errorMessage = getErrorMessage(error)

    console.error('[Google OAuth] 解析後的錯誤訊息:', errorMessage)

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
    await getMyProfileApiV1ProfileMeGet({
      throwOnError: true,
    })
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
    await logoutApiV1AuthLogoutPost({
      throwOnError: true,
    })
  } catch (_error) {
    // Ignore errors on logout
  }
}
