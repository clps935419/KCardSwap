# 測試覆蓋率補齊工作總結

## 當前狀態
- **起始覆蓋率**: 約 61%
- **當前覆蓋率**: 約 62-63% (初步提升)
- **目標覆蓋率**: 接近 100%

## 已完成工作

### 1. 修復現有失敗測試 ✅
**問題**: Post entity 新增了 `scope` 和 `category` 參數，導致 30 個測試失敗 + 71 個錯誤

**解決方案**:
- 更新所有 `Post()` 初始化以包含 `scope=PostScope.CITY` 和 `category=PostCategory.TRADE`
- 修復 `CreatePostUseCase.execute()` 調用，添加必需參數
- 修正 mock repositories 返回正確的類型

**結果**:
- ✅ test_create_post_use_case.py (10/10 通過)
- ✅ test_accept_interest_use_case.py (7/7 通過)
- ✅ test_reject_interest_use_case.py (6/6 通過)  
- ✅ test_express_interest_use_case.py (6/6 通過)
- ✅ test_list_post_interests_use_case.py (6/6 通過)
- ⚠️ test_close_post_use_case.py (4/5 通過)
- ⚠️ test_list_board_posts_use_case.py (4/8 通過)
- ⚠️ test_post_repository_impl.py (8/9 通過)

**總計**: 從 30 failed + 71 errors 降至 **5 failed + 0 errors**

### 2. 新增 Identity 模組 Schema 測試 ✅
**創建文件**:
- `tests/unit/identity/presentation/schemas/test_idol_schemas.py` (5 tests)
- `tests/unit/identity/presentation/schemas/test_subscription_schemas.py` (8 tests)

**測試覆蓋**:
- IdolGroupResponse 創建和驗證
- IdolGroupListResponse 和 Wrapper
- SubscriptionStatusData (active/free)
- VerifyReceiptRequest (android/ios)
- ExpireSubscriptionsData/Response

**結果**: 13/13 測試通過 ✅

## 待完成工作 (按優先級排序)

### 優先級 1: 修復剩餘 5 個失敗測試
**文件**: 
- `test_list_board_posts_use_case.py` (4 個失敗)
  - 問題: 測試期望 `list_by_city()` 帶 scope/category，但實際 use case 未傳遞
  - 解決: 檢查 ListBoardPostsUseCase 實現，更新測試預期或實現
  
- `test_post_repository_impl.py` (1 個失敗)
  - 問題: fixture 創建的 model 返回 None 作為 scope
  - 解決: 修正 fixture 以正確設定 scope/category

### 優先級 2: 補齊 0% 覆蓋率模組 (Routers)

#### Identity Module Routers (0%)
- [ ] `idols_router.py` - GET /api/identity/idols 端點測試
- [ ] `subscription_router.py` - 訂閱相關端點測試

**測試策略**: 使用 FastAPI TestClient 測試 HTTP endpoints
```python
from fastapi.testclient import TestClient

def test_get_idol_groups(client: TestClient):
    response = client.get("/api/identity/idols")
    assert response.status_code == 200
    # ...
```

#### Social Module Routers & Schemas (0%)
- [ ] `cards_router.py` - 卡片交換端點
- [ ] `chat_router.py` - 聊天端點
- [ ] `gallery_router.py` (32.5%) - 相簿端點 (需提升)
- [ ] `card_schemas.py` - Pydantic schemas
- [ ] `chat_schemas.py` - Pydantic schemas

### 優先級 3: Middleware & Dependencies (0%)
- [ ] `subscription_check.py` - 訂閱檢查 middleware
- [ ] `use_case_deps.py` (Social) - 依賴注入
- [ ] `auth.py` (27.8%) - 認證依賴

### 優先級 4: Application Use Cases (20-48%)
- [ ] Social use cases:
  - `reorder_gallery_cards.py` (20.6%)
  - `accept_request.py` (25.0%)
  - `create_request.py` (31.2%)
  - `decline_request.py` (33.3%)

- [ ] Identity use cases:
  - `verify_receipt_use_case.py` (24.0%)

### 優先級 5: Repositories (25-36%)
- [ ] Social repositories:
  - `gallery_card_repository.py` (27.4%)
  - `message_request_repository.py` (31.5%)
  - `thread_repository.py` (32.7%)

- [ ] Identity repositories:
  - `refresh_token_repository_impl.py` (31.7%)

