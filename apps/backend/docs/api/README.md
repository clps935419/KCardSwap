# KCardSwap API Documentation

**Version**: 1.0.0  
**Last Updated**: 2026-01-02

## Overview

KCardSwap 提供 RESTful API 供行動端與第三方應用程式使用。所有 API 端點均遵循統一的回應格式規範。

## Base URL

```
開發環境: http://localhost:8000/api/v1
生產環境: https://api.kcardswap.com/api/v1
```

## 統一回應格式

### 基本結構

所有 API 回應使用以下 envelope 結構：

```json
{
  "data": <response_data> | null,
  "meta": <metadata> | null,
  "error": <error_object> | null
}
```

### 欄位說明

- **`data`**: 成功時包含實際回應資料，失敗時為 `null`
- **`meta`**: 包含元資料（如分頁資訊），非分頁回應時為 `null`
- **`error`**: 包含錯誤資訊，成功時為 `null`

## 成功回應範例

### 單一資源

```json
{
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "nickname": "CardMaster"
  },
  "meta": null,
  "error": null
}
```

**範例端點**:
- `GET /api/v1/profile/me`
- `POST /api/v1/auth/google-login`
- `PUT /api/v1/profile/me`

### 列表資源（無分頁）

```json
{
  "data": [
    {"id": "uuid-1", "name": "Item 1"},
    {"id": "uuid-2", "name": "Item 2"}
  ],
  "meta": null,
  "error": null
}
```

**範例端點**:
- `GET /api/v1/locations/cities`
- `GET /api/v1/friends`

### 分頁列表資源

```json
{
  "data": [
    {"id": "uuid-1", "title": "Item 1"},
    {"id": "uuid-2", "title": "Item 2"}
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "error": null
}
```

**範例端點**:
- `GET /api/v1/cards/me?page=1&page_size=20`
- `GET /api/v1/posts?page=1&page_size=20`
- `GET /api/v1/chats/{id}/messages?page=1&page_size=50`

## 錯誤回應範例

### 標準錯誤格式

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "404_NOT_FOUND",
    "message": "Resource not found",
    "details": {}
  }
}
```

### 常見錯誤碼

| HTTP Status | Error Code | 說明 |
|------------|------------|------|
| 400 | `400_VALIDATION_FAILED` | 請求參數驗證失敗 |
| 401 | `401_UNAUTHORIZED` | 未登入或 token 無效 |
| 403 | `403_FORBIDDEN` | 無權限存取資源 |
| 404 | `404_NOT_FOUND` | 資源不存在 |
| 409 | `409_CONFLICT` | 資源衝突（如重複建立） |
| 422 | `422_LIMIT_EXCEEDED` | 超過使用限制（配額） |
| 429 | `429_RATE_LIMITED` | 請求頻率過高 |
| 500 | `500_INTERNAL_ERROR` | 伺服器內部錯誤 |

### 驗證錯誤範例

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "400_VALIDATION_FAILED",
    "message": "Validation failed",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

### 配額超限範例

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "422_LIMIT_EXCEEDED",
    "message": "Daily upload limit exceeded",
    "details": {
      "limit_type": "daily_uploads",
      "current": 2,
      "max": 2
    }
  }
}
```

## 認證

### JWT Token

大部分 API 端點需要 JWT 認證。請在請求 header 中包含：

```http
Authorization: Bearer <access_token>
```

### Token 取得

1. **Google OAuth 登入** (推薦):
   ```http
   POST /api/v1/auth/google-callback
   Content-Type: application/json
   
   {
     "code": "google_authorization_code",
     "code_verifier": "pkce_code_verifier"
   }
   ```

2. **管理員登入** (僅供後台):
   ```http
   POST /api/v1/auth/admin-login
   Content-Type: application/json
   
   {
     "email": "admin@example.com",
     "password": "secure_password"
   }
   ```

### Token Refresh

當 access token 過期時，使用 refresh token 取得新的 access token：

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

## 分頁參數

支援分頁的端點接受以下查詢參數：

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `page` | integer | 1 | 頁碼（從 1 開始） |
| `page_size` | integer | 20 | 每頁資料筆數 |

**範例**:
```http
GET /api/v1/cards/me?page=2&page_size=50
```

## API 模組

### Identity Module

身份驗證與個人檔案管理

- [Identity Module API Documentation](./identity-module.md)

**端點列表**:
- 認證: `/auth/*`
- 個人檔案: `/profile/*`
- 訂閱: `/subscriptions/*`

### Social Module - Cards

小卡管理與上傳

- [Social Module - Cards Documentation](./social-module-cards.md)

**端點列表**:
- 卡片上傳: `/cards/upload-url`
- 我的卡冊: `/cards/me`
- 配額狀態: `/cards/quota/status`

