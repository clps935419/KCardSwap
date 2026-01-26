# HttpOnly Cookie 認證實作 - 完成報告

## 專案資訊
- **PR**: copilot/handle-httponly-cookies
- **日期**: 2026-01-26
- **狀態**: ✅ 實作完成，待人工測試驗證

## 問題背景

用戶報告前後端沒有正確實作 HttpOnly Cookie 認證機制，存在以下問題：

1. 前端將 tokens 存儲在 localStorage，易受 XSS 攻擊
2. 後端登入端點只在 response body 回傳 tokens
3. 認證中介層只支援 Bearer token，未檢查 cookie
4. 缺少登出端點來清除 cookies

## 實作內容

### 後端變更

#### 1. 登入端點設置 HttpOnly Cookies
**檔案**: `apps/backend/app/modules/identity/presentation/routers/auth_router.py`

修改三個登入端點：
- `POST /api/v1/auth/admin-login`
- `POST /api/v1/auth/google-login`
- `POST /api/v1/auth/google-callback`

**變更內容**：
```python
# 登入成功後設置兩個 httpOnly cookies
response.set_cookie(
    key=settings.ACCESS_COOKIE_NAME,
    value=access_token,
    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    httponly=settings.COOKIE_HTTPONLY,  # True
    samesite=settings.COOKIE_SAMESITE,  # "lax"
    secure=settings.COOKIE_SECURE,      # True for production
    domain=settings.COOKIE_DOMAIN,      # None for same-origin
    path=settings.COOKIE_PATH,          # "/"
)

response.set_cookie(
    key=settings.REFRESH_COOKIE_NAME,
    value=refresh_token,
    max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    httponly=settings.COOKIE_HTTPONLY,
    samesite=settings.COOKIE_SAMESITE,
    secure=settings.COOKIE_SECURE,
    domain=settings.COOKIE_DOMAIN,
    path=settings.COOKIE_PATH,
)
```

**安全特性**：
- ✅ `HttpOnly=true`: JavaScript 無法存取，防止 XSS
- ✅ `SameSite=lax`: 防止 CSRF 攻擊
- ✅ `Secure=true` (production): 僅在 HTTPS 傳輸
- ✅ `Path=/`: 所有路徑可用
- ✅ `Domain`: 可配置，預設同源

#### 2. 新增登出端點
**檔案**: `apps/backend/app/modules/identity/presentation/routers/auth_router.py`

```python
@router.post("/logout")
async def logout(response: Response) -> RefreshSuccessResponse:
    # 清除兩個 cookies (設置 max-age=0)
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value="",
        max_age=0,
        ...
    )
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value="",
        max_age=0,
        ...
    )
```

#### 3. 認證中介層優先使用 Cookie
**檔案**: `apps/backend/app/shared/presentation/dependencies/auth.py`

**修改前**：
```python
# 只支援 Bearer token
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    ...
) -> UUID:
    token = credentials.credentials
```

**修改後**：
```python
# 優先使用 cookie，後備 Bearer token
async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token_cookie: Optional[str] = Cookie(None, alias=settings.ACCESS_COOKIE_NAME),
    ...
) -> UUID:
    # Priority 1: Check httpOnly cookie first
    token = access_token_cookie
    
    # Priority 2: Fallback to Bearer token (backward compatibility)
    if not token and credentials:
        token = credentials.credentials
```

**設計考量**：
- 使用 `HTTPBearer(auto_error=False)` 允許 cookie-first 檢查
- 保留 Bearer token 支援以維持向後相容
- Mobile app 可繼續使用 Bearer token

#### 4. 配置檔案
**檔案**: `apps/backend/app/config.py`

已存在完整的 cookie 配置（第 33-42 行）：
```python
# Cookie-JWT Settings
ACCESS_COOKIE_NAME: str = "access_token"
REFRESH_COOKIE_NAME: str = "refresh_token"
COOKIE_SAMESITE: str = "lax"
COOKIE_SECURE: bool = False  # true for production
COOKIE_HTTPONLY: bool = True  # Always true
COOKIE_DOMAIN: str | None = None
COOKIE_PATH: str = "/"
```

### 前端變更

#### 1. 移除 localStorage 操作
**檔案**: `apps/web/src/app/(auth)/login/page.tsx`

**修改前**：
```typescript
// Store tokens in localStorage
localStorage.setItem('access_token', response.data.access_token)
localStorage.setItem('refresh_token', response.data.refresh_token)
```

**修改後**：
```typescript
// Tokens are now stored in httpOnly cookies automatically
// No need to manually store them in localStorage
if (response.data) {
  // Redirect to posts feed after login
  window.location.href = '/posts'
}
```

#### 2. Axios 配置驗證
**檔案**: `apps/web/src/lib/api/axios.ts`

已正確配置（無需修改）：
```typescript
export const apiClient: AxiosInstance = axios.create({
  baseURL,
  withCredentials: true,  // ✓ Enable cookies for cross-origin requests
  headers: {
    'Content-Type': 'application/json',
  },
})
```

#### 3. SDK 配置驗證
**檔案**: `apps/web/src/shared/api/sdk-config.ts`

已正確配置（無需修改）：
```typescript
OpenAPI.WITH_CREDENTIALS = true
OpenAPI.CREDENTIALS = 'include'
```

