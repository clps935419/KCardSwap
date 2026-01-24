# Priority 5 路線圖：API 端點整合測試 (E2E)

## 📊 當前狀況

### 已完成
- ✅ Priority 1-3: 基礎路由器測試 (165 tests)
- ✅ Priority 4: 單元測試 + 基礎設施整合測試 (173 tests)
- ✅ 總測試數: 338+ tests
- ✅ 覆蓋率: 88-90%

### 目標
- **目標覆蓋率**: 92-95%
- **提升幅度**: +2-5%
- **測試類型**: API 端點 E2E 整合測試

## 🎯 Priority 5 工作清單

### 1. Subscription Router E2E Tests (預計 8-10 tests, 1h)

#### 端點列表
```python
POST   /api/subscriptions/verify-receipt
GET    /api/subscriptions/me
GET    /api/subscriptions/plans
```

#### 測試場景
**POST /subscriptions/verify-receipt**:
- ✅ 有效收據驗證成功
- ✅ 無效收據驗證失敗
- ✅ 重複收據處理
- ✅ 未授權請求 (401)

**GET /subscriptions/me**:
- ✅ 已訂閱用戶獲取訂閱資訊
- ✅ 未訂閱用戶返回 null
- ✅ 未授權請求 (401)

**GET /subscriptions/plans**:
- ✅ 獲取所有訂閱方案
- ✅ 方案格式驗證

### 2. Cards Router E2E Tests (預計 10-12 tests, 1.5h)

#### 端點列表
```python
GET    /api/cards/mine
POST   /api/cards
PUT    /api/cards/{card_id}
DELETE /api/cards/{card_id}
POST   /api/cards/reorder
```

#### 測試場景
**GET /cards/mine**:
- ✅ 獲取當前用戶的卡片列表
- ✅ 空列表場景
- ✅ 分頁測試
- ✅ 未授權請求 (401)

**POST /cards**:
- ✅ 創建新卡片成功
- ✅ 缺少必填欄位 (422)
- ✅ 無效資料格式 (422)
- ✅ 未授權請求 (401)

**PUT /cards/{card_id}**:
- ✅ 更新卡片成功
- ✅ 卡片不存在 (404)
- ✅ 非擁有者更新 (403)
- ✅ 無效資料 (422)

**DELETE /cards/{card_id}**:
- ✅ 刪除卡片成功
- ✅ 卡片不存在 (404)
- ✅ 非擁有者刪除 (403)

**POST /cards/reorder**:
- ✅ 重新排序成功
- ✅ 無效順序資料 (422)

### 3. Chat & Threads Router E2E Tests (預計 8-10 tests, 1h)

#### 端點列表
```python
# Threads
GET    /api/threads
GET    /api/threads/{thread_id}
POST   /api/threads

# Chat Messages
GET    /api/threads/{thread_id}/messages
POST   /api/threads/{thread_id}/messages
DELETE /api/threads/{thread_id}/messages/{message_id}
```

#### 測試場景
**Threads**:
- ✅ 獲取用戶的執行緒列表
- ✅ 獲取特定執行緒詳情
- ✅ 創建新執行緒
- ✅ 執行緒不存在 (404)

**Chat Messages**:
- ✅ 獲取執行緒訊息 (含分頁)
- ✅ 發送新訊息
- ✅ 刪除訊息
- ✅ 非參與者訪問 (403)

### 4. Profile Router E2E Tests (預計 4-6 tests, 0.5h)

#### 端點列表
```python
GET    /api/profiles/{user_id}
PATCH  /api/profiles/me
```

#### 測試場景
**GET /profiles/{user_id}**:
- ✅ 獲取其他用戶個人資料
- ✅ 用戶不存在 (404)
- ✅ 隱私設定測試

**PATCH /profiles/me**:
- ✅ 更新個人資料成功
- ✅ 無效資料 (422)
- ✅ 未授權 (401)

### 5. Friends Router E2E Tests (預計 4-6 tests, 0.5h)

#### 端點列表
```python
GET    /api/friends
DELETE /api/friends/{friend_id}
```

#### 測試場景
**GET /friends**:
- ✅ 獲取好友列表
- ✅ 空列表場景
- ✅ 分頁測試

**DELETE /friends/{friend_id}**:
- ✅ 刪除好友成功
- ✅ 好友關係不存在 (404)

### 6. Idols Router E2E Tests (預計 2-3 tests, 0.5h)

#### 端點列表
```python
GET    /api/idols
```

#### 測試場景
- ✅ 獲取所有偶像列表
- ✅ 列表格式驗證
- ✅ 空列表場景

## 📈 預期成果

### 測試數量
- **當前**: 338+ tests (Priority 1-4)
- **新增**: 30-40 tests (Priority 5)
- **總計**: 370-380 tests

