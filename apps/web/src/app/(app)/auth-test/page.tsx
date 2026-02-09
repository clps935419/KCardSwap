'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { checkAuth, initGoogleOAuth, loginWithGoogle, logout } from '@/lib/google-oauth'
import { getMyProfileApiV1ProfileMeGet, type ProfileResponse } from '@/shared/api/generated'

/**
 * Auth Test Page
 * 測試 Cookie-based 認證整合是否正常運作
 *
 * 訪問路徑: /auth-test
 *
 * 功能：
 * - 顯示目前的認證狀態（基於 httpOnly cookies）
 * - 顯示使用者資訊（從後端 API 取得）
 * - 提供登入/登出按鈕
 */
export default function AuthTestPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [userInfo, setUserInfo] = useState<ProfileResponse | null>(null)
  const [error, setError] = useState('')

  // Check auth status and fetch user info on mount
  useEffect(() => {
    initGoogleOAuth()

    const fetchUserInfo = async () => {
      try {
        const response = await getMyProfileApiV1ProfileMeGet()
        setUserInfo(response.data?.data ?? null)
      } catch (err) {
        console.error('Failed to fetch user info:', err)
      }
    }

    const initAuth = async () => {
      setIsLoading(true)
      const authenticated = await checkAuth()
      setIsAuthenticated(authenticated)

      if (authenticated) {
        await fetchUserInfo()
      }

      setIsLoading(false)
    }

    initAuth()
  }, [])

  const fetchUserInfo = async () => {
    try {
      const response = await getMyProfileApiV1ProfileMeGet()
      setUserInfo(response.data?.data ?? null)
    } catch (err) {
      console.error('Failed to fetch user info:', err)
    }
  }

  const handleLogin = async () => {
    setError('')
    setIsLoading(true)

    try {
      await loginWithGoogle()
      // Re-check auth status after login
      const authenticated = await checkAuth()
      setIsAuthenticated(authenticated)
      if (authenticated) {
        await fetchUserInfo()
      }
      setIsLoading(false)
    } catch (err: unknown) {
      const error = err as Error
      setError(error.message || 'Google 登入失敗')
      setIsLoading(false)
    }
  }

  const handleCheckStatus = async () => {
    setIsLoading(true)
    const authenticated = await checkAuth()
    setIsAuthenticated(authenticated)
    if (authenticated) {
      await fetchUserInfo()
    }
    setIsLoading(false)
  }

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">登入狀態檢查</h1>

        {/* Status */}
        <div className="bg-card border rounded-lg p-6 mb-4">
          <h2 className="text-xl font-semibold mb-4">登入狀態</h2>
          <div className="space-y-2">
            <div className="flex gap-2">
              <span className="font-medium">狀態：</span>
              <span
                className={`font-mono ${
                  isAuthenticated
                    ? 'text-green-600'
                    : isLoading
                      ? 'text-yellow-600'
                      : 'text-red-600'
                }`}
              >
                {isLoading ? '載入中' : isAuthenticated ? '已登入' : '未登入'}
              </span>
            </div>
          </div>
        </div>

        {/* User Info */}
        {isAuthenticated && userInfo && (
          <div className="bg-card border rounded-lg p-6 mb-4">
            <h2 className="text-xl font-semibold mb-4">使用者資訊</h2>
            <div className="space-y-2">
              <div className="flex gap-2">
                <span className="font-medium">使用者代碼：</span>
                <span className="font-mono text-sm">{userInfo.user_id || 'N/A'}</span>
              </div>
              <div className="flex gap-2">
                <span className="font-medium">暱稱：</span>
                <span className="font-mono text-sm">{userInfo.nickname || 'N/A'}</span>
              </div>
            </div>

            <details className="mt-4">
              <summary className="cursor-pointer font-medium">原始使用者資料</summary>
              <pre className="mt-2 p-4 bg-muted rounded-lg overflow-auto text-xs">
                {JSON.stringify(userInfo, null, 2)}
              </pre>
            </details>
          </div>
        )}

        {/* Loading */}
        {isLoading && !isAuthenticated && (
          <div className="bg-card border rounded-lg p-6 mb-4">
            <p className="text-center text-muted-foreground">載入中...</p>
          </div>
        )}

        {/* Unauthenticated */}
        {!isLoading && !isAuthenticated && (
          <div className="bg-card border rounded-lg p-6 mb-4">
            <p className="text-center text-muted-foreground mb-4">您尚未登入</p>
            {error && <p className="text-center text-destructive text-sm">{error}</p>}
          </div>
        )}

        {/* Actions */}
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">操作</h2>
          <div className="flex flex-wrap gap-3">
            {isAuthenticated ? (
              <>
                <Button onClick={handleLogout} variant="destructive">
                  登出
                </Button>
                <Button onClick={handleCheckStatus} variant="outline">
                  重新檢查狀態
                </Button>
              </>
            ) : (
              <Button onClick={handleLogin} disabled={isLoading}>
                使用 Google 登入
              </Button>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-muted/50 border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">說明</h2>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>這是登入狀態的檢查頁，用於確認帳號是否可正常使用。</p>
            <p>若登入異常，請重新登入或稍後再試。</p>
          </div>
        </div>
      </div>
    </div>
  )
}
