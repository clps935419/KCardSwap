'use client'

import { signIn, signOut, useSession } from 'next-auth/react'
import { Button } from '@/components/ui/button'

/**
 * Auth Test Page
 * 測試 NextAuth 整合是否正常運作
 *
 * 訪問路徑: /auth-test
 *
 * 功能：
 * - 顯示目前的 session 狀態
 * - 顯示使用者資訊
 * - 提供登入/登出按鈕
 */
export default function AuthTestPage() {
  const { data: session, status } = useSession()

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">NextAuth 測試頁面</h1>

        {/* Status */}
        <div className="bg-card border rounded-lg p-6 mb-4">
          <h2 className="text-xl font-semibold mb-4">Session 狀態</h2>
          <div className="space-y-2">
            <div className="flex gap-2">
              <span className="font-medium">Status:</span>
              <span
                className={`font-mono ${
                  status === 'authenticated'
                    ? 'text-green-600'
                    : status === 'loading'
                      ? 'text-yellow-600'
                      : 'text-red-600'
                }`}
              >
                {status}
              </span>
            </div>
          </div>
        </div>

        {/* Session Data */}
        {status === 'authenticated' && session && (
          <div className="bg-card border rounded-lg p-6 mb-4">
            <h2 className="text-xl font-semibold mb-4">使用者資訊</h2>
            <div className="space-y-2">
              <div className="flex gap-2">
                <span className="font-medium">User ID:</span>
                <span className="font-mono text-sm">{session.user?.id || 'N/A'}</span>
              </div>
              <div className="flex gap-2">
                <span className="font-medium">Email:</span>
                <span className="font-mono text-sm">{session.user?.email || 'N/A'}</span>
              </div>
              <div className="flex gap-2">
                <span className="font-medium">Name:</span>
                <span className="font-mono text-sm">{session.user?.name || 'N/A'}</span>
              </div>
            </div>

            <details className="mt-4">
              <summary className="cursor-pointer font-medium">原始 Session 資料</summary>
              <pre className="mt-2 p-4 bg-muted rounded-lg overflow-auto text-xs">
                {JSON.stringify(session, null, 2)}
              </pre>
            </details>
          </div>
        )}

        {/* Loading */}
        {status === 'loading' && (
          <div className="bg-card border rounded-lg p-6 mb-4">
            <p className="text-center text-muted-foreground">載入中...</p>
          </div>
        )}

        {/* Unauthenticated */}
        {status === 'unauthenticated' && (
          <div className="bg-card border rounded-lg p-6 mb-4">
            <p className="text-center text-muted-foreground mb-4">您尚未登入</p>
          </div>
        )}

        {/* Actions */}
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">操作</h2>
          <div className="flex flex-wrap gap-3">
            {status === 'authenticated' ? (
              <>
                <Button onClick={() => signOut({ callbackUrl: '/login' })} variant="destructive">
                  登出
                </Button>
                <Button onClick={() => window.location.reload()} variant="outline">
                  重新整理
                </Button>
              </>
            ) : (
              <>
                <Button onClick={() => signIn('google', { callbackUrl: '/auth-test' })}>
                  使用 Google 登入
                </Button>
                <Button onClick={() => signIn('google', { callbackUrl: '/' })} variant="outline">
                  登入並導向首頁
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-muted/50 border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">說明</h2>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>✅ 此頁面用於測試 NextAuth 整合是否正常運作</p>
            <p>✅ 確保已設定正確的環境變數（GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET）</p>
            <p>
              ✅ Google OAuth redirect URI 應設定為:{' '}
              <code className="bg-muted px-1 py-0.5 rounded">
                {typeof window !== 'undefined'
                  ? `${window.location.origin}/api/auth/callback/google`
                  : 'http://localhost:3000/api/auth/callback/google'}
              </code>
            </p>
            <p>✅ 成功登入後，session 資料會顯示在上方</p>
          </div>
        </div>
      </div>
    </div>
  )
}
