'use client'

import { useState } from 'react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Check if running in development mode
  const isDev = process.env.NODE_ENV === 'development'

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

      // Store tokens (you may want to use httpOnly cookies in production)
      if (response.data) {
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)
        // Redirect to home or dashboard
        window.location.href = '/'
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || '登入失敗，請檢查帳號密碼')
    } finally {
      setIsLoading(false)
    }
  }

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
        <p className="text-xs text-muted-foreground mt-1 tracking-wide font-medium">
          貼文優先 POC • Web 流程
        </p>
      </div>

      {/* Content Section */}
      <div className="w-full max-w-md space-y-3">
        {/* Info Card */}
        <div className="bg-card border border-border/30 rounded-2xl p-4">
          <p className="text-xs text-muted-foreground">
            <span className="font-black text-foreground">所有瀏覽需登入（V2 決策）</span>
          </p>
          <p className="text-[11px] text-muted-foreground mt-1">
            登入後才能瀏覽貼文、相簿與信箱
          </p>
        </div>

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
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"
                required
              />
              <input
                type="password"
                placeholder="密碼"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"
                required
              />
              {error && (
                <p className="text-xs text-red-600 font-medium">{error}</p>
              )}
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

        {/* Google Login Button */}
        <button className="w-full h-16 bg-gradient-to-r from-secondary-50 to-rose-50 border-2 border-secondary-300 rounded-2xl flex items-center justify-center px-6 hover:from-secondary-50/80 hover:to-rose-50/80 transition-all shadow-md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-xl shadow flex items-center justify-center font-black">
              G
            </div>
            <div className="text-left">
              <p className="text-sm font-black text-foreground">使用 Google 登入</p>
              <p className="text-[10px] text-muted-foreground">
                登入後才能瀏覽貼文、相簿與信箱
              </p>
            </div>
          </div>
        </button>

        {/* POC Info */}
        <div className="bg-slate-900 text-slate-200 rounded-2xl p-4">
          <p className="text-xs font-bold text-white">POC 互動路徑</p>
          <p className="text-[11px] mt-1 opacity-80">
            貼文 → 私信作者（送出請求）→ 收件者接受 → 信箱對話
          </p>
        </div>
      </div>
    </div>
  )
}