### 覆蓋率
- **當前**: 88-90%
- **完成後**: 92-95%
- **提升**: +2-5%

### 工作時數
- **預計**: 5-6 小時
- **階段**: Priority 5

## 🚀 測試策略

### 測試框架
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
```

### 測試模式
```python
@pytest.mark.integration
def test_api_endpoint_success(test_db_session, authenticated_user):
    """
    API 端點成功場景測試
    
    Given: 已認證用戶
    When: 發送有效請求到 API 端點
    Then: 返回正確的回應和狀態碼
    """
    # Arrange
    headers = {"Authorization": f"Bearer {authenticated_user.token}"}
    payload = {"field": "value"}
    
    # Act
    response = client.post("/api/endpoint", json=payload, headers=headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "data" in response.json()


@pytest.mark.integration
def test_api_endpoint_unauthorized():
    """
    API 端點未授權測試
    
    Given: 未認證用戶
    When: 發送請求到需要認證的端點
    Then: 返回 401 Unauthorized
    """
    # Act
    response = client.get("/api/protected-endpoint")
    
    # Assert
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.integration
def test_api_endpoint_not_found():
    """
    API 端點資源不存在測試
    
    Given: 已認證用戶
    When: 請求不存在的資源
    Then: 返回 404 Not Found
    """
    # Arrange
    headers = {"Authorization": f"Bearer {authenticated_user.token}"}
    
    # Act
    response = client.get("/api/resource/nonexistent-id", headers=headers)
    
    # Assert
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
def test_api_endpoint_validation_error():
    """
    API 端點驗證錯誤測試
    
    Given: 已認證用戶
    When: 發送無效資料到 API 端點
    Then: 返回 422 Validation Error
    """
    # Arrange
    headers = {"Authorization": f"Bearer {authenticated_user.token}"}
    invalid_payload = {"field": ""}  # 缺少必填欄位
    
    # Act
    response = client.post("/api/endpoint", json=invalid_payload, headers=headers)
    
    # Assert
    assert response.status_code == 422
    assert "detail" in response.json()
```

### Fixtures 設定
```python
@pytest.fixture
def test_db_session():
    """提供測試資料庫會話"""
    # 使用 Makefile 配置的測試資料庫
    session = create_test_session()
    yield session
    session.rollback()  # 回滾測試資料
    session.close()


@pytest.fixture
def authenticated_user(test_db_session):
    """創建並返回已認證用戶"""
    user = create_test_user(test_db_session)
    token = generate_test_token(user)
    return {"user": user, "token": token}


@pytest.fixture
def test_data(test_db_session):
    """準備測試資料"""
    # 創建測試所需的資料
    data = setup_test_data(test_db_session)
    yield data
    # 清理測試資料
    cleanup_test_data(test_db_session)
```

## 📝 執行順序

### 階段 1: 高優先級 (1.5-2h)
1. Subscription Router (8-10 tests)
2. Cards Router (10-12 tests)

### 階段 2: 中優先級 (1-1.5h)
3. Chat & Threads Router (8-10 tests)

### 階段 3: 低優先級 (0.5-1h)
4. Profile Router (4-6 tests)
5. Friends Router (4-6 tests)
6. Idols Router (2-3 tests)

## 🎯 成功標準

### 測試品質
- ✅ 所有測試通過 (100% pass rate)
- ✅ 遵循 AAA 模式
- ✅ 完整的錯誤場景覆蓋
- ✅ 認證/授權測試
- ✅ 資料驗證測試

### 覆蓋率
- ✅ 達到 92-95% 總覆蓋率
- ✅ 所有主要 API 端點有測試
- ✅ 所有錯誤場景有測試

### 執行效能
- ✅ 整合測試執行時間 < 60s
- ✅ 測試隔離性良好
- ✅ 無測試間相依性

## 📊 與 Priority 4 的差異

| 項目 | Priority 4 | Priority 5 |
|------|-----------|-----------|
| **焦點** | 單元測試 + 基礎設施整合 | API 端點 E2E 整合 |
| **測試類型** | Unit + Integration (Infrastructure) | Integration (API E2E) |
| **測試對象** | Services, Repositories, Middleware | API Endpoints, Request/Response |
| **Mock 程度** | 高 (大量 Mock) | 低 (真實資料庫) |
| **測試範圍** | 模組級別 | 端點級別 |
| **執行時間** | ~10-15s | ~30-60s |

## 🔄 後續計劃

### Priority 6: 效能與安全測試 (可選)
- 負載測試 (Locust)
- 安全測試 (SQL Injection, XSS, CSRF)
- 壓力測試 (連接池、併發)

---

**文檔創建**: 2026-01-24  
**當前狀態**: Priority 4 完成，準備開始 Priority 5  
**預計完成**: Priority 5 完成後達到 92-95% 覆蓋率
