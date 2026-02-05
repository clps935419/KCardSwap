"""
整合測試範例 - 使用真實測試資料庫

此檔案展示如何在整合測試中使用測試資料庫進行端到端測試。
這些測試使用真實的資料庫連接，但所有變更會在測試後自動回滾。

執行方式:
    cd apps/backend
    TEST_DATABASE_URL=******localhost:5432/kcardswap_test pytest tests/integration/examples/ -v
"""

from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.infrastructure.database.connection import get_db_session
from app.shared.presentation.dependencies.auth import get_current_user_id

client = TestClient(app)


class TestProfileFlowWithRealDatabase:
    """個人檔案流程整合測試 - 使用真實資料庫"""

    @pytest_asyncio.fixture
    async def test_user(self, db_session) -> UUID:
        """建立測試用戶並返回用戶 ID

        這個 fixture 示範如何在測試資料庫中建立測試資料。
        測試結束後，這些資料會自動回滾。
        """
        user_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """
            ),
            {
                "id": user_id,
                "google_id": "test_integration_user",
                "email": "integration@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()
        return user_id

    @pytest_asyncio.fixture
    async def test_user_with_profile(self, db_session) -> tuple[UUID, UUID]:
        """建立有個人檔案的測試用戶

        Returns:
            tuple: (user_id, profile_id)
        """
        # 建立用戶
        user_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """
            ),
            {
                "id": user_id,
                "google_id": "test_user_with_profile",
                "email": "withprofile@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()

        # 建立個人檔案
        profile_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO profiles (id, user_id, nickname, bio, region)
                VALUES (:id, :user_id, :nickname, :bio, :region)
                RETURNING id
            """
            ),
            {
                "id": profile_id,
                "user_id": user_id,
                "nickname": "TestNickname",
                "bio": "Test bio",
                "region": "TPE",
            },
        )
        profile_id = result.scalar()
        await db_session.commit()

        return user_id, profile_id

    @pytest.fixture
    def authenticated_client(self, test_user, app_db_session_override):
        """提供已認證的測試客戶端

        此 fixture 示範如何 override FastAPI dependencies:
        1. 模擬已認證的用戶 (get_current_user_id)
        2. 注入真實的資料庫 session (get_db_session)
        """

        async def override_get_current_user_id():
            return test_user

        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = app_db_session_override

        yield client

        # 清理 dependency overrides
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_verify_database_rollback(self, db_session):
        """驗證資料庫事務回滾功能

        此測試示範：
        1. 插入資料到測試資料庫
        2. 在同一測試中可以查詢到資料
        3. 測試結束後，資料會自動回滾（在其他測試中查詢不到）
        """
        # 插入測試用戶
        user_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """
            ),
            {
                "id": user_id,
                "google_id": "rollback_test_user",
                "email": "rollback@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.flush()

        # 驗證資料存在
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM users WHERE id = :user_id"), {"user_id": user_id}
        )
        count = result.scalar()
        assert count == 1

        # 測試結束後，此資料會自動回滾

    @pytest.mark.asyncio
    async def test_verify_previous_test_data_rolled_back(self, db_session):
        """驗證前一個測試的資料已經回滾

        此測試確認 test_verify_database_rollback 中插入的資料
        已經被回滾，不會影響這個測試。
        """
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM users WHERE google_id = :google_id"),
            {"google_id": "rollback_test_user"},
        )
        count = result.scalar()
        assert count == 0, "前一個測試的資料應該已被回滾"

    @pytest.mark.asyncio
    async def test_query_user_profile_from_database(
        self, test_user_with_profile, db_session
    ):
        """測試直接從資料庫查詢用戶個人檔案

        此測試示範如何：
        1. 使用 fixture 建立測試資料
        2. 直接查詢資料庫驗證資料正確性
        """
        user_id, profile_id = test_user_with_profile

        # 查詢個人檔案
        result = await db_session.execute(
            text(
                """
                SELECT p.id, p.nickname, p.bio, p.region, u.email
                FROM profiles p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = :profile_id
            """
            ),
            {"profile_id": profile_id},
        )
        row = result.fetchone()

        assert row is not None
        assert row[1] == "TestNickname"  # nickname
        assert row[2] == "Test bio"  # bio
        assert row[3] == "TPE"  # region
        assert row[4] == "withprofile@test.com"  # email


