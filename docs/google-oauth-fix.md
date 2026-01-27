# Google OAuth 登入流程修正說明

## 問題背景

原先的實作使用 NextAuth.js，但因為 NextAuth 在**伺服器端** (Next.js Route Handler) 呼叫後端的 `/api/v1/auth/google-login`，這導致以下問題：

1. 後端設定的 `Set-Cookie` header 無法傳遞到**瀏覽器**
2. 瀏覽器後續請求缺少 `access_token` 和 `refresh_token` cookies
3. 所有需要認證的 API 請求都收到 401 Unauthorized

**根本原因**: NextAuth JWT callback 中的 fetch 請求是在 Next.js 伺服器端執行的，不是在瀏覽器端。即使使用 `credentials: 'include'`，cookies 也只會在 Next.js server 和 backend server 之間傳遞，不會到達使用者的瀏覽器。

## 解決方案

### 核心改變

**將 Google OAuth 登入改為完全在瀏覽器端執行**，不使用 NextAuth，直接使用 Google Identity Services，確保後端設定的 httpOnly cookies 能正確傳遞到瀏覽器。

### 新的登入流程

```
1. 使用者點擊「使用 Google 登入」按鈕
   └─> 觸發 loginWithGoogle() 函式

2. 瀏覽器載入 Google Identity Services SDK
   └─> 使用 Google One Tap 或 popup 進行 OAuth

3. Google 驗證成功，ID token 直接返回到**瀏覽器**
   └─> callback 函式接收到 credential (ID token)

4. **瀏覽器端** fetch 呼叫後端 /api/v1/auth/google-login
   └─> POST { google_token: idToken }
   └─> credentials: 'include' 確保 cookies 能被接收

5. 後端驗證 token，設定 httpOnly cookies
   └─> Set-Cookie: access_token=...
   └─> Set-Cookie: refresh_token=...
   └─> 這些 cookies **直接存入瀏覽器**

6. 瀏覽器重定向到 /posts
   └─> 後續所有請求自動帶上 cookies
```

## 技術實作細節

### 1. 新增 `src/lib/google-oauth.ts`

核心功能模組，包含：

- `initGoogleOAuth()`: 載入 Google Identity Services SDK
- `loginWithGoogle()`: 處理 Google OAuth 登入（使用 One Tap）
- `handleGoogleCallback()`: 將 ID token 發送到後端
- `checkAuth()`: 檢查使用者是否已登入（透過呼叫 `/api/v1/users/me`）
- `logout()`: 登出並清除 cookies

**關鍵**: 所有 fetch 都使用 `credentials: 'include'` 以確保 cookies 被正確處理。

### 2. 更新登入頁面 `src/app/(auth)/login/page.tsx`

- 移除 `import { signIn } from 'next-auth/react'`
- 使用 `loginWithGoogle()` 取代 `signIn('google')`
- 使用 `useEffect` 在頁面載入時初始化 Google OAuth
- 登入成功後使用 `window.location.href = '/posts'` 重定向

### 3. 更新 Proxy `src/proxy.ts` (Next.js 16)

改用 cookie-based 認證取代 session 檢查：

- 檢查 `access_token` cookie 是否存在
- 未認證使用者訪問受保護路徑 → 重定向到 `/login`
- 已認證使用者訪問 `/login` → 重定向到 `/posts`

**注意**: Next.js 16 使用 `proxy.ts` 而非 `middleware.ts`。Proxy 只檢查 cookie 存在性，完整的 JWT 驗證在後端進行。

### 4. 移除 NextAuth 依賴

完全移除 NextAuth 相關檔案和依賴：

#### 刪除的檔案
- `src/lib/auth/` - 整個目錄（config.ts, utils.ts, types.ts, index.ts）
- `src/app/api/auth/` - 整個目錄（NextAuth API routes）
- 從 `package.json` 移除 `next-auth` 依賴

#### `src/app/providers.tsx`
- 移除 `<SessionProvider>`，只保留 `<QueryClientProvider>`