### Social Module - Nearby

附近小卡搜尋

**端點列表**:
- 搜尋附近: `/nearby/search`
- 更新位置: `/nearby/location`

### Social Module - Friends

好友系統

**端點列表**:
- 送出邀請: `/friends/request`
- 接受邀請: `/friends/{id}/accept`
- 封鎖用戶: `/friends/block`
- 解除封鎖: `/friends/unblock`
- 好友列表: `/friends`

### Social Module - Chat

聊天室與訊息

**端點列表**:
- 聊天室列表: `/chats`
- 訊息歷史: `/chats/{id}/messages`
- 發送訊息: `/chats/{id}/messages`

### Social Module - Trade

小卡交換

**端點列表**:
- 建立提案: `/trades`
- 接受交換: `/trades/{id}/accept`
- 拒絕交換: `/trades/{id}/reject`
- 取消交換: `/trades/{id}/cancel`
- 完成交換: `/trades/{id}/complete`
- 交換歷史: `/trades/history`

### Social Module - Rating

用戶評分

**端點列表**:
- 評分: `/ratings`
- 用戶評分: `/ratings/user/{user_id}`
- 平均評分: `/ratings/user/{user_id}/average`

### Social Module - Report

檢舉系統

**端點列表**:
- 提交檢舉: `/reports`
- 檢舉列表: `/reports`

### Posts Module

城市看板貼文

**端點列表**:
- 建立貼文: `/posts`
- 看板列表: `/posts`
- 貼文詳情: `/posts/{id}`
- 表達興趣: `/posts/{id}/interest`
- 接受興趣: `/posts/{id}/interests/{interest_id}/accept`
- 拒絕興趣: `/posts/{id}/interests/{interest_id}/reject`
- 關閉貼文: `/posts/{id}/close`
- 興趣列表: `/posts/{id}/interests`

### Locations Module

地點與城市資訊

**端點列表**:
- 城市列表: `/locations/cities` (無需認證)

## 開發工具

### Swagger UI

啟動開發伺服器後，可透過瀏覽器存取互動式 API 文件：

```
http://localhost:8000/docs
```

### ReDoc

另一種 API 文件檢視方式：

```
http://localhost:8000/redoc
```

### OpenAPI Specification

取得 OpenAPI 3.0 規格檔案：

```
http://localhost:8000/openapi.json
```

或使用專案中的 snapshot：

```
/openapi/openapi.json
```

## 速率限制

### 免費用戶

- 每日上傳: 2 張卡片
- 每日搜尋: 5 次
- 每日發文: 2 則
- 總儲存空間: 1 GB
- 單檔大小: 10 MB

### 付費用戶 (Premium)

- 無限上傳
- 無限搜尋
- 無限發文
- 總儲存空間: 10 GB
- 單檔大小: 20 MB

## 最佳實務

### 1. 使用正確的 HTTP 方法

- `GET`: 讀取資源
- `POST`: 建立資源或執行操作
- `PUT`: 更新整個資源
- `PATCH`: 部分更新資源
- `DELETE`: 刪除資源

### 2. 錯誤處理

始終檢查回應中的 `error` 欄位：

```typescript
const response = await api.get('/api/v1/profile/me');

if (response.error) {
  // 處理錯誤
  console.error(response.error.code, response.error.message);
  return;
}

// 使用資料
const profile = response.data;
```

### 3. 分頁處理

對於大量資料，使用分頁參數：

```typescript
const response = await api.get('/api/v1/cards/me', {
  params: { page: 1, page_size: 20 }
});

if (response.data && response.meta) {
  console.log(`Total: ${response.meta.total}`);
  console.log(`Pages: ${response.meta.total_pages}`);
  // 處理資料
  response.data.forEach(card => {
    // ...
  });
}
```

### 4. Token 管理

- 儲存 access token 與 refresh token 於安全位置
- access token 過期時自動使用 refresh token 更新
- refresh token 過期時導向使用者重新登入

## 支援

如有任何問題或建議，請：

1. 查閱完整文件: `apps/backend/docs/`
2. 檢視 OpenAPI 規格: `openapi/openapi.json`
3. 建立 GitHub Issue

## 變更紀錄

### 2026-01-02 - v1.0.0

- ✅ 實作統一 envelope 回應格式
- ✅ 標準化所有 45 個 API 端點
- ✅ 更新錯誤處理機制
- ✅ 新增分頁支援
- ✅ 完整的 OpenAPI 3.0 規格

## 相關文件

- [Response Format Specification](../../specs/001-kcardswap-complete-spec/response-format.md)
- [Authentication Guide](../authentication.md)
- [Database Architecture](../database-architecture.md)
- [OpenAPI README](../../openapi/README.md)
