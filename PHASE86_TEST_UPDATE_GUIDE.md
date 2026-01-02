# Phase 8.6 - Integration Test Update Guide

**Date**: 2026-01-02  
**Purpose**: 指導如何更新整合測試以支援新的 envelope 回應格式  
**Status**: Ready for execution (需要資料庫環境)

## 概述

Phase 8.6 實作了統一的 API 回應格式 (`{data, meta, error}`)。所有整合測試需要更新斷言以解析新的 envelope 結構。

## 回應格式變更

### 舊格式 ❌

```python
# 直接回傳資料
{
  "cities": [...],
  "id": "uuid",
  "nickname": "user"
}
```

### 新格式 ✅

```python
# Envelope 包裝
{
  "data": {...} | [...],
  "meta": {...} | null,
  "error": {...} | null
}
```

## 測試更新模式

### 模式 1: 單一資源回應

**舊測試**:
```python
def test_get_profile(self, client, auth_token):
    response = client.get(
        "/api/v1/profile/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()  # ❌ 直接取得資料
    assert data["id"]
    assert data["email"] == "test@example.com"
```

**新測試**:
```python
def test_get_profile(self, client, auth_token):
    response = client.get(
        "/api/v1/profile/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    body = response.json()
    
    # 驗證 envelope 結構
    assert "data" in body
    assert "meta" in body
    assert "error" in body
    assert body["error"] is None
    
    # 從 envelope 提取資料
    data = body["data"]  # ✅ 從 envelope 提取
    assert data["id"]
    assert data["email"] == "test@example.com"
```

### 模式 2: 列表回應（無分頁）

**舊測試**:
```python
def test_get_cities(self, client):
    response = client.get("/api/v1/locations/cities")
    
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data  # ❌
    cities = data["cities"]
    assert len(cities) == 22
```

**新測試**:
```python
def test_get_cities(self, client):
    response = client.get("/api/v1/locations/cities")
    
    assert response.status_code == 200
    body = response.json()
    
    # 驗證 envelope
    assert "data" in body
    assert body["error"] is None
    assert body["meta"] is None  # 無分頁
    
    # 提取列表
    cities = body["data"]  # ✅ data 直接是列表
    assert isinstance(cities, list)
    assert len(cities) == 22
```

### 模式 3: 分頁列表回應

**舊測試**:
```python
def test_get_my_cards(self, client, auth_token):
    response = client.get(
        "/api/v1/cards/me?page=1&page_size=20",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data  # ❌
    assert "total" in data  # ❌
    cards = data["items"]
```

**新測試**:
```python
def test_get_my_cards(self, client, auth_token):
    response = client.get(
        "/api/v1/cards/me?page=1&page_size=20",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    body = response.json()
    
    # 驗證 envelope
    assert "data" in body
    assert "meta" in body  # ✅ 分頁資訊在 meta
    assert "error" in body
    assert body["error"] is None
    
    # 驗證分頁 meta
    meta = body["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "page_size" in meta
    assert "total_pages" in meta
    assert meta["page"] == 1
    assert meta["page_size"] == 20
    assert meta["total"] >= 0
    
    # 提取列表資料
    cards = body["data"]  # ✅ data 是列表
    assert isinstance(cards, list)
    assert len(cards) <= 20
```

### 模式 4: 錯誤回應

**舊測試**:
```python
def test_get_nonexistent_card(self, client, auth_token):
    response = client.get(
        "/api/v1/cards/nonexistent-id",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data  # ❌ FastAPI 預設格式
```

**新測試**:
```python
def test_get_nonexistent_card(self, client, auth_token):
    response = client.get(
        "/api/v1/cards/nonexistent-id",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    body = response.json()
    
    # 驗證錯誤 envelope
    assert "data" in body
    assert "meta" in body
    assert "error" in body
    assert body["data"] is None
    assert body["meta"] is None
    
    # 驗證錯誤結構
    error = body["error"]  # ✅
    assert error is not None
    assert "code" in error
    assert "message" in error
    assert error["code"] == "404_NOT_FOUND"
```

### 模式 5: 驗證錯誤 (422)

**新測試**:
```python
def test_upload_exceeds_quota(self, client, auth_token):
    # 假設已上傳 2 張（免費用戶限制）
    response = client.post(
        "/api/v1/cards/upload-url",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"file_size": 1000000}
    )
    
    assert response.status_code == 422
    body = response.json()
    
    # 驗證錯誤 envelope
    assert body["data"] is None
    assert body["meta"] is None
    assert body["error"] is not None
    
    # 驗證錯誤詳情
    error = body["error"]
    assert error["code"] == "422_LIMIT_EXCEEDED"
    assert "limit_type" in error["details"]
    assert error["details"]["limit_type"] == "daily_uploads"
```

