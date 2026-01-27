# Google OAuth Authorization Code Flow 實作

## 概述

本次更新將 Google 登入從 **ID Token Flow**（使用 Google Identity Services 按鈕）改為 **Authorization Code Flow**（使用自訂按鈕），以支援完全自訂的 UI 樣式。

## 變更內容

### 後端變更

1. **新增 Use Case**：`GoogleCodeLoginUseCase`
   - 路徑：`apps/backend/app/modules/identity/application/use_cases/auth/login_with_google_code.py`
   - 功能：處理 authorization code 的交換與驗證

2. **新增 API Endpoint**：`POST /api/v1/auth/google-login-code`
   - 接收前端的 authorization code
   - 與 Google OAuth 交換 ID token
   - 驗證 token 並建立/取得使用者
   - 設定 httpOnly cookies（access_token、refresh_token）

3. **更新 Schema**：新增 `GoogleCodeLoginRequest`
   ```python
   {
       "code": str,  # Google authorization code
       "redirect_uri": Optional[str]  # 可選的 redirect URI
   }
   ```

4. **IoC Container**：註冊新的 use case 到依賴注入容器

### 前端變更

1. **安裝套件**：`@react-oauth/google`
   ```bash
   npm install @react-oauth/google
   ```

2. **更新登入頁面**：`apps/web/src/app/(auth)/login/page.tsx`
   - 移除舊的 Google Identity Services 按鈕
   - 使用 `GoogleOAuthProvider` 和 `useGoogleLogin` hook
   - 實作自訂滿版粉色按鈕
   - 使用 `flow: 'auth-code'` 獲取 authorization code
   - 呼叫新的後端 API endpoint

3. **按鈕樣式**：
   - 滿版寬度（100% width）
   - 粉色漸層背景（from-secondary-500 to-rose-400）
   - Google Logo + 文字
   - Loading 狀態

## 環境變數設定

### 後端 (.env)

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000  # Web app origin
```

**注意**：`GOOGLE_REDIRECT_URI` 現在應設定為前端的 origin（如 `http://localhost:3000`），而非後端的 callback URL。

### 前端 (.env.local)

```bash
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Google Cloud Console 設定

1. 前往 [Google Cloud Console](https://console.cloud.google.com)
2. 選擇你的專案
3. 進入「APIs & Services」→「Credentials」
4. 編輯 OAuth 2.0 Client ID
5. 在「Authorized redirect URIs」中新增：
   - `http://localhost:3000`（開發環境）
   - `https://yourdomain.com`（生產環境）

## 使用方式

### 開發環境測試

1. **啟動後端**：
   ```bash
   cd apps/backend
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **啟動前端**：
   ```bash
   cd apps/web
   npm run dev
   ```

3. **訪問登入頁面**：
   - 前往 http://localhost:3000/login
   - 點擊「使用 Google 登入」按鈕
   - 選擇 Google 帳號並授權
   - 成功登入後會重定向到 `/posts`

### 測試頁面

你也可以使用根目錄的 `test-google-oauth-code-flow.html` 來測試：

1. 編輯檔案中的 `GOOGLE_CLIENT_ID`
2. 使用本地伺服器開啟（如 `python -m http.server 3000`）
3. 訪問 http://localhost:3000/test-google-oauth-code-flow.html

## 流程說明

### Authorization Code Flow

```
1. 使用者點擊「使用 Google 登入」
   ↓
2. 前端重定向到 Google OAuth 授權頁面
   URL: https://accounts.google.com/o/oauth2/v2/auth
   參數: client_id, redirect_uri, response_type=code, scope
   ↓
3. 使用者選擇 Google 帳號並授權
   ↓
4. Google 重定向回前端，帶上 authorization code
   URL: http://localhost:3000?code=AUTHORIZATION_CODE
   ↓
5. 前端呼叫後端 API，傳送 code
   POST /api/v1/auth/google-login-code
   Body: { code, redirect_uri }
   ↓
6. 後端用 code + client_secret 向 Google 交換 ID token
   POST https://oauth2.googleapis.com/token
   ↓
7. 後端驗證 ID token，建立/取得使用者
   ↓
8. 後端設定 httpOnly cookies (access_token, refresh_token)
   ↓
9. 前端重定向到 /posts
```

## 與原有流程的差異

### 原有流程（ID Token Flow）

- 使用 Google Identity Services 提供的按鈕
- 前端直接取得 ID token
- 按鈕樣式受限（寬度 200-400px）
- 無法完全自訂 UI

### 新流程（Authorization Code Flow）

- 使用自訂按鈕，完全控制 UI
- 前端取得 authorization code
- 後端負責與 Google 交換 token
- 支援滿版、粉色等自訂樣式

## API 文件

### POST /api/v1/auth/google-login-code

**Request Body:**
```json
{
  "code": "4/0AVG7fiQ...",  // Google authorization code
  "redirect_uri": "http://localhost:3000"  // 可選
}
```

**Response (Success - 200):**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  },
  "meta": null,
  "error": null
}
```

**Response (Error - 401):**
```json
{
  "detail": {
    "code": "UNAUTHORIZED",
    "message": "Invalid authorization code. Token exchange failed."
  }
}
```

## 安全性考量

1. **Authorization Code + Client Secret**：
   - Authorization code 只能使用一次
   - 交換 token 需要 client_secret，只有後端知道
   - 防止 code 被攔截後濫用

2. **HttpOnly Cookies**：
   - Access token 和 refresh token 儲存在 httpOnly cookies
   - JavaScript 無法存取，防止 XSS 攻擊
   - Cookies 設定 SameSite=Lax，防止 CSRF

3. **Redirect URI 驗證**：
   - Google 會驗證 redirect_uri 是否在白名單中
   - 防止 authorization code 被導向惡意網站

## 故障排除

### 問題：「Invalid authorization code」

**可能原因**：
1. Code 已使用過（只能使用一次）
2. Code 已過期（通常 10 分鐘）
3. Redirect URI 不匹配

**解決方法**：
1. 確認 Google Cloud Console 的 redirect URIs 設定正確
2. 確認前端和後端使用相同的 redirect_uri
3. 重新嘗試登入

### 問題：「CORS error」

**可能原因**：
後端 CORS 設定未包含前端 origin

**解決方法**：
在後端 `.env` 中設定：
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 問題：按鈕沒有反應

**可能原因**：
1. Google Client ID 未設定
2. 瀏覽器阻擋彈出視窗

**解決方法**：
1. 檢查 `NEXT_PUBLIC_GOOGLE_CLIENT_ID` 環境變數
2. 允許瀏覽器彈出視窗
3. 查看瀏覽器 console 的錯誤訊息

## 相關檔案

### 後端
- `apps/backend/app/modules/identity/application/use_cases/auth/login_with_google_code.py`
- `apps/backend/app/modules/identity/presentation/routers/auth_router.py`
- `apps/backend/app/modules/identity/presentation/schemas/auth_schemas.py`
- `apps/backend/app/modules/identity/module.py`

### 前端
- `apps/web/src/app/(auth)/login/page.tsx`
- `apps/web/package.json`

### 文件
- `openapi/openapi.json` - 更新的 API 規格
- `test-google-oauth-code-flow.html` - 測試頁面
- `.env.example` - 環境變數範例

## 後續改進

1. **錯誤處理**：增強前端錯誤訊息顯示
2. **載入狀態**：改進載入動畫
3. **測試**：新增 E2E 測試
4. **多語言**：支援英文 UI
5. **Mobile**：確保在 Mobile Web 上也能正常運作
