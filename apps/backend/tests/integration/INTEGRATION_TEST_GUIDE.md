# Integration Test Guide - 使用測試資料庫

本指南說明如何在整合測試中使用新的測試資料庫 (`kcardswap_test`)。

## 概述

測試資料庫已經設定完成，提供以下功能：
- ✅ 獨立的測試資料庫 (`kcardswap_test`)
- ✅ 自動事務回滾，每個測試後清理資料
- ✅ 與開發資料庫完全隔離
- ✅ 支援並行測試執行

## 整合測試的兩種方式

### 方式 1: 使用真實資料庫 (推薦用於 E2E 測試)

使用 `db_session` fixture 連接到真實測試資料庫，測試完整的資料流程。

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestProfileFlowWithRealDB:
    """使用真實資料庫的整合測試範例"""

    @pytest.fixture
    def test_user_id(self, db_session):
        """建立測試用戶並返回 ID"""
        # 插入測試用戶到資料庫
        result = db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": "test_google_123",
                "email": "test@example.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        db_session.flush()
        return user_id

    @pytest.fixture
    def authenticated_client(self, test_user_id):
        """建立已認證的測試客戶端"""
        async def override_get_current_user_id():
            return test_user_id
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def test_client_with_db(self, db_session):
        """提供使用真實資料庫的測試客戶端"""
        async def override_get_db_session():
            return db_session
        
        app.dependency_overrides[get_db_session] = override_get_db_session
        yield client
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_and_get_profile(
        self,
        test_user_id,
        authenticated_client,
        test_client_with_db
    ):
        """測試建立和取得個人檔案"""
        # 建立個人檔案
        profile_data = {
            "nickname": "TestUser",
            "bio": "Test bio",
            "region": "TPE"
        }
        
        response = authenticated_client.post(
            "/api/v1/profile/me",
            json=profile_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["nickname"] == "TestUser"
        
        # 取得個人檔案
        response = authenticated_client.get("/api/v1/profile/me")
        assert response.status_code == 200
        assert response.json()["data"]["nickname"] == "TestUser"
        
        # 測試後資料會自動回滾，不會影響其他測試
```

### 方式 2: 使用 Mock (適用於隔離測試)

當你只想測試 API 邏輯而不需要資料庫時，可以繼續使用 Mock。

```python
from unittest.mock import AsyncMock, Mock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestProfileFlowWithMock:
    """使用 Mock 的整合測試範例"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock 資料庫 session"""
        mock_session = Mock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.flush = AsyncMock()
        
        async def override_get_db_session():
            return mock_session
        
        app.dependency_overrides[get_db_session] = override_get_db_session
        yield mock_session
        app.dependency_overrides.clear()

    def test_profile_api_with_mock(self, mock_db_session):
        """使用 Mock 測試 API 邏輯"""
        # 設定 Mock 行為
        mock_db_session.execute.return_value.scalar.return_value = "mock_profile_id"
        
        response = client.get("/api/v1/profile/me")
        # 測試 API 邏輯...
```

## 使用 `db_session` Fixture

`db_session` fixture 在 `tests/conftest.py` 中定義，提供以下功能：

### 特性

1. **自動回滾**: 每個測試後自動回滾所有變更
2. **資料隔離**: 測試之間完全獨立
3. **並行安全**: 多個測試可同時執行
4. **真實資料庫**: 測試完整的 SQL 查詢、constraint、trigger

### 範例：插入測試資料

```python
@pytest.mark.asyncio
async def test_with_test_data(db_session):
    """使用 db_session 插入測試資料"""
    from sqlalchemy import text
    
    # 插入用戶
    result = await db_session.execute(
        text("""
            INSERT INTO users (google_id, email, role)
            VALUES (:google_id, :email, :role)
            RETURNING id
        """),
        {"google_id": "test_123", "email": "test@example.com", "role": "user"}
    )
    user_id = result.scalar()
    await db_session.flush()
    
    # 插入個人檔案
    await db_session.execute(
        text("""
            INSERT INTO profiles (user_id, nickname)
            VALUES (:user_id, :nickname)
        """),
        {"user_id": user_id, "nickname": "TestNick"}
    )
    await db_session.flush()
    
    # 查詢資料
    result = await db_session.execute(
        text("SELECT nickname FROM profiles WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    nickname = result.scalar()
    assert nickname == "TestNick"
    
    # 測試結束後，所有資料自動回滾
```

## 執行整合測試

### 執行所有測試
```bash
# 使用 Makefile
make test

# 或直接使用 pytest
cd apps/backend
TEST_DATABASE_URL=******localhost:5432/kcardswap_test pytest tests/integration/ -v
```

### 執行特定測試
```bash
# 執行特定測試檔案
pytest tests/integration/modules/identity/test_profile_flow.py -v

# 執行特定測試類別
pytest tests/integration/modules/identity/test_profile_flow.py::TestProfileFlowWithRealDB -v

# 執行特定測試方法
pytest tests/integration/modules/identity/test_profile_flow.py::TestProfileFlowWithRealDB::test_create_profile -v
```

## 遷移現有測試

### 步驟 1: 移除 @pytest.mark.skip 裝飾器

```python
# Before
@pytest.mark.skip(reason="Requires database setup")
def test_get_profile(self):
    pass

# After
@pytest.mark.asyncio
async def test_get_profile(self, db_session, test_client_with_db):
    # 實作測試...
```

### 步驟 2: 使用 db_session 建立測試資料

```python
@pytest.fixture
async def test_user(self, db_session):
    """建立測試用戶"""
    from sqlalchemy import text
    
    result = await db_session.execute(
        text("""
            INSERT INTO users (google_id, email, role)
            VALUES (:google_id, :email, :role)
            RETURNING id
        """),
        {"google_id": "test_user", "email": "user@test.com", "role": "user"}
    )
    user_id = result.scalar()
    await db_session.flush()
    return user_id
```

### 步驟 3: Override FastAPI dependencies

```python
@pytest.fixture
def authenticated_client(self, test_user, db_session):
    """提供已認證的測試客戶端"""
    from app.shared.presentation.dependencies.auth import get_current_user_id
    from app.shared.infrastructure.database.connection import get_db_session
    
    async def override_get_current_user_id():
        return test_user
    
    async def override_get_db_session():
        return db_session
    
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    yield client
    
    app.dependency_overrides.clear()
```

## 最佳實務

### ✅ 推薦做法

1. **使用 Fixture 建立測試資料**: 重複使用測試資料設置邏輯
2. **測試完整流程**: 測試 API → 應用層 → 資料庫的完整路徑
3. **驗證資料庫狀態**: 直接查詢資料庫驗證結果
4. **使用事務**: 依賴自動回滾，不需手動清理

### ❌ 避免做法

1. **不要手動清理資料**: 事務會自動回滾
2. **不要依賴測試執行順序**: 每個測試應該獨立
3. **不要在測試間共享狀態**: 使用 fixture 為每個測試建立新資料

## 範例測試檔案

完整範例請參考：
- `tests/test_db_session.py` - 基礎資料庫測試
- `tests/integration/examples/test_profile_with_real_db.py` - 實際整合測試範例 (即將建立)

## 疑難排解

### 測試資料庫連接失敗
```bash
# 確認測試資料庫存在
docker compose exec db psql -U kcardswap -d kcardswap_test -c "\l"

# 執行 migrations
DATABASE_URL=******localhost:5432/kcardswap_test alembic upgrade head
```

### 測試資料沒有回滾
確認測試函數有正確使用 `db_session` fixture：
```python
@pytest.mark.asyncio
async def test_example(db_session):  # ← 必須包含 db_session 參數
    # 測試邏輯...
```

### AsyncIO 錯誤
確認測試函數使用 `@pytest.mark.asyncio` 裝飾器：
```python
@pytest.mark.asyncio  # ← 必須有這個裝飾器
async def test_example(db_session):
    # 測試邏輯...
```

## 更多資訊

- 測試資料庫配置: `apps/backend/tests/conftest.py`
- 資料庫初始化: `infra/db/init-test-db.sh`
- Makefile 指令: `Makefile` (root directory)
