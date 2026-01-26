# HttpOnly Cookie 認證實作驗證指南

本文檔說明如何驗證 HttpOnly Cookie 認證機制的實作。

## 實作摘要

### 後端變更

#### 1. 登入端點設置 HttpOnly Cookies
- **檔案**: `apps/backend/app/modules/identity/presentation/routers/auth_router.py`
- **變更端點**:
  - `POST /auth/admin-login` - 管理員登入
  - `POST /auth/google-login` - Google OAuth 登入
  - `POST /auth/google-callback` - Google OAuth callback
- **行為**: 登入成功後，設置兩個 httpOnly cookies:
  - `access_token`: 短效 token (預設 15 分鐘)
  - `refresh_token`: 長效 token (預設 7 天)
- **Cookie 屬性**:
  - `httponly=true` - 防止 JavaScript 存取
  - `secure=true` (production) - 僅 HTTPS
  - `samesite=lax` - CSRF 保護
  - `path=/` - 全域可用

#### 2. 新增登出端點
- **檔案**: `apps/backend/app/modules/identity/presentation/routers/auth_router.py`
- **端點**: `POST /auth/logout`
- **行為**: 設置 `max-age=0` 清除兩個 cookies

#### 3. 認證中介層支援 Cookie
- **檔案**: `apps/backend/app/shared/presentation/dependencies/auth.py`
- **變更**: `get_current_user_id()` 和 `get_optional_current_user_id()`
- **優先順序**:
  1. 優先從 `access_token` cookie 讀取 token
  2. 後備從 `Authorization: Bearer` header 讀取 (向後相容)

### 前端變更

#### 1. 移除 localStorage 操作
- **檔案**: `apps/web/src/app/(auth)/login/page.tsx`
- **變更**: 移除 `localStorage.setItem()` 呼叫
- **行為**: 依賴後端自動設置的 httpOnly cookies

#### 2. Axios 配置已就緒
- **檔案**: `apps/web/src/lib/api/axios.ts`
- **配置**: `withCredentials: true` (已存在)
- **行為**: 自動在請求中帶上 cookies

## 驗證方法

### 方法 1: 手動測試腳本

使用提供的 Python 測試腳本：

```bash
cd apps/backend

# 1. 確保後端服務執行中
# docker compose up -d  # 或
# poetry run uvicorn app.main:app --reload

# 2. 執行測試腳本
python3 test_httponly_manual.py
```

測試腳本會驗證：
- ✓ 登入設置 cookies
- ✓ 使用 cookie 進行認證請求
- ✓ Token refresh 更新 cookies
- ✓ 登出清除 cookies
- ✓ 登出後請求被拒絕

### 方法 2: 瀏覽器開發者工具

1. 啟動前端和後端服務
2. 開啟瀏覽器開發者工具 (F12)
3. 前往 Network 標籤
4. 訪問登入頁面並登入
5. 檢查 `/auth/admin-login` 的 Response Headers:
   ```
   set-cookie: access_token=...; HttpOnly; Path=/; SameSite=lax
   set-cookie: refresh_token=...; HttpOnly; Path=/; SameSite=lax
   ```
6. 前往 Application > Cookies 查看已設置的 cookies
7. 確認 `HttpOnly` 欄位為 ✓

### 方法 3: cURL 測試

```bash
# 1. 登入並儲存 cookies
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kcardswap.com","password":"admin123456"}'

# 2. 查看 cookies
cat cookies.txt

# 3. 使用 cookies 進行認證請求
curl -b cookies.txt http://localhost:8000/api/v1/profile/me

# 4. Refresh tokens
curl -b cookies.txt -c cookies.txt \
  -X POST http://localhost:8000/api/v1/auth/refresh

# 5. 登出
curl -b cookies.txt -X POST http://localhost:8000/api/v1/auth/logout
```

## 安全檢查清單

驗證以下安全措施已實作：

- [ ] ✅ Cookies 設置 `HttpOnly=true`
- [ ] ✅ Production 環境 `Secure=true` (需在 HTTPS)
- [ ] ✅ 設置 `SameSite=lax` 防止 CSRF
- [ ] ✅ 後端 CORS 設定 `allow_credentials=true`
- [ ] ✅ 前端 axios 設定 `withCredentials: true`
- [ ] ✅ 前端不使用 localStorage 存儲 tokens
- [ ] ✅ 認證中介層優先使用 cookie
- [ ] ✅ 登出端點清除 cookies
- [ ] ✅ Refresh 端點 rotation tokens

## 環境變數配置

確認以下環境變數設置正確 (apps/backend/.env):

```bash
# Cookie 配置
ACCESS_COOKIE_NAME=access_token
REFRESH_COOKIE_NAME=refresh_token
COOKIE_SAMESITE=lax          # lax | strict | none
COOKIE_SECURE=false          # true for production (HTTPS)
COOKIE_HTTPONLY=true         # 強制 true
COOKIE_DOMAIN=               # 留空表示同源
COOKIE_PATH=/

# Token 過期時間
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (必須包含前端網域)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 向後相容性

實作保持向後相容：
- ✅ 登入端點仍在 response body 回傳 tokens (用於舊客戶端)
- ✅ 認證中介層仍支援 `Authorization: Bearer` header
- ✅ Mobile app 可繼續使用 Bearer token 方式

## 已知限制

1. **Mobile App (Expo)**: HttpOnly cookies 在 WebView 中可能不適用，mobile 應繼續使用 Bearer token
2. **跨域**: 如果前後端不同網域，需要正確設置 `COOKIE_DOMAIN` 和 `CORS_ORIGINS`
3. **HTTPS**: Production 必須使用 HTTPS，否則 `Secure` cookies 無法運作

## 測試覆蓋

現有測試已驗證：
- ✅ `tests/integration/modules/identity/test_auth_refresh_cookie.py` - Cookie refresh 流程
- ⚠️ 登入端點測試需要更新來驗證 cookie 設置

建議新增測試：
- [ ] 驗證登入端點設置正確的 cookie 屬性
- [ ] 驗證登出端點清除 cookies
- [ ] 驗證認證中介層優先使用 cookie

## 故障排除

### 問題: Cookie 未被設置
- 檢查 CORS 配置是否允許 credentials
- 檢查前端是否設置 `withCredentials: true`
- 檢查後端是否正確呼叫 `response.set_cookie()`

### 問題: Cookie 未被送出
- 檢查前端 axios 配置 `withCredentials: true`
- 檢查 SDK 配置 `WITH_CREDENTIALS: true`
- 檢查瀏覽器是否阻擋第三方 cookies

### 問題: 401 Unauthorized
- 檢查 cookie 是否過期
- 檢查認證中介層是否正確讀取 cookie
- 檢查 `ACCESS_COOKIE_NAME` 配置是否一致

### 問題: CORS 錯誤
- 確認 `CORS_ORIGINS` 包含前端網域
- 確認 `allow_credentials=True` 已設置
- 確認不能使用 `CORS_ORIGINS=*` 搭配 credentials

## 參考資源

- [OWASP: HttpOnly Cookie](https://owasp.org/www-community/HttpOnly)
- [MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)
- [FastAPI: Response Cookies](https://fastapi.tiangolo.com/advanced/response-cookies/)
- [Axios: withCredentials](https://axios-http.com/docs/req_config)