### 優先級 6: Infrastructure & Services
- [ ] External services:
  - `google_play_billing_service.py` (17.4%)
  - `fcm_service.py` (22.6%)
  - `gcs_storage_service.py` (38%)
  - `jwt_service.py` (39%)

- [ ] Database:
  - `connection.py` (38%)

- [ ] Utils:
  - `geolocation.py` (15.4%)

## 測試實施指南

### Router 測試模板
```python
"""Unit tests for [Router Name]"""
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

class Test[RouterName]:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()
    
    @pytest.fixture  
    def client(self, mock_use_case):
        # Override dependency
        from app.main import app
        app.dependency_overrides[get_use_case] = lambda: mock_use_case
        yield TestClient(app)
        app.dependency_overrides.clear()
    
    def test_endpoint_success(self, client, mock_use_case):
        # Arrange
        mock_use_case.execute.return_value = expected_result
        
        # Act
        response = client.get("/api/endpoint")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_json
```

### Use Case 測試模板
```python
"""Unit tests for [UseCase Name]"""
from unittest.mock import AsyncMock
import pytest

class Test[UseCaseName]:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def use_case(self, mock_repository):
        return UseCaseName(repository=mock_repository)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, use_case, mock_repository):
        # Arrange
        mock_repository.method.return_value = expected
        
        # Act
        result = await use_case.execute(params)
        
        # Assert
        assert result == expected
        mock_repository.method.assert_called_once_with(params)
```

### Repository 測試模板
```python
"""Unit tests for [Repository Name]"""
from unittest.mock import AsyncMock, MagicMock
import pytest

class Test[RepositoryName]:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock()
    
    @pytest.fixture
    def repository(self, mock_session):
        return RepositoryImpl(session=mock_session)
    
    @pytest.mark.asyncio
    async def test_method(self, repository, mock_session):
        # Arrange
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await repository.method(params)
        
        # Assert
        assert result == expected
        mock_session.execute.assert_called_once()
```

## 執行計劃

### 短期目標 (立即)
1. ✅ 修復 Post 測試失敗 (已完成大部分)
2. ⏳ 修復剩餘 5 個失敗測試
3. ⏳ 完成所有 0% 覆蓋率的 schemas 測試

### 中期目標 (本週)
4. 完成所有 0% 覆蓋率的 routers 測試
5. 完成 middleware 和 dependencies 測試
6. 提升 application use cases 至 > 80%

### 長期目標 (下週)
7. 提升所有 repositories 至 > 90%
8. 提升 infrastructure services 至 > 80%
9. 最終驗證並達到 > 95% 整體覆蓋率

## 測試運行命令

```bash
# 運行所有測試並生成覆蓋率報告
cd apps/backend
python3 -m pytest --cov=app --cov-report=term-missing --cov-report=html

# 只運行 unit 測試
python3 -m pytest tests/unit -v

# 運行特定模組
python3 -m pytest tests/unit/identity -v
python3 -m pytest tests/unit/social -v
python3 -m pytest tests/unit/posts -v

# 查看 HTML 覆蓋率報告
# 打開 apps/backend/htmlcov/index.html
```

## 已知問題和注意事項

1. **Integration 測試需要資料庫**: 目前 integration 測試因沒有 PostgreSQL 而失敗，這是預期的
2. **Post 參數變更**: 確保所有新的 Post 測試都包含 `scope` 和 `category`
3. **Mock 類型**: AsyncMock 需要正確返回值類型，否則會導致比較錯誤
4. **Pydantic 驗證**: Schema 測試應該測試驗證規則，不只是成功案例

## 進度追蹤

- ✅ 階段 1: 修復現有測試 (90% 完成)
- ⏳ 階段 2: 0% 覆蓋率模組 (15% 完成)
- ⏺️  階段 3: 低覆蓋率模組 (0% 完成)
- ⏺️  階段 4: 最終驗證 (0% 完成)

**預估完成時間**: 需要額外 8-12 小時工作時間

## 下一步行動

建議按以下順序繼續：

1. **修復 5 個失敗測試** (30 mins)
2. **完成 Identity routers 測試** (1-2 hours)
3. **完成 Social routers 測試** (2-3 hours)
4. **完成 middleware 測試** (1 hour)
5. **批量提升 use cases 覆蓋率** (2-3 hours)
6. **批量提升 repositories 覆蓋率** (2-3 hours)
7. **最終驗證和優化** (1 hour)
