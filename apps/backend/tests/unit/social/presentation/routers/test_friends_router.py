"""
Unit tests for Friends Router

Tests the friends router endpoints:
- POST /friends/block - Block a user
- POST /friends/unblock - Unblock a user
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException


class TestFriendsRouter:
    """Test cases for Friends Router endpoints"""

    @pytest.fixture
    def mock_friendship_repo(self):
        """Mock friendship repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_block_use_case(self):
        """Mock block user use case"""
        return AsyncMock()

    @pytest.fixture
    def mock_unblock_use_case(self):
        """Mock unblock user use case"""
        return AsyncMock()

    @pytest.fixture
    def current_user_id(self):
        """Current authenticated user ID"""
        return uuid4()

    @pytest.fixture
    def target_user_id(self):
        """Target user ID to block/unblock"""
        return uuid4()

    # Block User Tests

    @pytest.mark.asyncio
    async def test_block_user_success(
        self, mock_block_use_case, current_user_id, target_user_id
    ):
        """Test successfully blocking a user"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import block_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            BlockUserRequest,
        )

        request = BlockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_block_use_case.execute.return_value = None

        # Act
        with patch(
            "app.modules.social.presentation.routers.friends_router.BlockUserUseCase",
            return_value=mock_block_use_case,
        ):
            result = await block_user(
                request=request,
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result == {"message": "User blocked successfully", "error": None}
        mock_block_use_case.execute.assert_called_once_with(
            blocker_user_id=str(current_user_id),
            blocked_user_id=str(target_user_id),
        )

    @pytest.mark.asyncio
    async def test_block_user_validation_error(
        self, mock_block_use_case, current_user_id, target_user_id
    ):
        """Test blocking user with validation error"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import block_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            BlockUserRequest,
        )

        request = BlockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_block_use_case.execute.side_effect = ValueError("Cannot block yourself")

        # Act & Assert
        with patch(
            "app.modules.social.presentation.routers.friends_router.BlockUserUseCase",
            return_value=mock_block_use_case,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await block_user(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 400
            assert "Cannot block yourself" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_block_user_internal_error(
        self, mock_block_use_case, current_user_id, target_user_id
    ):
        """Test blocking user with internal server error"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import block_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            BlockUserRequest,
        )

        request = BlockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_block_use_case.execute.side_effect = Exception("Database error")

        # Act & Assert
        with patch(
            "app.modules.social.presentation.routers.friends_router.BlockUserUseCase",
            return_value=mock_block_use_case,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await block_user(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to block user" in str(exc_info.value.detail)

    # Unblock User Tests

    @pytest.mark.asyncio
    async def test_unblock_user_success(
        self, mock_unblock_use_case, current_user_id, target_user_id
    ):
        """Test successfully unblocking a user"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import unblock_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            UnblockUserRequest,
        )

        request = UnblockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_unblock_use_case.execute.return_value = None

        # Act
        with patch(
            "app.modules.social.presentation.routers.friends_router.UnblockUserUseCase",
            return_value=mock_unblock_use_case,
        ):
            result = await unblock_user(
                request=request,
                current_user_id=current_user_id,
                session=mock_session,
            )

        # Assert
        assert result == {"message": "User unblocked successfully", "error": None}
        mock_unblock_use_case.execute.assert_called_once_with(
            unblocker_user_id=str(current_user_id),
            unblocked_user_id=str(target_user_id),
        )

    @pytest.mark.asyncio
    async def test_unblock_user_validation_error(
        self, mock_unblock_use_case, current_user_id, target_user_id
    ):
        """Test unblocking user with validation error"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import unblock_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            UnblockUserRequest,
        )

        request = UnblockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_unblock_use_case.execute.side_effect = ValueError("User not blocked")

        # Act & Assert
        with patch(
            "app.modules.social.presentation.routers.friends_router.UnblockUserUseCase",
            return_value=mock_unblock_use_case,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await unblock_user(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 400
            assert "User not blocked" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_unblock_user_internal_error(
        self, mock_unblock_use_case, current_user_id, target_user_id
    ):
        """Test unblocking user with internal server error"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import unblock_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            UnblockUserRequest,
        )

        request = UnblockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_unblock_use_case.execute.side_effect = Exception("Database error")

        # Act & Assert
        with patch(
            "app.modules.social.presentation.routers.friends_router.UnblockUserUseCase",
            return_value=mock_unblock_use_case,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await unblock_user(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

            assert exc_info.value.status_code == 500
            assert "Failed to unblock user" in str(exc_info.value.detail)

    # Edge Cases

    @pytest.mark.asyncio
    async def test_block_user_creates_repository_correctly(
        self, mock_block_use_case, current_user_id, target_user_id
    ):
        """Test that block_user creates repository with correct session"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import block_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            BlockUserRequest,
        )

        request = BlockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_block_use_case.execute.return_value = None
        mock_repo_class = AsyncMock()

        # Act
        with patch(
            "app.modules.social.presentation.routers.friends_router.BlockUserUseCase",
            return_value=mock_block_use_case,
        ):
            with patch(
                "app.modules.social.presentation.routers.friends_router.FriendshipRepositoryImpl",
                mock_repo_class,
            ):
                await block_user(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

        # Assert
        mock_repo_class.assert_called_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_unblock_user_creates_repository_correctly(
        self, mock_unblock_use_case, current_user_id, target_user_id
    ):
        """Test that unblock_user creates repository with correct session"""
        # Arrange
        from app.modules.social.presentation.routers.friends_router import unblock_user
        from app.modules.social.presentation.schemas.friends_schemas import (
            UnblockUserRequest,
        )

        request = UnblockUserRequest(user_id=target_user_id)
        mock_session = AsyncMock()

        mock_unblock_use_case.execute.return_value = None
        mock_repo_class = AsyncMock()

        # Act
        with patch(
            "app.modules.social.presentation.routers.friends_router.UnblockUserUseCase",
            return_value=mock_unblock_use_case,
        ):
            with patch(
                "app.modules.social.presentation.routers.friends_router.FriendshipRepositoryImpl",
                mock_repo_class,
            ):
                await unblock_user(
                    request=request,
                    current_user_id=current_user_id,
                    session=mock_session,
                )

        # Assert
        mock_repo_class.assert_called_once_with(mock_session)
