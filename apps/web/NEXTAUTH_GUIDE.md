# NextAuth.js 整合指南

## 概述

本專案使用 NextAuth.js v4 進行身份驗證，支援 Google OAuth 登入。NextAuth 與後端 API 整合，在使用者登入時自動與後端建立 session。

## 架構說明

### 認證流程

1. 使用者點擊「使用 Google 登入」
2. NextAuth 導向 Google OAuth 頁面
3. Google 驗證成功後，返回 Google ID token
4. NextAuth 將 Google ID token 發送到後端 `/api/v1/auth/google-login`
5. 後端驗證 token 並創建/更新使用者
6. 後端返回 JWT tokens (access + refresh)
7. Tokens 儲存在 httpOnly cookies 中（由後端設定）
8. NextAuth 建立 session，儲存使用者資訊

### 檔案結構

```
apps/web/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...nextauth]/
│   │   │           └── route.ts          # NextAuth API route
│   │   ├── (auth)/
│   │   │   └── login/
│   │   │       └── page.tsx              # 登入頁面
│   │   └── providers.tsx                 # SessionProvider
│   ├── lib/
│   │   └── auth/
│   │       ├── config.ts                 # NextAuth 設定
│   │       ├── utils.ts                  # Auth 工具函式
│   │       ├── types.ts                  # 型別定義
│   │       └── index.ts                  # 匯出
│   └── proxy.ts                          # 路由保護（Next.js 16+）
```

## 環境變數

在 `.env.local` 中設定以下環境變數：

```env
# NextAuth
NEXTAUTH_SECRET=your-secret-here          # 使用 openssl rand -base64 32 生成
NEXTAUTH_URL=http://localhost:3000        # 前端 URL

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 使用方式

### 在 Client Component 中

```typescript
'use client'

import { useSession, signIn, signOut } from 'next-auth/react'

export default function MyComponent() {
  const { data: session, status } = useSession()
  
  if (status === 'loading') {
    return <div>載入中...</div>
  }
  
  if (!session) {
    return <button onClick={() => signIn('google')}>登入</button>
  }
  
  return (
    <div>
      <p>歡迎, {session.user.email}</p>
      <button onClick={() => signOut()}>登出</button>
    </div>
  )
}
```

### 在 Server Component 中

```typescript
import { getSession, getCurrentUser } from '@/lib/auth'

export default async function MyServerComponent() {
  const session = await getSession()
  
  if (!session) {
    redirect('/login')
  }
  
  return <div>歡迎, {session.user.email}</div>
}
```

### 在 API Route 中

```typescript
import { getSession } from '@/lib/auth'
import { NextResponse } from 'next/server'

export async function GET() {
  const session = await getSession()
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  // 處理已認證的請求
  return NextResponse.json({ user: session.user })
}
```

### 路由保護

`proxy.ts` 已設定為保護所有路由（除了 `/login` 和公開頁面）。

**注意**: Next.js 16 將 `middleware.ts` 重新命名為 `proxy.ts`。這是一個輕量級的認證檢查層，僅檢查 session token 的存在，完整的 session 驗證仍在 Server Components 和 API routes 中進行。

如需調整受保護的路由，編輯 `src/proxy.ts` 中的 `matcher` 設定。

## API 呼叫

所有的 API 呼叫都應該使用 `withCredentials: true`，這樣 httpOnly cookies 才會被包含在請求中。

這已經在 `src/lib/api/axios.ts` 中設定好了。

## 開發注意事項

### Google OAuth 設定

1. 前往 [Google Cloud Console](https://console.developers.google.com/)
2. 建立專案或選擇現有專案
3. 啟用 Google+ API
4. 建立 OAuth 2.0 憑證
5. 新增授權的重新導向 URI:
   - 開發環境: `http://localhost:3000/api/auth/callback/google`
   - 正式環境: `https://yourdomain.com/api/auth/callback/google`

### Session 管理

- Session 有效期: 7 天
- Access token 有效期: 15 分鐘（由後端設定）
- Token 會自動刷新（透過後端的 refresh endpoint）

### 安全性

- Tokens 儲存在 httpOnly cookies 中，無法被 JavaScript 存取
- CSRF 保護由 NextAuth 自動處理
- 確保在正式環境中使用 HTTPS

## 除錯

### 查看 Session 狀態

在 Client Component 中使用 `useSession()` hook:

```typescript
const { data: session, status } = useSession()
console.log('Session:', session)
console.log('Status:', status) // 'loading' | 'authenticated' | 'unauthenticated'
```

### NextAuth Debug Mode

在 `.env.local` 中加入:

```env
NEXTAUTH_DEBUG=true
```

這會在 console 中顯示詳細的 debug 訊息。

## 常見問題

### Q: 如何處理 Token 過期？

A: Token 刷新由後端的 axios interceptor 自動處理（見 `src/lib/api/axios-interceptors.ts`）。當收到 401 錯誤時，會自動嘗試刷新 token。

### Q: 如何手動觸發登出？

A: 使用 `signOut()` function:

```typescript
import { signOut } from 'next-auth/react'

// 登出並重定向到登入頁
signOut({ callbackUrl: '/login' })
```

### Q: 如何取得目前使用者的資訊？

A: 在 Client Component 中使用 `useSession()`，在 Server Component 中使用 `getSession()` 或 `getCurrentUser()`。

## 相關連結

- [NextAuth.js 文件](https://next-auth.js.org/)
- [Google OAuth Provider](https://next-auth.js.org/providers/google)
- [後端 API 文件](../../backend/README.md)