#### `src/app/(app)/layout.tsx`
- 改用 `fetch('/api/v1/users/me')` 取得使用者資訊（不依賴 session）

#### `src/app/page.tsx`
- 改用 `cookies().get('access_token')` 檢查認證狀態

#### `src/app/(app)/me/gallery/page.tsx`
- 改用 `logout()` from google-oauth

#### `src/app/(app)/auth-test/page.tsx`
- 完全改寫，使用新的認證檢查方式
- 測試 cookie-based 認證

## 環境變數更新

### `.env.example`

```env
# Google OAuth (Client-side)
# Used by browser-side Google Identity Services for OAuth login
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

**說明**:
- **`NEXT_PUBLIC_GOOGLE_CLIENT_ID`**: 瀏覽器端 OAuth 使用（必需）
- 不再需要 `GOOGLE_CLIENT_SECRET`（因為不使用 server-side OAuth）

## Cookie 設定

後端 (`apps/backend/app/config.py`) 的 cookie 設定：

```python
COOKIE_SAMESITE = "lax"      # 開發環境使用 lax
COOKIE_SECURE = False        # 開發環境 HTTP 使用 false
COOKIE_HTTPONLY = True       # 永遠是 true (安全性)
COOKIE_DOMAIN = None         # None 表示 same-origin
```

**重要**: 
- 開發環境 (`localhost`) 必須使用 `COOKIE_SECURE=false`
- 生產環境 (HTTPS) 應使用 `COOKIE_SECURE=true`
- `COOKIE_SAMESITE=lax` 允許 GET 導向時帶 cookie

## 測試步驟

### 1. 測試 Google 登入

```bash
# 啟動後端
cd apps/backend
poetry run uvicorn app.main:app --reload

# 啟動前端
cd apps/web
npm run dev
```

訪問 http://localhost:3000/login，點擊「使用 Google 登入」：

1. 應該看到 Google One Tap 提示
2. 選擇 Google 帳號後，應該自動登入並重定向到 /posts
3. 開啟瀏覽器 DevTools → Application → Cookies → http://localhost:3000
   - 應該看到 `access_token` cookie
   - 應該看到 `refresh_token` cookie
   - 兩個 cookies 都應該標記為 `HttpOnly`

### 2. 測試受保護路由

未登入狀態訪問 http://localhost:3000/posts → 應該被重定向到 `/login`

### 3. 測試 API 呼叫

登入後，開啟 DevTools → Network：
- 所有 API 請求 (如 `/api/v1/posts`) 的 Request Headers 中應該包含 Cookie
- 應該不會看到 401 錯誤

### 4. 測試登出

訪問 http://localhost:3000/me/gallery，點擊「登出」：
- 應該清除 cookies
- 應該重定向到 `/login`

### 5. 測試認證頁面

訪問 http://localhost:3000/auth-test：
- 顯示認證狀態
- 顯示使用者資訊（從後端 API 取得）
- 可測試登入/登出功能

## 完成的清理

1. **已移除 NextAuth 相關內容**: 
   - ✅ 移除 `next-auth` 套件（從 package.json）
   - ✅ 刪除 `/api/auth` 路由
   - ✅ 刪除 `lib/auth/` 目錄（config.ts, utils.ts, types.ts, index.ts）
   - ✅ 更新環境變數（移除 NextAuth 相關變數）

## 後續優化建議

1. **改善錯誤處理**:
   - 在 `google-oauth.ts` 加入更詳細的錯誤訊息
   - 處理 token 過期的情況
   - 加入 refresh token 自動續期邏輯

2. **改善 UX**:
   - 在登入按鈕加入 loading 狀態
   - 改善 Google One Tap 的顯示方式
   - 加入「記住我」功能

3. **安全性增強**:
   - 生產環境啟用 `COOKIE_SECURE=true`
   - 考慮使用 `COOKIE_SAMESITE=strict`
   - 加入 CSRF protection

## 參考文件

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web)
- [HTTP Cookies (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [Next.js 16 Proxy](https://nextjs.org/docs/app/building-your-application/routing/middleware)
