# API Response Format Specification

**版本**: 1.0.0  
**最後更新**: 2026-01-02  
**狀態**: Active

## 概述

本文件定義 KCardSwap API 的統一回應格式規範。所有 API 端點必須遵循此格式，確保前後端介接的一致性與可預測性。

## 基本結構

所有 API 回應必須使用以下 envelope 結構：

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

## 成功回應格式

### 1. 單一資源回應

```json
{
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "nickname": "CardMaster",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "meta": null,
  "error": null
}
```

**使用場景**:
- GET /api/v1/profile/me
- POST /api/v1/auth/google-login
- PUT /api/v1/profile/me

### 2. 列表回應（無分頁）

```json
{
  "data": [
    {
      "id": "uuid-1",
      "name": "Item 1"
    },
    {
      "id": "uuid-2",
      "name": "Item 2"
    }
  ],
  "meta": null,
  "error": null
}
```

**使用場景**:
- GET /api/v1/locations/cities
- GET /api/v1/friends (小量資料，不需分頁)

### 3. 分頁列表回應

```json
{
  "data": [
    {
      "id": "uuid-1",
      "title": "Item 1"
    },
    {
      "id": "uuid-2",
      "title": "Item 2"
    }
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

**使用場景**:
- GET /api/v1/cards/me
- GET /api/v1/posts
- GET /api/v1/trades/history
- GET /api/v1/chats/{id}/messages

**Meta 欄位說明**:
- `total`: 總筆數
- `page`: 當前頁碼（從 1 開始）
- `page_size`: 每頁筆數
- `total_pages`: 總頁數

### 4. 操作成功回應（無資料）

```json
{
  "data": {
    "success": true,
    "message": "Operation completed successfully"
  },
  "meta": null,
  "error": null
}
```

**使用場景**:
- DELETE /api/v1/cards/{id}
- POST /api/v1/posts/{id}/close
- POST /api/v1/friends/block

## 錯誤回應格式

### 錯誤結構

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### 錯誤欄位說明

- **`code`**: 錯誤代碼（字串，格式：`{HTTP_STATUS}_{ERROR_TYPE}`）
- **`message`**: 使用者友善的錯誤訊息（中文或英文，由 Accept-Language 決定）
- **`details`**: 額外的錯誤細節（物件，可選）

### 常見錯誤範例

#### 1. 驗證失敗 (400)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "400_VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "email",
          "message": "Invalid email format",
          "type": "value_error.email"
        }
      ]
    }
  }
}
```

#### 2. 未授權 (401)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "401_UNAUTHORIZED",
    "message": "Authentication required",
    "details": {}
  }
}
```

#### 3. 權限不足 (403)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "403_FORBIDDEN",
    "message": "You don't have permission to access this resource",
    "details": {
      "required_role": "admin"
    }
  }
}
```

#### 4. 資源不存在 (404)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "404_NOT_FOUND",
    "message": "Resource not found",
    "details": {
      "resource_type": "card",
      "resource_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
```

#### 5. 衝突 (409)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "409_CONFLICT",
    "message": "Resource already exists",
    "details": {
      "field": "email",
      "value": "user@example.com"
    }
  }
}
```

#### 6. 業務邏輯錯誤 (422)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "422_LIMIT_EXCEEDED",
    "message": "Daily upload limit exceeded",
    "details": {
      "limit_type": "daily_upload",
      "limit": 2,
      "current": 2
    }
  }
}
```

#### 7. 速率限制 (429)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "429_RATE_LIMITED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "retry_after": 3600,
      "limit": 5,
      "window": "day"
    }
  }
}
```

