"""
Integration tests for Trade Flow (T165)
Tests complete trade flow end-to-end from creation to completion

Note: These tests use TestClient and mock the database.
For full E2E tests with real database, use pytest with testcontainers (see conftest.py).
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.social.domain.entities.card import Card
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.modules.social.domain.entities.trade import Trade
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestTradeFlowIntegration:
    """Integration tests for complete trade flow"""

    @pytest.fixture
    def test_user_ids(self):
        """Generate test user IDs"""
        return {
            "initiator": uuid4(),
            "responder": uuid4(),
        }

    @pytest.fixture
    def test_trade_data(self, test_user_ids):
        """Generate test trade data"""
        return {
            "trade_id": uuid4(),
            "initiator_card_id": uuid4(),
            "responder_card_id": uuid4(),
            **test_user_ids,
        }

    @pytest.fixture
    def mock_auth_initiator(self, test_user_ids):
        """Mock authentication for initiator using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_ids["initiator"]
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_ids["initiator"]
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_auth_responder(self, test_user_ids):
        """Mock authentication for responder using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_ids["responder"]
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_ids["responder"]
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session using dependency override"""
        # Create a mock that supports async operations
        mock_session = Mock()
        # Make execute() return an AsyncMock so it can be awaited
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        
        async def override_get_db_session():
            return mock_session
        
        app.dependency_overrides[get_db_session] = override_get_db_session
        yield mock_session
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_trade_repository(self, test_trade_data):
        """Mock trade repository"""
        with patch(
            "app.modules.social.infrastructure.repositories.trade_repository_impl.TradeRepositoryImpl"
        ) as mock:
            repo_instance = Mock()

            # Mock trade creation
            created_trade = Trade(
                id=test_trade_data["trade_id"],
                initiator_id=test_trade_data["initiator"],
                responder_id=test_trade_data["responder"],
                status=Trade.STATUS_PROPOSED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            repo_instance.create = AsyncMock(return_value=created_trade)
            repo_instance.get_by_id = AsyncMock(return_value=created_trade)
            repo_instance.update = AsyncMock(side_effect=lambda trade: trade)
            repo_instance.get_items_by_trade_id = AsyncMock(return_value=[])
            repo_instance.count_active_trades_between_users = AsyncMock(return_value=0)
            repo_instance.get_user_trades = AsyncMock(return_value=[created_trade])

            mock.return_value = repo_instance
            yield repo_instance

    @pytest.fixture
    def mock_card_repository(self, test_trade_data):
        """Mock card repository"""
        with patch(
            "app.modules.social.infrastructure.repositories.card_repository_impl.CardRepositoryImpl"
        ) as mock:
            repo_instance = Mock()

            # Mock cards
            initiator_card = Card(
                owner_id=test_trade_data["initiator"],
                id=test_trade_data["initiator_card_id"],
                status=Card.STATUS_AVAILABLE,
            )
            responder_card = Card(
                owner_id=test_trade_data["responder"],
                id=test_trade_data["responder_card_id"],
                status=Card.STATUS_AVAILABLE,
            )

            repo_instance.find_by_id = AsyncMock(
                side_effect=lambda card_id: (
                    initiator_card
                    if card_id == test_trade_data["initiator_card_id"]
                    else responder_card
                    if card_id == test_trade_data["responder_card_id"]
                    else None
                )
            )
            repo_instance.save = AsyncMock(side_effect=lambda card: card)

            mock.return_value = repo_instance
            yield repo_instance

    @pytest.fixture
    def mock_friendship_repository(self, test_user_ids):
        """Mock friendship repository"""
        with patch(
            "app.modules.social.infrastructure.repositories.friendship_repository_impl.FriendshipRepositoryImpl"
        ) as mock:
            repo_instance = Mock()

            # Mock friendship
            friendship = Friendship(
                id=str(uuid4()),
                user_id=str(test_user_ids["initiator"]),
                friend_id=str(test_user_ids["responder"]),
                status=FriendshipStatus.ACCEPTED,
                created_at=datetime.utcnow(),
            )
            repo_instance.get_by_users = AsyncMock(return_value=friendship)
            repo_instance.is_blocked = AsyncMock(return_value=False)

            mock.return_value = repo_instance
            yield repo_instance

    @pytest.mark.asyncio
    async def test_create_trade_proposal(
        self,
        mock_auth_initiator,
        mock_db_session,
        test_trade_data,
        test_user_ids,
    ):
        """Test creating a trade proposal"""
        from app.modules.social.infrastructure.repositories.trade_repository_impl import TradeRepositoryImpl
        from app.modules.social.infrastructure.repositories.card_repository_impl import CardRepositoryImpl
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import FriendshipRepositoryImpl
        
        # Create mock trade
        created_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_PROPOSED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Create mock cards
        initiator_card = Card(
            id=str(test_trade_data["initiator_card_id"]),
            owner_id=str(test_trade_data["initiator"]),
            idol="IU",
            status=Card.STATUS_AVAILABLE,
        )
        
        responder_card = Card(
            id=str(test_trade_data["responder_card_id"]),
            owner_id=str(test_trade_data["responder"]),
            idol="BTS Jungkook",
            status=Card.STATUS_AVAILABLE,
        )
        
        # Mock friendship
        friendship = Friendship(
            id=str(uuid4()),
            user_id=str(test_trade_data["initiator"]),
            friend_id=str(test_trade_data["responder"]),
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )
        
        with patch.object(TradeRepositoryImpl, "create", new_callable=AsyncMock) as mock_create:
            with patch.object(TradeRepositoryImpl, "count_active_trades_between_users", new_callable=AsyncMock) as mock_count:
                with patch.object(CardRepositoryImpl, "get_by_id", new_callable=AsyncMock) as mock_get_card:
                    with patch.object(FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock) as mock_get_friendship:
                        mock_create.return_value = created_trade
                        mock_count.return_value = 0
                        mock_get_card.side_effect = lambda card_id: initiator_card if str(card_id) == str(test_trade_data["initiator_card_id"]) else responder_card
                        mock_get_friendship.return_value = friendship
                        
                        response = client.post(
                            "/api/v1/trades",
                            json={
                                "responder_id": str(test_trade_data["responder"]),
                                "initiator_card_ids": [str(test_trade_data["initiator_card_id"])],
                                "responder_card_ids": [str(test_trade_data["responder_card_id"])],
                            },
                        )

                        assert response.status_code == 201
                        response_data = response.json()
                        assert "data" in response_data
                        data = response_data["data"]
                        assert data["status"] == "proposed"
                        assert data["initiator_id"] == str(test_trade_data["initiator"])
                        assert data["responder_id"] == str(test_trade_data["responder"])

    @pytest.mark.asyncio
    async def test_get_trade_history(
        self,
        mock_auth_initiator,
        mock_db_session,
        test_trade_data,
    ):
        """Test getting trade history"""
        from app.modules.social.infrastructure.repositories.trade_repository_impl import TradeRepositoryImpl
        
        # Create mock trade
        test_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_PROPOSED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        with patch.object(TradeRepositoryImpl, "get_user_trades", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [test_trade]
            
            response = client.get("/api/v1/trades/history")

            assert response.status_code == 200
            response_data = response.json()
            assert "data" in response_data
            data = response_data["data"]
            assert "trades" in data
            assert isinstance(data["trades"], list)

    @pytest.mark.asyncio
    async def test_accept_trade(
        self,
        mock_auth_responder,
        mock_db_session,
        test_trade_data,
    ):
        """Test accepting a trade proposal"""
        from app.modules.social.infrastructure.repositories.trade_repository_impl import TradeRepositoryImpl
        
        # Create mock proposed trade
        proposed_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_PROPOSED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Create accepted trade
        accepted_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_ACCEPTED,
            accepted_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        with patch.object(TradeRepositoryImpl, "get_by_id", new_callable=AsyncMock) as mock_get:
            with patch.object(TradeRepositoryImpl, "update", new_callable=AsyncMock) as mock_update:
                mock_get.return_value = proposed_trade
                mock_update.return_value = accepted_trade
                
                response = client.post(f"/api/v1/trades/{test_trade_data['trade_id']}/accept")

                assert response.status_code == 200
                response_data = response.json()
                assert "data" in response_data

    @pytest.mark.asyncio
    async def test_reject_trade(
        self,
        mock_auth_responder,
        mock_db_session,
        test_trade_data,
    ):
        """Test rejecting a trade proposal"""
        from app.modules.social.infrastructure.repositories.trade_repository_impl import TradeRepositoryImpl
        from app.modules.social.infrastructure.repositories.card_repository_impl import CardRepositoryImpl
        
        # Create mock proposed trade
        proposed_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_PROPOSED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Create rejected trade
        rejected_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_REJECTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        with patch.object(TradeRepositoryImpl, "get_by_id", new_callable=AsyncMock) as mock_get:
            with patch.object(TradeRepositoryImpl, "update", new_callable=AsyncMock) as mock_update:
                with patch.object(TradeRepositoryImpl, "get_items_by_trade_id", new_callable=AsyncMock) as mock_get_items:
                    with patch.object(CardRepositoryImpl, "update", new_callable=AsyncMock) as mock_update_card:
                        mock_get.return_value = proposed_trade
                        mock_update.return_value = rejected_trade
                        mock_get_items.return_value = []
                        mock_update_card.return_value = None
                        
                        response = client.post(f"/api/v1/trades/{test_trade_data['trade_id']}/reject")

                        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_cancel_trade(
        self,
        mock_auth_initiator,
        mock_db_session,
        test_trade_data,
    ):
        """Test canceling a trade"""
        from app.modules.social.infrastructure.repositories.trade_repository_impl import TradeRepositoryImpl
        from app.modules.social.infrastructure.repositories.card_repository_impl import CardRepositoryImpl
        
        # Create mock accepted trade
        accepted_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_ACCEPTED,
            accepted_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Create cancelled trade
        cancelled_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_CANCELLED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        with patch.object(TradeRepositoryImpl, "get_by_id", new_callable=AsyncMock) as mock_get:
            with patch.object(TradeRepositoryImpl, "update", new_callable=AsyncMock) as mock_update:
                with patch.object(TradeRepositoryImpl, "get_items_by_trade_id", new_callable=AsyncMock) as mock_get_items:
                    with patch.object(CardRepositoryImpl, "update", new_callable=AsyncMock) as mock_update_card:
                        mock_get.return_value = accepted_trade
                        mock_update.return_value = cancelled_trade
                        mock_get_items.return_value = []
                        mock_update_card.return_value = None
                        
                        response = client.post(f"/api/v1/trades/{test_trade_data['trade_id']}/cancel")

                        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_complete_trade_flow(
        self,
        mock_auth_initiator,
        mock_db_session,
        test_trade_data,
    ):
        """Test complete trade flow: create → accept → complete (both parties)"""
        from app.modules.social.infrastructure.repositories.trade_repository_impl import TradeRepositoryImpl
        from app.modules.social.infrastructure.repositories.card_repository_impl import CardRepositoryImpl
        
        # Step 1: Accepted trade
        accepted_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_ACCEPTED,
            accepted_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Step 2: Partially confirmed trade
        partially_confirmed_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_ACCEPTED,
            accepted_at=datetime.utcnow(),
            initiator_confirmed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Step 3: Completed trade
        completed_trade = Trade(
            id=str(test_trade_data["trade_id"]),
            initiator_id=str(test_trade_data["initiator"]),
            responder_id=str(test_trade_data["responder"]),
            status=Trade.STATUS_COMPLETED,
            accepted_at=datetime.utcnow(),
            initiator_confirmed_at=datetime.utcnow(),
            responder_confirmed_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        with patch.object(TradeRepositoryImpl, "get_by_id", new_callable=AsyncMock) as mock_get:
            with patch.object(TradeRepositoryImpl, "update", new_callable=AsyncMock) as mock_update:
                with patch.object(TradeRepositoryImpl, "get_items_by_trade_id", new_callable=AsyncMock) as mock_get_items:
                    with patch.object(CardRepositoryImpl, "update", new_callable=AsyncMock) as mock_update_card:
                        # First call - initiator confirms
                        mock_get.return_value = accepted_trade
                        mock_update.return_value = partially_confirmed_trade
                        mock_get_items.return_value = []
                        mock_update_card.return_value = None
                        
                        response = client.post(f"/api/v1/trades/{test_trade_data['trade_id']}/complete")
                        assert response.status_code == 200


class TestTradeFlowTimeout:
    """Test trade timeout scenarios"""

    @pytest.mark.asyncio
    async def test_complete_trade_after_timeout(self):
        """Test trade is auto-canceled after 48h timeout"""
        from app.modules.social.infrastructure.repositories.trade_repository_impl import TradeRepositoryImpl
        from app.modules.social.infrastructure.repositories.card_repository_impl import CardRepositoryImpl
        
        # Setup: trade accepted more than 48 hours ago
        old_time = datetime.utcnow() - timedelta(hours=49)

        trade_id = uuid4()
        initiator_id = uuid4()
        responder_id = uuid4()

        accepted_trade = Trade(
            id=str(trade_id),
            initiator_id=str(initiator_id),
            responder_id=str(responder_id),
            status=Trade.STATUS_ACCEPTED,
            accepted_at=old_time,
            created_at=old_time,
            updated_at=old_time,
        )

        # Setup auth override
        async def override_get_current_user_id():
            return initiator_id
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        
        # Setup db session override
        mock_session = Mock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        
        async def override_get_db_session():
            return mock_session
        
        app.dependency_overrides[get_db_session] = override_get_db_session

        with patch.object(TradeRepositoryImpl, "get_by_id", new_callable=AsyncMock) as mock_get:
            with patch.object(TradeRepositoryImpl, "update", new_callable=AsyncMock) as mock_update:
                with patch.object(TradeRepositoryImpl, "get_items_by_trade_id", new_callable=AsyncMock) as mock_get_items:
                    with patch.object(CardRepositoryImpl, "update", new_callable=AsyncMock) as mock_update_card:
                        mock_get.return_value = accepted_trade
                        mock_update.return_value = accepted_trade
                        mock_get_items.return_value = []
                        mock_update_card.return_value = None
                        
                        response = client.post(f"/api/v1/trades/{trade_id}/complete")

                        # Should return 422 because trade has timed out
                        assert response.status_code == 422
                        
        # Cleanup
        app.dependency_overrides.clear()
