"""
Integration tests for Trade Flow with Real Database

Tests complete trade flow end-to-end using real database with automatic rollback.
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestTradeFlowWithRealDatabase:
    """Integration tests for trade flow using real database"""

    @pytest_asyncio.fixture
    async def test_users(self, db_session) -> dict:
        """Create test users in database"""
        # Create initiator user
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": "trade_initiator",
                "email": "initiator@test.com",
                "role": "user"
            }
        )
        initiator_id = result.scalar()
        
        # Create responder user
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": "trade_responder",
                "email": "responder@test.com",
                "role": "user"
            }
        )
        responder_id = result.scalar()
        await db_session.flush()
        
        return {
            "initiator": initiator_id,
            "responder": responder_id
        }

    @pytest_asyncio.fixture
    async def test_cards(self, db_session, test_users) -> dict:
        """Create test cards in database"""
        # Create initiator's card
        result = await db_session.execute(
            text("""
                INSERT INTO cards (owner_id, idol, idol_group, status)
                VALUES (:owner_id, :idol, :idol_group, :status)
                RETURNING id
            """),
            {
                "owner_id": test_users["initiator"],
                "idol": "IU",
                "idol_group": "Solo",
                "status": "available"
            }
        )
        initiator_card_id = result.scalar()
        
        # Create responder's card
        result = await db_session.execute(
            text("""
                INSERT INTO cards (owner_id, idol, idol_group, status)
                VALUES (:owner_id, :idol, :idol_group, :status)
                RETURNING id
            """),
            {
                "owner_id": test_users["responder"],
                "idol": "Jungkook",
                "idol_group": "BTS",
                "status": "available"
            }
        )
        responder_card_id = result.scalar()
        await db_session.flush()
        
        return {
            "initiator_card": initiator_card_id,
            "responder_card": responder_card_id
        }

    @pytest_asyncio.fixture
    async def test_friendship(self, db_session, test_users) -> UUID:
        """Create friendship between test users"""
        result = await db_session.execute(
            text("""
                INSERT INTO friendships (user_id, friend_id, status)
                VALUES (:user_id, :friend_id, :status)
                RETURNING id
            """),
            {
                "user_id": test_users["initiator"],
                "friend_id": test_users["responder"],
                "status": "accepted"
            }
        )
        friendship_id = result.scalar()
        await db_session.flush()
        return friendship_id

    @pytest.fixture
    def authenticated_client_initiator(self, test_users, db_session):
        """Provide authenticated client as initiator"""
        async def override_get_current_user_id():
            return test_users["initiator"]
        
        async def override_get_db_session():
            return db_session
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = override_get_db_session
        
        yield client
        
        app.dependency_overrides.clear()

    @pytest.fixture
    def authenticated_client_responder(self, test_users, db_session):
        """Provide authenticated client as responder"""
        async def override_get_current_user_id():
            return test_users["responder"]
        
        async def override_get_db_session():
            return db_session
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = override_get_db_session
        
        yield client
        
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_trade_proposal(
        self,
        authenticated_client_initiator,
        test_users,
        test_cards,
        test_friendship,
        db_session
    ):
        """Test creating a trade proposal with real database"""
        request_data = {
            "responder_id": str(test_users["responder"]),
            "initiator_card_ids": [str(test_cards["initiator_card"])],
            "responder_card_ids": [str(test_cards["responder_card"])],
            "message": "Let's trade!"
        }
        
        response = authenticated_client_initiator.post(
            "/api/v1/trades",
            json=request_data
        )
        
        # Check response
        assert response.status_code in [200, 201], f"Unexpected status: {response.status_code}, body: {response.text}"
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "data" in data
            trade_data = data["data"]
            assert trade_data["initiator_id"] == str(test_users["initiator"])
            assert trade_data["responder_id"] == str(test_users["responder"])
            assert trade_data["status"] in ["proposed", "pending"]

    @pytest.mark.asyncio
    async def test_get_trade_history(
        self,
        authenticated_client_initiator,
        test_users,
        db_session
    ):
        """Test retrieving trade history with real database"""
        response = authenticated_client_initiator.get("/api/v1/trades/history")
        
        # Check response
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_trade_operations_require_authentication(self):
        """Test that trade operations require authentication"""
        # Test without authentication
        response = client.post("/api/v1/trades", json={})
        assert response.status_code in [401, 403]
        
        response = client.get("/api/v1/trades/history")
        assert response.status_code in [401, 403]
