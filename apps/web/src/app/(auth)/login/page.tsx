'use client'

import { GoogleOAuthProvider, useGoogleLogin } from '@react-oauth/google'
import { useEffect, useState } from 'react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [googleError, setGoogleError] = useState('')

  // Check if running in development mode
  const isDev = process.env.NODE_ENV === 'development'
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Import SDK dynamically to avoid build issues
      const { AuthenticationService } = await import('@/shared/api/generated')

      const response = await AuthenticationService.adminLoginApiV1AuthAdminLoginPost({
        requestBody: {
          email,
          password,
        },
      })

      // Tokens are now stored in httpOnly cookies automatically
      // No need to manually store them in localStorage
      if (response.data) {
        // Redirect to posts feed after login
        window.location.href = '/posts'
      }
    } catch (err: unknown) {
      // More robust error parsing
      let errorMessage = '登入失敗，請檢查帳號密碼'
      
      if (err && typeof err === 'object') {
        const error = err as { 
          response?: { 
            data?: { 
              error?: { message?: string }
              detail?: { message?: string }
              message?: string
            }
          }
          message?: string
        }
        
        errorMessage = 
          error.response?.data?.error?.message ||
          error.response?.data?.detail?.message ||
          error.response?.data?.message ||
          error.message ||
          errorMessage
      }
      
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <LoginPageContent
        email={email}
        setEmail={setEmail}
        password={password}
        setPassword={setPassword}
        error={error}
        isLoading={isLoading}
        googleError={googleError}
        setGoogleError={setGoogleError}
        isDev={isDev}
        handleAdminLogin={handleAdminLogin}
      />
    </GoogleOAuthProvider>
  )
}

interface LoginPageContentProps {
  email: string
  setEmail: (email: string) => void
  password: string
  setPassword: (password: string) => void
  error: string
  isLoading: boolean
  googleError: string
  setGoogleError: (error: string) => void
  isDev: boolean
  handleAdminLogin: (e: React.FormEvent) => void
}

function LoginPageContent({
  email,
  setEmail,
  password,
  setPassword,
  error,
  isLoading,
  googleError,
  setGoogleError,
  isDev,
  handleAdminLogin,
}: LoginPageContentProps) {
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)

  const googleLogin = useGoogleLogin({
    flow: 'auth-code',
    onSuccess: async codeResponse => {
      console.log('[Google OAuth] Authorization code received')
      setIsGoogleLoading(true)
      setGoogleError('')

      try {
        // Import SDK dynamically to avoid build issues
        const { AuthenticationService } = await import('@/shared/api/generated')

        // Get the redirect_uri that was used in the authorization request
        // @react-oauth/google uses window.location.origin by default
        const redirectUri = window.location.origin

        // Send authorization code to backend with redirect_uri for OAuth 2.0 validation
        const response = await AuthenticationService.googleLoginCodeApiV1AuthGoogleLoginCodePost({
          requestBody: {
            code: codeResponse.code,
            redirect_uri: redirectUri,
          },
        })

        if (response.data) {
          // Redirect to posts feed after login
          window.location.href = '/posts'
        }
      } catch (err: unknown) {
        // More robust error parsing
        let errorMessage = 'Google 登入失敗，請稍後再試'
        
        if (err && typeof err === 'object') {
          const error = err as { 
            response?: { 
              data?: { 
                error?: { message?: string }
                detail?: { message?: string }
                message?: string
              }
            }
            message?: string
          }
          
          errorMessage = 
            error.response?.data?.error?.message ||
            error.response?.data?.detail?.message ||
            error.response?.data?.message ||
            error.message ||
            errorMessage
        }
        
        setGoogleError(errorMessage)
      } finally {
        setIsGoogleLoading(false)
      }
    },
    onError: error => {
      console.error('[Google OAuth] Error:', error)
      setGoogleError('Google 登入失敗，請稍後再試')
    },
  })

  return (
    <div className="flex min-h-screen items-center justify-between flex-col bg-gradient-to-b from-slate-50 to-white p-8 py-20">
      {/* Logo Section */}
      <div className="text-center">
        <div className="w-20 h-20 bg-secondary-50 rounded-3xl mx-auto flex items-center justify-center shadow-2xl shadow-secondary-300/30 mb-4 ring-4 ring-secondary-50">
          <div className="w-14 h-14 bg-gradient-to-br from-secondary-500 to-rose-400 rounded-2xl flex items-center justify-center text-white font-black text-xl">
            S!
          </div>
        </div>
        <h2 className="text-2xl font-black text-secondary-500">小卡Show!</h2>
      </div>

      {/* Content Section */}
      <div className="w-full max-w-md space-y-3">
        {/* Admin Login Form (Dev Only) */}
        {isDev && (
          <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 bg-amber-400 rounded-lg flex items-center justify-center text-white font-black text-sm">
                🔐
              </div>
              <p className="text-xs font-black text-amber-900">開發模式：管理員登入</p>
            </div>
            <form onSubmit={handleAdminLogin} className="space-y-2">
              <input
                type="email"
                placeholder="管理員 Email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"
                required
              />
              <input
                type="password"
                placeholder="密碼"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"
                required
              />
              {error && <p className="text-xs text-red-600 font-medium">{error}</p>}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 bg-amber-500 text-white text-sm font-bold rounded-lg hover:bg-amber-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '登入中...' : '管理員登入'}
              </button>
            </form>
          </div>
        )}

        {/* Custom Google Login Button */}
        <div className="space-y-2">
          <button
            onClick={() => googleLogin()}
            disabled={isGoogleLoading}
            className="w-full h-14 bg-gradient-to-r from-pink-50 to-rose-50 border-2 border-pink-200 rounded-2xl hover:from-pink-100 hover:to-rose-100 transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 px-6"
          >
            {isGoogleLoading ? (
              <>
                <svg
                  className="animate-spin h-5 w-5 text-slate-500"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <p className="text-sm font-black text-slate-500">登入中...</p>
              </>
            ) : (
              <>
                <svg className="w-6 h-6" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <p className="text-sm font-black text-slate-900">使用 Google 登入</p>
              </>
            )}
          </button>
          {googleError && (
            <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-4">
              <div className="flex items-start gap-2">
                <div className="text-lg">⚠️</div>
                <div className="flex-1">
                  <p className="text-xs font-black text-red-900 mb-1">登入錯誤</p>
                  <p className="text-xs text-red-700 whitespace-pre-line">{googleError}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
