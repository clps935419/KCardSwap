"""
Unit tests for Friends Router - Unblock Endpoint Response

Tests specifically focused on the unblock endpoint response validation
to ensure the FriendshipResponse schema works correctly with created_at=None
"""

from datetime import datetime
from uuid import uuid4

from app.modules.social.presentation.schemas.friends_schemas import (
    FriendshipResponse,
    FriendshipResponseWrapper,
)


class TestUnblockUserResponse:
    """Test unblock user endpoint response construction"""

    def test_friendship_response_with_created_at(self):
        """Test FriendshipResponse can be created with created_at"""
        # Arrange
        user_id = uuid4()
        friend_id = uuid4()
        friendship_id = uuid4()
        created_at = datetime.utcnow()

        # Act
        response = FriendshipResponse(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status="accepted",
            created_at=created_at,
        )

        # Assert
        assert response.id == friendship_id
        assert response.user_id == user_id
        assert response.friend_id == friend_id
        assert response.status == "accepted"
        assert response.created_at == created_at

    def test_friendship_response_with_none_created_at(self):
        """Test FriendshipResponse can be created with created_at=None (for unblocked status)"""
        # Arrange
        user_id = uuid4()
        friend_id = uuid4()
        friendship_id = uuid4()

        # Act
        response = FriendshipResponse(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status="unblocked",
            created_at=None,
        )

        # Assert
        assert response.id == friendship_id
        assert response.user_id == user_id
        assert response.friend_id == friend_id
        assert response.status == "unblocked"
        assert response.created_at is None

    def test_friendship_response_wrapper_with_none_created_at(self):
        """Test FriendshipResponseWrapper can wrap a response with created_at=None"""
        # Arrange
        user_id = uuid4()
        friend_id = uuid4()
        friendship_id = uuid4()

        data = FriendshipResponse(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status="unblocked",
            created_at=None,
        )

        # Act
        wrapper = FriendshipResponseWrapper(data=data, meta=None, error=None)

        # Assert
        assert wrapper.data.id == friendship_id
        assert wrapper.data.status == "unblocked"
        assert wrapper.data.created_at is None
        assert wrapper.meta is None
        assert wrapper.error is None

    def test_friendship_response_serialization_with_none(self):
        """Test FriendshipResponse can be serialized to dict with created_at=None"""
        # Arrange
        user_id = uuid4()
        friend_id = uuid4()
        friendship_id = uuid4()

        response = FriendshipResponse(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status="unblocked",
            created_at=None,
        )

        # Act
        data_dict = response.model_dump()

        # Assert
        assert data_dict["id"] == friendship_id
        assert data_dict["user_id"] == user_id
        assert data_dict["friend_id"] == friend_id
        assert data_dict["status"] == "unblocked"
        assert data_dict["created_at"] is None

    def test_friendship_response_json_serialization_with_none(self):
        """Test FriendshipResponse can be serialized to JSON with created_at=None"""
        # Arrange
        user_id = uuid4()
        friend_id = uuid4()
        friendship_id = uuid4()

        response = FriendshipResponse(
            id=friendship_id,
            user_id=user_id,
            friend_id=friend_id,
            status="unblocked",
            created_at=None,
        )

        # Act
        json_str = response.model_dump_json()

        # Assert
        assert json_str is not None
        assert "unblocked" in json_str
        assert "null" in json_str  # created_at should be serialized as null