#### 8. 伺服器錯誤 (500)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "500_INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": {}
  }
}
```

#### 9. 服務不可用 (503)

```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "503_SERVICE_UNAVAILABLE",
    "message": "Service temporarily unavailable. Please try again later.",
    "details": {
      "service": "google_play_billing"
    }
  }
}
```

## 錯誤代碼規範

### 命名規則

```
{HTTP_STATUS_CODE}_{ERROR_TYPE}
```

範例：
- `400_VALIDATION_FAILED`
- `401_UNAUTHORIZED`
- `422_LIMIT_EXCEEDED`
- `429_RATE_LIMITED`

### 常用錯誤代碼清單

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | `400_VALIDATION_FAILED` | 請求驗證失敗 |
| 400 | `400_INVALID_REQUEST` | 無效的請求 |
| 401 | `401_UNAUTHORIZED` | 未授權（未登入或 token 無效） |
| 401 | `401_TOKEN_EXPIRED` | Token 已過期 |
| 403 | `403_FORBIDDEN` | 權限不足 |
| 403 | `403_BLOCKED` | 使用者已被封鎖 |
| 404 | `404_NOT_FOUND` | 資源不存在 |
| 409 | `409_CONFLICT` | 資源衝突（如 email 重複） |
| 422 | `422_LIMIT_EXCEEDED` | 超過限制（上傳次數、容量等） |
| 422 | `422_INVALID_STATE` | 無效的狀態轉換 |
| 429 | `429_RATE_LIMITED` | 速率限制 |
| 500 | `500_INTERNAL_ERROR` | 內部伺服器錯誤 |
| 503 | `503_SERVICE_UNAVAILABLE` | 服務暫時不可用 |

## 實作指引

### 後端實作

#### 1. 使用共用 Helper Functions

```python
from app.shared.presentation.response import success, paginated, error_response

# 單一資源回應
return success(data=user_data)

# 分頁回應
return paginated(
    data=items,
    total=100,
    page=1,
    page_size=20
)

# 錯誤回應（由 middleware 自動處理）
raise APIException(
    status_code=422,
    error_code="422_LIMIT_EXCEEDED",
    message="Daily upload limit exceeded",
    details={"limit": 2}
)
```

#### 2. Response Models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class ResponseEnvelope(BaseModel, Generic[T]):
    data: Optional[T] = None
    meta: Optional[dict] = None
    error: Optional[dict] = None
```

### 前端處理

#### 1. 解析回應

```typescript
// Success
if (response.data && !response.error) {
  const data = response.data;
  // 處理資料
}

// Paginated
if (response.data && response.meta) {
  const items = response.data;
  const { total, page, page_size } = response.meta;
  // 處理分頁資料
}

// Error
if (response.error) {
  const { code, message, details } = response.error;
  // 顯示錯誤訊息
}
```

#### 2. TanStack Query Integration

```typescript
const { data, error, isLoading } = useQuery({
  queryKey: ['cards'],
  queryFn: async () => {
    const response = await api.get('/api/v1/cards/me');
    if (response.error) {
      throw new Error(response.error.message);
    }
    return response.data;
  }
});
```

## 遷移策略

### Phase 1: 建立基礎設施
1. 建立共用 response helper functions
2. 更新全域錯誤處理中介軟體

### Phase 2: 後端遷移
1. Identity 模組（auth, profile, subscriptions）
2. Social 模組（cards, chat, friends, nearby, rating, report, trade）
3. Posts 模組

### Phase 3: 測試更新
1. 更新所有整合測試
2. 更新單元測試中的 mock 回應

### Phase 4: OpenAPI & SDK
1. 重新生成 OpenAPI snapshot
2. 重新生成 Mobile SDK

### Phase 5: 前端遷移
1. 更新 API hooks/queries
2. 更新錯誤處理
3. 測試與驗證

## 向後相容性

**重要**: 此變更為 breaking change，需要同步更新前後端。

建議採用以下策略：
1. 在單一 PR 中完成後端遷移
2. 確保所有測試通過
3. 重新生成 OpenAPI 和 SDK
4. 在同一 PR 中更新前端
5. 完整測試後再部署

## 檢查清單

### 後端
- [ ] 所有 router 使用統一的 response envelope
- [ ] 錯誤處理中介軟體已更新
- [ ] Response schemas 已定義
- [ ] Helper functions 已實作
- [ ] 所有測試已更新

### 前端
- [ ] SDK 已重新生成
- [ ] API hooks 已更新
- [ ] 錯誤處理已更新
- [ ] 型別定義已更新
- [ ] UI 元件已調整

### 文件
- [ ] API 文件已更新
- [ ] OpenAPI snapshot 已更新
- [ ] README 已更新
- [ ] 遷移指南已撰寫

## 參考資料

- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Google JSON Style Guide](https://google.github.io/styleguide/jsoncstyleguide.xml)
- [JSON:API Specification](https://jsonapi.org/)

## 版本歷史

- **1.0.0** (2026-01-02): 初版發布