## 需要更新的測試檔案

### 1. Locations Module
**檔案**: `tests/integration/modules/locations/test_city_list_flow.py`

**變更**:
```python
# 舊: data["cities"]
# 新: body["data"]

# 第 24-27 行
- assert "cities" in data
- assert isinstance(data["cities"], list)
- assert len(data["cities"]) == 22
- first_city = data["cities"][0]
+ assert "data" in body
+ assert body["error"] is None
+ assert isinstance(body["data"], list)
+ assert len(body["data"]) == 22
+ first_city = body["data"][0]
```

### 2. Identity Module

#### test_auth_flow.py
- 更新 `test_google_callback_success_new_user`
- 更新錯誤測試的斷言 (`detail` → `error`)

#### test_profile_flow.py
- 更新 `GET /profile/me` 斷言
- 更新 `PUT /profile/me` 斷言

#### test_subscription_flow.py
- 更新 `POST /subscriptions/verify-receipt` 斷言
- 更新 `GET /subscriptions/status` 斷言

### 3. Social Module - Cards

**檔案**: `tests/integration/modules/social/test_card_upload_flow.py`

**關鍵變更**:
```python
# 上傳 URL 回應
response = client.post("/api/v1/cards/upload-url")
body = response.json()
assert "data" in body
upload_info = body["data"]
assert "upload_url" in upload_info

# 我的卡冊（分頁）
response = client.get("/api/v1/cards/me?page=1&page_size=20")
body = response.json()
assert "data" in body
assert "meta" in body
cards = body["data"]
meta = body["meta"]
assert meta["page"] == 1

# 配額狀態
response = client.get("/api/v1/cards/quota/status")
body = response.json()
assert "data" in body
quota = body["data"]
```

### 4. Social Module - Others

**需要更新的檔案**:
- `test_posts_flow.py` - 分頁列表 + 興趣操作
- `test_rating_flow.py` - 評分 CRUD
- `test_trade_flow.py` - 交換流程
- `test_friendship_flow.py` - 好友操作
- `test_chat_flow.py` - 聊天訊息（分頁）
- `test_report_flow.py` - 檢舉提交
- `test_nearby_search_flow.py` - 附近搜尋

## 通用 Helper Function

建議在 `tests/conftest.py` 或測試基類中新增:

```python
def assert_success_response(body, data_type=dict):
    """驗證成功回應的 envelope 結構"""
    assert "data" in body, "Response missing 'data' field"
    assert "meta" in body, "Response missing 'meta' field"
    assert "error" in body, "Response missing 'error' field"
    assert body["error"] is None, f"Expected no error, got: {body['error']}"
    assert isinstance(body["data"], data_type), \
        f"Expected data type {data_type}, got {type(body['data'])}"
    return body["data"]

def assert_error_response(body, expected_code=None):
    """驗證錯誤回應的 envelope 結構"""
    assert "data" in body
    assert "meta" in body
    assert "error" in body
    assert body["data"] is None, "Error response should have null data"
    assert body["meta"] is None, "Error response should have null meta"
    assert body["error"] is not None, "Error response missing error object"
    
    error = body["error"]
    assert "code" in error
    assert "message" in error
    
    if expected_code:
        assert error["code"] == expected_code, \
            f"Expected error code {expected_code}, got {error['code']}"
    
    return error

def assert_paginated_response(body, expected_page=None, expected_page_size=None):
    """驗證分頁回應的 envelope 結構"""
    assert "data" in body
    assert "meta" in body
    assert "error" in body
    assert body["error"] is None
    
    meta = body["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "page_size" in meta
    assert "total_pages" in meta
    
    if expected_page is not None:
        assert meta["page"] == expected_page
    if expected_page_size is not None:
        assert meta["page_size"] == expected_page_size
    
    assert isinstance(body["data"], list)
    return body["data"], meta
```

