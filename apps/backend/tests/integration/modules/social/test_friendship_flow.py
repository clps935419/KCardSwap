"""
Integration tests for Friendship Flow

Tests the complete friendship flow end-to-end including:
1. Sending friend requests
2. Accepting friend requests
3. Rejecting friend requests
4. Getting friends list
5. Removing friends
6. Blocking users
7. Unblocking users
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.modules.social.domain.entities.friendship import Friendship, FriendshipStatus
from app.shared.presentation.dependencies.auth import get_current_user_id
from app.shared.infrastructure.database.connection import get_db_session

client = TestClient(app)


class TestFriendshipFlowIntegration:
    """Integration tests for friendship flow"""

    @pytest.fixture
    def test_user_ids(self):
        """Generate test user IDs"""
        return {
            "user1": uuid4(),
            "user2": uuid4(),
            "user3": uuid4(),
        }

    @pytest.fixture
    def test_pending_friendship(self, test_user_ids):
        """Generate test pending friendship"""
        return Friendship(
            id=str(uuid4()),
            user_id=str(test_user_ids["user1"]),
            friend_id=str(test_user_ids["user2"]),
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def test_accepted_friendship(self, test_user_ids):
        """Generate test accepted friendship"""
        return Friendship(
            id=str(uuid4()),
            user_id=str(test_user_ids["user1"]),
            friend_id=str(test_user_ids["user2"]),
            status=FriendshipStatus.ACCEPTED,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def test_blocked_friendship(self, test_user_ids):
        """Generate test blocked friendship"""
        return Friendship(
            id=str(uuid4()),
            user_id=str(test_user_ids["user1"]),
            friend_id=str(test_user_ids["user3"]),
            status=FriendshipStatus.BLOCKED,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def mock_auth_user1(self, test_user_ids):
        """Mock authentication for user1 using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_ids["user1"]
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_ids["user1"]
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_auth_user2(self, test_user_ids):
        """Mock authentication for user2 using dependency override"""
        async def override_get_current_user_id() -> UUID:
            return test_user_ids["user2"]
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id
        yield test_user_ids["user2"]
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session using dependency override"""
        mock_session = Mock()
        
        async def override_get_db_session():
            return mock_session
        
        app.dependency_overrides[get_db_session] = override_get_db_session
        yield mock_session
        # Clear this specific override only if it's still set
        if get_db_session in app.dependency_overrides:
            del app.dependency_overrides[get_db_session]

    # ==================== Send Friend Request Tests ====================
    
    @pytest.mark.asyncio
    async def test_send_friend_request_success(
        self, mock_auth_user1, mock_db_session, test_user_ids
    ):
        """Test successfully sending a friend request"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            with patch.object(
                FriendshipRepositoryImpl, "create", new_callable=AsyncMock
            ) as mock_create:
                with patch.object(
                    FriendshipRepositoryImpl, "is_blocked", new_callable=AsyncMock
                ) as mock_is_blocked:
                    mock_get.return_value = None  # No existing friendship
                    mock_is_blocked.return_value = False  # Not blocked

                    def create_side_effect(friendship):
                        return friendship

                    mock_create.side_effect = create_side_effect

                    # Act - NOTE: endpoint is /request (singular), payload field is target_user_id
                    response = client.post(
                        "/api/v1/friends/request",
                        json={"target_user_id": str(test_user_ids["user2"])},
                    )

                    # Assert
                    assert response.status_code == status.HTTP_201_CREATED
                    data = response.json()
                    assert "data" in data
                    assert data["data"]["friend_id"] == str(test_user_ids["user2"])
                    assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_send_friend_request_to_self_fails(
        self, mock_auth_user1, mock_db_session, test_user_ids
    ):
        """Test cannot send friend request to yourself"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            # Act
            response = client.post(
                "/api/v1/friends/request",
                json={"target_user_id": str(test_user_ids["user1"])},  # Same as current user
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_send_friend_request_already_friends(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_accepted_friendship
    ):
        """Test cannot send friend request if already friends"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = test_accepted_friendship

            # Act
            response = client.post(
                "/api/v1/friends/request",
                json={"target_user_id": str(test_user_ids["user2"])},
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_send_friend_request_already_pending(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_pending_friendship
    ):
        """Test cannot send friend request if pending request exists"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = test_pending_friendship

            # Act
            response = client.post(
                "/api/v1/friends/request",
                json={"target_user_id": str(test_user_ids["user2"])},
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_send_friend_request_user_blocked(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_blocked_friendship
    ):
        """Test cannot send friend request if user is blocked"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            # User has blocked the target
            mock_get.return_value = test_blocked_friendship

            # Act
            response = client.post(
                "/api/v1/friends/request",
                json={"target_user_id": str(test_user_ids["user3"])},
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # ==================== Accept Friend Request Tests ====================

    @pytest.mark.asyncio
    async def test_accept_friend_request_success(
        self, mock_auth_user2, mock_db_session, test_user_ids, test_pending_friendship
    ):
        """Test successfully accepting a friend request"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )
        from app.modules.social.infrastructure.repositories.chat_room_repository_impl import (
            ChatRoomRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            with patch.object(
                FriendshipRepositoryImpl, "update", new_callable=AsyncMock
            ) as mock_update:
                with patch.object(
                    ChatRoomRepositoryImpl, "get_by_participants", new_callable=AsyncMock
                ) as mock_get_room:
                    with patch.object(
                        ChatRoomRepositoryImpl, "create", new_callable=AsyncMock
                    ) as mock_create_room:
                        mock_get.return_value = test_pending_friendship
                        mock_get_room.return_value = None  # No existing chat room

                        def update_side_effect(friendship):
                            return friendship

                        mock_update.side_effect = update_side_effect

                        # Act - NOTE: endpoint is /{friendship_id}/accept
                        response = client.post(
                            f"/api/v1/friends/{test_pending_friendship.id}/accept"
                        )

                        # Assert
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert "data" in data
                        assert data["data"]["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_accept_friend_request_not_found(
        self, mock_auth_user2, mock_db_session, test_user_ids
    ):
        """Test accepting non-existent friend request"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        fake_id = str(uuid4())
        with patch.object(
            FriendshipRepositoryImpl, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            # Act
            response = client.post(f"/api/v1/friends/{fake_id}/accept")

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_accept_friend_request_not_recipient(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_pending_friendship
    ):
        """Test only recipient can accept friend request"""
        # Arrange - user1 tries to accept but user2 is the recipient
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = test_pending_friendship

            # Act
            response = client.post(
                f"/api/v1/friends/{test_pending_friendship.id}/accept"
            )

            # Assert
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_accept_friend_request_not_pending(
        self, mock_auth_user2, mock_db_session, test_user_ids, test_accepted_friendship
    ):
        """Test cannot accept already accepted request"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = test_accepted_friendship

            # Act
            response = client.post(
                f"/api/v1/friends/{test_accepted_friendship.id}/accept"
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # ==================== Get Friends List Tests ====================

    @pytest.mark.asyncio
    async def test_get_friends_list_success(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_accepted_friendship
    ):
        """Test successfully getting friends list"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "find_by_user_and_status", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = [test_accepted_friendship]

            # Act
            response = client.get("/api/v1/friends")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "data" in data
            assert "friends" in data["data"]
            assert len(data["data"]["friends"]) == 1

    @pytest.mark.asyncio
    async def test_get_friends_filter_by_pending(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_pending_friendship
    ):
        """Test getting friends list filtered by pending status"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "find_by_user_and_status", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = [test_pending_friendship]

            # Act
            response = client.get("/api/v1/friends?status=pending")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "data" in data
            assert "friends" in data["data"]

    @pytest.mark.asyncio
    async def test_get_friends_filter_by_blocked(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_blocked_friendship
    ):
        """Test getting friends list filtered by blocked status"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "find_by_user_and_status", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = [test_blocked_friendship]

            # Act
            response = client.get("/api/v1/friends?status=blocked")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "data" in data
            assert "friends" in data["data"]

    # ==================== Block User Tests ====================

    @pytest.mark.asyncio
    async def test_block_user_success(
        self, mock_auth_user1, mock_db_session, test_user_ids
    ):
        """Test successfully blocking a user"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            with patch.object(
                FriendshipRepositoryImpl, "create", new_callable=AsyncMock
            ) as mock_create:
                mock_get.return_value = None

                def create_side_effect(friendship):
                    return friendship

                mock_create.side_effect = create_side_effect

                # Act
                response = client.post(
                    "/api/v1/friends/block",
                    json={"user_id": str(test_user_ids["user3"])},
                )

                # Assert
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["data"]["status"] == "blocked"

    @pytest.mark.asyncio
    async def test_block_user_self_fails(
        self, mock_auth_user1, mock_db_session, test_user_ids
    ):
        """Test cannot block yourself"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            # Act
            response = client.post(
                "/api/v1/friends/block",
                json={"user_id": str(test_user_ids["user1"])},  # Same as current user
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_block_user_already_blocked(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_blocked_friendship
    ):
        """Test blocking already blocked user (should succeed idempotently)"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            with patch.object(
                FriendshipRepositoryImpl, "update", new_callable=AsyncMock
            ) as mock_update:
                mock_get.return_value = test_blocked_friendship

                def update_side_effect(friendship):
                    return friendship

                mock_update.side_effect = update_side_effect

                # Act
                response = client.post(
                    "/api/v1/friends/block",
                    json={"user_id": str(test_user_ids["user3"])},
                )

                # Assert - blocking already blocked user should succeed (idempotent)
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["data"]["status"] == "blocked"

    # ==================== Unblock User Tests ====================

    @pytest.mark.asyncio
    async def test_unblock_user_success(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_blocked_friendship
    ):
        """Test successfully unblocking a user"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            with patch.object(
                FriendshipRepositoryImpl, "delete", new_callable=AsyncMock
            ) as mock_delete:
                mock_get.return_value = test_blocked_friendship
                mock_delete.return_value = None

                # Act
                response = client.post(
                    "/api/v1/friends/unblock",
                    json={"user_id": str(test_user_ids["user3"])},
                )

                # Assert
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "data" in data
                assert data["data"]["status"] == "unblocked"
                assert data["data"]["user_id"] == str(test_user_ids["user1"])
                assert data["data"]["friend_id"] == str(test_user_ids["user3"])
                # created_at should be None for unblocked status (the fix we made)
                assert data["data"]["created_at"] is None

    @pytest.mark.asyncio
    async def test_unblock_user_no_relationship(
        self, mock_auth_user1, mock_db_session, test_user_ids
    ):
        """Test unblocking when no relationship exists"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            # Act
            response = client.post(
                "/api/v1/friends/unblock",
                json={"user_id": str(test_user_ids["user3"])},
            )

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_unblock_user_not_blocked(
        self, mock_auth_user1, mock_db_session, test_user_ids, test_accepted_friendship
    ):
        """Test unblocking when relationship is not blocked"""
        # Arrange
        from app.modules.social.infrastructure.repositories.friendship_repository_impl import (
            FriendshipRepositoryImpl,
        )

        with patch.object(
            FriendshipRepositoryImpl, "get_by_users", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = test_accepted_friendship

            # Act
            response = client.post(
                "/api/v1/friends/unblock",
                json={"user_id": str(test_user_ids["user2"])},
            )

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
