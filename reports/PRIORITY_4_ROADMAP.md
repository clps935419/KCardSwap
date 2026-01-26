# Priority 4 測試路線圖

## 📊 當前狀況

### 覆蓋率
- **當前覆蓋率**: 85-90%
- **目標覆蓋率**: 90-95%
- **剩餘提升**: +5-7%

### 已完成
- ✅ Priority 1-3 所有路由器測試（13個路由器，165個測試）
- ✅ 413+ 個測試，100% 通過率
- ✅ 0 個安全漏洞
- ✅ 基礎設施、Schemas、中介軟體完整測試

## 🎯 剩餘工作清單

### 1. External Services (預計 1.5-2h, +2-3%)

#### GoogleOAuthService (38% → 95%)
**文件位置**: `app/shared/infrastructure/auth/google_oauth_service.py`

**需要測試的方法**:
```python
class GoogleOAuthService:
    def __init__(self, client_id: str, client_secret: str)
    async def verify_google_token(self, id_token: str) -> dict
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict
    async def exchange_code_with_pkce(self, code: str, code_verifier: str, redirect_uri: str) -> dict
```

**測試重點**:
- Token 驗證成功/失敗
- 授權碼交換（標準流程）
- PKCE 流程
- 錯誤處理（無效 token、網絡錯誤）
- HTTP 請求 mock

**預計測試數**: 10-12 tests

#### FCMService (23% → 95%)
**文件位置**: `app/shared/infrastructure/notifications/fcm_service.py`

**需要測試的方法**:
```python
class FCMService:
    def __init__(self, credentials_path: str)
    async def send_notification(self, token: str, title: str, body: str, data: dict = None) -> bool
    async def send_notification_to_multiple(self, tokens: List[str], title: str, body: str, data: dict = None) -> dict
```

**測試重點**:
- 單一通知發送
- 批量通知發送
- Firebase 初始化
- 無效 token 處理
- 網絡錯誤處理
- Data payload 處理

**預計測試數**: 8-10 tests

### 2. Repository Implementations (預計 1-1.5h, +1-2%)

#### ProfileRepository (33% → 85%)
**文件位置**: `app/modules/identity/infrastructure/repositories/profile_repository.py`

**需要測試的方法**:
```python
async def create(self, profile: Profile) -> Profile
async def get_by_user_id(self, user_id: str) -> Optional[Profile]
async def update(self, profile: Profile) -> Profile
async def delete(self, user_id: str) -> bool
```

**預計測試數**: 8-10 tests

#### ThreadRepository (32% → 85%)
**文件位置**: `app/modules/social/infrastructure/repositories/thread_repository.py`

**需要測試的方法**:
```python
async def create(self, thread: MessageThread) -> MessageThread
async def get_by_id(self, thread_id: str) -> Optional[MessageThread]
async def get_by_participants(self, user_id_1: str, user_id_2: str) -> Optional[MessageThread]
async def list_by_user(self, user_id: str) -> List[MessageThread]
```

**預計測試數**: 8-10 tests

#### RefreshTokenRepository (32% → 85%)
**文件位置**: `app/modules/identity/infrastructure/repositories/refresh_token_repository.py`

**需要測試的方法**:
```python
async def create(self, refresh_token: RefreshToken) -> RefreshToken
async def get_by_token(self, token: str) -> Optional[RefreshToken]
async def revoke(self, token: str) -> bool
async def revoke_all_for_user(self, user_id: str) -> int
```

**預計測試數**: 6-8 tests

#### SubscriptionRepository (35% → 85%)
**文件位置**: `app/modules/identity/infrastructure/repositories/subscription_repository.py`

**需要測試的方法**:
```python
async def create(self, subscription: Subscription) -> Subscription
async def get_by_user_id(self, user_id: str) -> Optional[Subscription]
async def update(self, subscription: Subscription) -> Subscription
async def get_active_subscription(self, user_id: str) -> Optional[Subscription]
```

**預計測試數**: 6-8 tests

### 3. Use Cases & Dependencies (預計 1.5-2h, +2-3%)

#### 低覆蓋率 Use Cases
**需要補齊的 use cases**:
- Gallery Card Related (27%)
- Message Requests Use Cases (25-33%)
- Reorder Gallery Cards (21%)
- Verify Receipt Use Case (24%)

**預計測試數**: 15-20 tests

#### Use Case Dependencies
**文件位置**: 
- `app/modules/social/presentation/use_case_deps.py`
- 其他模組的 use_case_deps

**測試重點**:
- 依賴注入正確性
- Injector 配置
- Use case 初始化

**預計測試數**: 5-8 tests

## 📈 預期成果

### 測試數量
- **當前**: 413+ tests
- **新增**: 70-90 tests
- **總計**: 480-500 tests

### 覆蓋率
- **當前**: 85-90%
- **完成後**: 90-95%
- **提升**: +5-7%

### 工作時數
- **預計**: 4.5-5.5 小時
- **階段**: Priority 4

## 🚀 執行建議

### 執行順序
1. **External Services** (高影響力)
   - GoogleOAuthService
   - FCMService

2. **Repository Implementations** (中影響力)
   - ProfileRepository
   - ThreadRepository
   - RefreshTokenRepository
   - SubscriptionRepository

3. **Use Cases & Dependencies** (補齊剩餘)
   - 低覆蓋 use cases
   - Use case dependencies

### 測試模式
```python
# External Service 測試模式
@pytest.fixture
def mock_http_client():
    return AsyncMock()

@pytest.mark.asyncio
async def test_service_method(service, mock_http_client):
    # Arrange
    mock_http_client.post.return_value = expected_response
    
    # Act
    result = await service.method(params)
    
    # Assert
    assert result == expected
    mock_http_client.post.assert_called_once()
```

```python
# Repository 測試模式
@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_repository_method(repository, mock_session):
    # Arrange
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await repository.method(params)
    
    # Assert
    assert result == expected
```

## 📝 注意事項

1. **跳過 Google Play Billing**: 此 POC 以 web 為主，不需要測試 Google Play Billing Service

2. **Mock 外部依賴**: 
   - HTTP 請求使用 httpx.AsyncClient mock
   - Firebase 使用 firebase_admin mock
   - 資料庫使用 AsyncSession mock

3. **保持一致性**:
   - AAA 模式
   - AsyncMock 適當使用
   - 清晰的測試命名

4. **文檔更新**:
   - 完成後更新 PROJECT_FINAL_SUMMARY.md
   - 創建 TEST_COVERAGE_PHASE8_SUMMARY.md

---

**文檔創建日期**: 2026-01-24  
**當前狀態**: Priority 1-3 完成，準備開始 Priority 4  
**預計完成日期**: Priority 4 完成後達到 90-95% 覆蓋率