### CORS 配置

#### 1. 後端 CORS 設置
**檔案**: `apps/backend/app/main.py`

已正確配置（無需修改）：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,  # ✓ Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. 環境變數範例更新
更新 `.env.example` 和 `apps/backend/.env.example`：

```bash
# Development: Allow localhost ports
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:19006

# Cookie settings
ACCESS_COOKIE_NAME=access_token
REFRESH_COOKIE_NAME=refresh_token
COOKIE_SAMESITE=lax
COOKIE_SECURE=false  # true for production
COOKIE_DOMAIN=
```

## 安全檢查結果

### 1. Code Review
✅ **通過** - 已處理所有建議：
- 統一使用 `Optional[str]` 類型註解
- 為 `auto_error=False` 添加說明

### 2. CodeQL Security Scan
✅ **通過** - 0 alerts found
- Python: No alerts
- JavaScript: No alerts

## 測試工具

### 1. 手動測試腳本
**檔案**: `apps/backend/test_httponly_manual.py`

提供自動化測試腳本，驗證：
- ✓ 登入設置 cookies
- ✓ 使用 cookie 進行認證請求
- ✓ Token refresh 更新 cookies
- ✓ 登出清除 cookies
- ✓ 登出後請求被拒絕

**使用方法**：
```bash
cd apps/backend
python3 test_httponly_manual.py
```

### 2. 驗證文檔
**檔案**: `docs/HTTPONLY_COOKIE_VERIFICATION.md`

完整的驗證指南，包含：
- 實作摘要
- 三種驗證方法（腳本、瀏覽器、cURL）
- 安全檢查清單
- 環境變數配置
- 故障排除指南

## 向後相容性

✅ **完全向後相容**：

1. **登入端點**：仍在 response body 回傳 tokens
   ```json
   {
     "data": {
       "access_token": "...",
       "refresh_token": "...",
       ...
     }
   }
   ```
   舊客戶端可以繼續使用 response body 中的 tokens

2. **認證中介層**：仍支援 Bearer token
   ```
   Authorization: Bearer <token>
   ```
   Mobile app 可以繼續使用 Bearer token 方式

3. **既有測試**：refresh endpoint 的測試已驗證 cookie 功能
   - `tests/integration/modules/identity/test_auth_refresh_cookie.py`

## 業界最佳實務符合度

✅ **完全符合 OWASP 和業界標準**：

### 1. Token 存儲
- ✅ 使用 HttpOnly cookies（不是 localStorage）
- ✅ 分離 access token 和 refresh token

### 2. Cookie 安全屬性
- ✅ `HttpOnly=true` - 防止 XSS
- ✅ `Secure=true` (production) - 僅 HTTPS
- ✅ `SameSite=lax` - 防止 CSRF
- ✅ 適當的 `max-age` 設定

### 3. CORS 配置
- ✅ `allow_credentials=true`
- ✅ 明確列出允許的 origins（不使用 `*`）

### 4. Token Rotation
- ✅ Refresh 端點實作 token rotation
- ✅ 舊 refresh token 被撤銷

### 5. 前端安全
- ✅ `withCredentials: true`
- ✅ 不使用 localStorage 存儲敏感資料

## 待辦事項

### 開發者測試（需人工執行）
- [ ] 啟動 backend 和 web 服務
- [ ] 執行測試腳本：`python3 apps/backend/test_httponly_manual.py`
- [ ] 使用瀏覽器開發者工具驗證 cookie 屬性
- [ ] 測試完整流程：登入 → 請求 → refresh → 登出

### 未來改進（可選）
- [ ] 新增整合測試驗證登入端點設置 cookie
- [ ] 考慮實作 CSRF token（如果需要跨域 `SameSite=none`）
- [ ] 監控 cookie size（避免超過瀏覽器限制）
- [ ] 考慮實作 remember me 功能（可選）

## 參考文件

### 內部文件
1. `docs/HTTPONLY_COOKIE_VERIFICATION.md` - 驗證指南
2. `apps/backend/test_httponly_manual.py` - 測試腳本
3. `apps/backend/README.md` - 後端開發指南
4. `apps/backend/app/config.py` - 配置說明

### 外部參考
1. [OWASP: HttpOnly Cookie](https://owasp.org/www-community/HttpOnly)
2. [MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)
3. [FastAPI: Response Cookies](https://fastapi.tiangolo.com/advanced/response-cookies/)
4. [Axios: withCredentials](https://axios-http.com/docs/req_config)

## 結論

✅ **實作完成**

本次實作完整實現了 HttpOnly Cookie 認證機制，符合業界最佳實務和 OWASP 安全標準。主要成果：

1. **安全性提升**：使用 HttpOnly cookies 防止 XSS 攻擊
2. **完整實作**：登入、refresh、登出端點全部支援 cookie
3. **向後相容**：保留 Bearer token 支援，不影響現有客戶端
4. **完善文檔**：提供測試腳本和驗證指南
5. **通過檢查**：Code review 和 CodeQL 安全掃描全部通過

建議在合併前進行人工測試驗證，確保在實際環境中運作正常。

---

**生成時間**: 2026-01-26  
**PR Branch**: copilot/handle-httponly-cookies  
**相關 Issue**: HttpOnly Cookie 認證實作