class TestAuthenticationFlowWithRealDatabase:
    """認證流程整合測試 - 使用真實資料庫"""

    @pytest.mark.asyncio
    async def test_user_creation_in_database(self, db_session):
        """測試在資料庫中建立用戶

        此測試驗證：
        1. 可以成功插入新用戶
        2. 資料庫 constraints 正常運作
        3. 可以查詢插入的資料
        """
        # 插入新用戶
        user_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role, created_at)
                VALUES (:id, :google_id, :email, :role, NOW())
                RETURNING id, google_id, email, role, created_at
            """
            ),
            {
                "id": user_id,
                "google_id": "google_oauth_123",
                "email": "oauth@test.com",
                "role": "user",
            },
        )
        await db_session.commit()

        # 驗證插入結果（重新查詢避免 RETURNING 在某些環境下回傳空結果）
        result = await db_session.execute(
            text(
                """
                SELECT id, google_id, email, role, created_at
                FROM users
                WHERE id = :user_id
                """
            ),
            {"user_id": user_id},
        )
        row = result.fetchone()

        # 驗證插入結果
        assert row is not None
        assert row[1] == "google_oauth_123"  # google_id
        assert row[2] == "oauth@test.com"  # email
        assert row[3] == "user"  # role
        assert row[4] is not None  # created_at

    @pytest.mark.asyncio
    async def test_duplicate_email_constraint(self, db_session):
        """測試 email 唯一性約束

        此測試驗證資料庫 constraint 正常運作：
        嘗試插入重複的 email 應該失敗
        """
        # 插入第一個用戶
        await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
            """
            ),
            {
                "id": str(uuid4()),
                "google_id": "user1",
                "email": "duplicate@test.com",
                "role": "user",
            },
        )
        await db_session.flush()

        # 嘗試插入相同 email 的第二個用戶（應該失敗）
        with pytest.raises(Exception) as exc_info:
            await db_session.execute(
                text(
                    """
                    INSERT INTO users (id, google_id, email, role)
                    VALUES (:id, :google_id, :email, :role)
                """
                ),
                {
                    "id": str(uuid4()),
                    "google_id": "user2",
                    "email": "duplicate@test.com",  # 重複的 email
                    "role": "user",
                },
            )
            await db_session.flush()

        # 驗證錯誤訊息包含 unique constraint
        assert (
            "unique" in str(exc_info.value).lower()
            or "duplicate" in str(exc_info.value).lower()
        )


class TestDataRelationshipsWithRealDatabase:
    """資料關聯測試 - 使用真實資料庫"""

    @pytest.mark.asyncio
    async def test_user_profile_relationship(self, db_session):
        """測試 User 與 Profile 的關聯

        此測試驗證：
        1. Foreign key constraint 正常運作
        2. 可以建立關聯資料
        3. 可以透過 JOIN 查詢關聯資料
        """
        # 建立用戶
        user_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """
            ),
            {
                "id": user_id,
                "google_id": "relation_test_user",
                "email": "relation@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()

        # 建立個人檔案
        profile_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO profiles (id, user_id, nickname)
                VALUES (:id, :user_id, :nickname)
                RETURNING id
            """
            ),
            {"id": profile_id, "user_id": user_id, "nickname": "RelationTest"},
        )
        _profile_id = result.scalar()
        await db_session.commit()

        # 透過 JOIN 查詢驗證關聯
        result = await db_session.execute(
            text(
                """
                SELECT u.email, p.nickname
                FROM users u
                JOIN profiles p ON u.id = p.user_id
                WHERE u.id = :user_id
            """
            ),
            {"user_id": user_id},
        )
        row = result.fetchone()

        assert row is not None
        assert row[0] == "relation@test.com"
        assert row[1] == "RelationTest"

    @pytest.mark.asyncio
    async def test_cascade_delete(self, db_session):
        """測試級聯刪除 (如果有設定的話)

        此測試驗證當刪除父記錄時，子記錄是否會被自動刪除
        (取決於資料庫 schema 中的 ON DELETE CASCADE 設定)
        """
        # 建立用戶與個人檔案
        user_id = str(uuid4())
        result = await db_session.execute(
            text(
                """
                INSERT INTO users (id, google_id, email, role)
                VALUES (:id, :google_id, :email, :role)
                RETURNING id
            """
            ),
            {
                "id": user_id,
                "google_id": "cascade_test",
                "email": "cascade@test.com",
                "role": "user",
            },
        )
        user_id = result.scalar()
        await db_session.commit()

        profile_id = str(uuid4())
        await db_session.execute(
            text(
                """
                INSERT INTO profiles (id, user_id, nickname)
                VALUES (:id, :user_id, :nickname)
            """
            ),
            {"id": profile_id, "user_id": user_id, "nickname": "CascadeTest"},
        )
        await db_session.commit()

        # 刪除用戶
        await db_session.execute(
            text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id}
        )
        await db_session.commit()

        # 檢查個人檔案是否也被刪除
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM profiles WHERE user_id = :user_id"),
            {"user_id": user_id},
        )
        count = result.scalar()

        # 如果設定了 CASCADE，count 應該是 0
        # 如果沒有設定，上面的 DELETE 會失敗（foreign key constraint）
        assert count == 0, "Profile 應該因為 CASCADE 被刪除"


# 提示：你可以複製這些範例並修改為你自己的測試
# 記得移除 @pytest.mark.skip 裝飾器來啟用測試