**使用範例**:
```python
def test_get_profile_with_helper(client, auth_token):
    response = client.get(
        "/api/v1/profile/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    
    # 使用 helper
    profile = assert_success_response(response.json())
    assert profile["email"] == "test@example.com"

def test_get_cards_with_helper(client, auth_token):
    response = client.get(
        "/api/v1/cards/me?page=1&page_size=20",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    
    # 使用 helper
    cards, meta = assert_paginated_response(
        response.json(),
        expected_page=1,
        expected_page_size=20
    )
    assert len(cards) <= 20

def test_not_found_with_helper(client, auth_token):
    response = client.get(
        "/api/v1/cards/nonexistent",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
    
    # 使用 helper
    error = assert_error_response(
        response.json(),
        expected_code="404_NOT_FOUND"
    )
    assert "not found" in error["message"].lower()
```

## 執行步驟

### 前置條件
1. 確保 PostgreSQL 正在運行
2. 執行資料庫遷移: `poetry run alembic upgrade head`
3. 初始化測試資料（如需要）

### 執行測試

```bash
# 進入 backend 目錄
cd apps/backend

# 執行所有整合測試
poetry run pytest tests/integration/ -v

# 執行特定模組
poetry run pytest tests/integration/modules/locations/ -v
poetry run pytest tests/integration/modules/identity/ -v
poetry run pytest tests/integration/modules/social/ -v

# 執行特定測試檔案
poetry run pytest tests/integration/modules/locations/test_city_list_flow.py -v

# 執行特定測試函數
poetry run pytest tests/integration/modules/locations/test_city_list_flow.py::TestCityListAPI::test_get_all_cities_success -v
```

### 預期結果

✅ **成功標準**:
- 所有測試通過 (綠燈)
- 無 assertion 錯誤
- 正確解析 envelope 結構
- 分頁 meta 驗證通過

❌ **常見錯誤**:
- `KeyError: 'cities'` → 改用 `body["data"]`
- `AssertionError: 'detail' not in data` → 改用 `body["error"]`
- `AssertionError: Expected dict, got list` → 檢查是否為列表回應

## 測試更新檢查清單

使用此清單追蹤進度：

### Locations Module
- [ ] `test_city_list_flow.py` - 5 個測試函數

### Identity Module
- [ ] `test_auth_flow.py` - Google OAuth + PKCE
- [ ] `test_profile_flow.py` - Profile CRUD
- [ ] `test_subscription_flow.py` - Subscription verify

### Social Module - Cards
- [ ] `test_card_upload_flow.py` - Upload + quota

### Social Module - Others
- [ ] `test_posts_flow.py` - Posts CRUD + interests
- [ ] `test_rating_flow.py` - Rating CRUD
- [ ] `test_trade_flow.py` - Trade flow
- [ ] `test_friendship_flow.py` - Friend operations
- [ ] `test_chat_flow.py` - Chat messages
- [ ] `test_report_flow.py` - Report submission
- [ ] `test_nearby_search_flow.py` - Nearby search
- [ ] `test_mark_message_read.py` - Message read status

## 常見問題

### Q1: 測試顯示 500 錯誤
**A**: 檢查資料庫連線與遷移狀態
```bash
poetry run alembic current
poetry run alembic upgrade head
```

### Q2: 測試中的 Mock 是否需要更新？
**A**: 是的，mock 回傳值也需要使用 envelope 格式
```python
# 舊 mock
mock_service.return_value = {"id": "123", "email": "test@example.com"}

# 新 mock
mock_service.return_value = {
    "data": {"id": "123", "email": "test@example.com"},
    "meta": None,
    "error": None
}
```

### Q3: 是否需要更新單元測試？
**A**: 不需要。單元測試測試的是內部邏輯，不涉及 HTTP 回應格式。只有整合測試需要更新。

### Q4: 如何處理已註解掉的測試？
**A**: 先更新斷言邏輯，然後在有資料庫環境時取消註解並執行。

## 相關文件

- [Response Format Specification](../../specs/001-kcardswap-complete-spec/response-format.md)
- [API Documentation](apps/backend/docs/api/README.md)
- [Backend Complete Report](PHASE86_BACKEND_COMPLETE.md)
- [OpenAPI Snapshot](openapi/openapi.json)

## 完成標準

測試更新完成的標準：

1. ✅ 所有 13 個測試檔案已更新
2. ✅ 所有測試函數斷言已修正
3. ✅ Helper functions 已建立（可選）
4. ✅ 執行 `poetry run pytest tests/integration/` 全數通過
5. ✅ 無 KeyError、AssertionError 等錯誤
6. ✅ 分頁測試正確驗證 meta 資訊
7. ✅ 錯誤測試正確驗證 error 結構

---

**狀態**: Ready for execution  
**預估時間**: 6-8 hours  
**需求**: PostgreSQL + Poetry 環境  
**優先順序**: High (blocking Mobile updates)
