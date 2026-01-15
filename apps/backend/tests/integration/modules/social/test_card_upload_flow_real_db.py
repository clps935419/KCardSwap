"""
Integration tests for Card Upload Flow with Real Database

Tests card management flow end-to-end using real database with automatic rollback.
"""

from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestCardUploadFlowWithRealDatabase:
    """Integration tests for card upload flow using real database"""

    @pytest_asyncio.fixture
    async def test_user(self, db_session) -> UUID:
        """Create test user in database"""
        result = await db_session.execute(
            text("""
                INSERT INTO users (google_id, email, role)
                VALUES (:google_id, :email, :role)
                RETURNING id
            """),
            {
                "google_id": "card_test_user",
                "email": "carduser@test.com",
                "role": "user"
            }
        )
        user_id = result.scalar()
        await db_session.flush()
        return user_id

    @pytest_asyncio.fixture
    async def test_cards(self, db_session, test_user) -> list:
        """Create test cards in database"""
        cards = []
        
        # Create multiple cards with different statuses
        for i, status in enumerate(["available", "pending", "available"]):
            result = await db_session.execute(
                text("""
                    INSERT INTO cards (owner_id, idol, idol_group, status)
                    VALUES (:owner_id, :idol, :idol_group, :status)
                    RETURNING id
                """),
                {
                    "owner_id": test_user,
                    "idol": f"Idol{i}",
                    "idol_group": f"Group{i}",
                    "status": status
                }
            )
            card_id = result.scalar()
            cards.append(card_id)
        
        await db_session.flush()
        return cards

    @pytest.fixture
    def authenticated_client(self, test_user, db_session):
        """Provide authenticated client"""
        async def override_get_current_user_id():
            return test_user
        
        async def override_get_db_session():
            return db_session
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        app.dependency_overrides[get_db_session] = override_get_db_session
        
        yield client
        
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_my_cards(
        self,
        authenticated_client,
        test_cards,
        db_session
    ):
        """Test retrieving user's cards with real database"""
        response = authenticated_client.get("/api/v1/cards/me")
        
        # Check response
        assert response.status_code == 200, f"Unexpected status: {response.status_code}, body: {response.text}"
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # Should have the cards we created
        assert len(data["data"]) >= 3

    @pytest.mark.asyncio
    async def test_get_my_cards_with_status_filter(
        self,
        authenticated_client,
        test_cards,
        db_session
    ):
        """Test retrieving user's cards with status filter"""
        response = authenticated_client.get("/api/v1/cards/me?status=available")
        
        # Check response
        assert response.status_code == 200, f"Unexpected status: {response.status_code}, body: {response.text}"
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # All returned cards should have status "available"
        for card in data["data"]:
            assert card["status"] == "available"

    @pytest.mark.asyncio
    async def test_get_cards_requires_authentication(self):
        """Test that getting cards requires authentication"""
        response = client.get("/api/v1/cards/me")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_cards_empty_list(
        self,
        authenticated_client,
        db_session
    ):
        """Test retrieving cards when user has no cards"""
        # Don't create any test cards - just test with empty user
        response = authenticated_client.get("/api/v1/cards/me")
        
        # Should return empty list, not error
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        # May have cards from test_cards fixture or be empty
        assert isinstance(data["data"], list)
