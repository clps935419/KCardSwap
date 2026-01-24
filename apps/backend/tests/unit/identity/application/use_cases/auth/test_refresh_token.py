"""
Unit tests for RefreshTokenUseCase
Testing token refresh logic
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from jose import JWTError

from app.modules.identity.application.use_cases.auth.refresh_token import (
    RefreshTokenUseCase,
)
from app.modules.identity.domain.entities.refresh_token import RefreshToken


class TestRefreshTokenUseCase:
    """Test refresh token use case"""

    @pytest.fixture
    def mock_refresh_token_repo(self):
        """Mock refresh token repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_jwt_service(self):
        """Mock JWT service"""
        return Mock()

    @pytest.fixture
    def use_case(self, mock_refresh_token_repo, mock_jwt_service):
        """Create refresh token use case with mocked dependencies"""
        return RefreshTokenUseCase(
            refresh_token_repo=mock_refresh_token_repo, jwt_service=mock_jwt_service
        )

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test successful token refresh"""
        user_id = uuid4()
        old_refresh_token = "old_refresh_token"
        new_access_token = "new_access_token"
        new_refresh_token = "new_refresh_token"

        # Mock JWT verification
        mock_jwt_service.verify_token.return_value = {
            "sub": str(user_id),
            "email": "user@example.com",
        }

        # Mock token entity
        token_entity = RefreshToken(
            user_id=user_id,
            token=old_refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
        )
        mock_refresh_token_repo.find_by_token.return_value = token_entity
        mock_refresh_token_repo.update.return_value = None
        mock_refresh_token_repo.create.return_value = None

        # Mock new token generation
        mock_jwt_service.create_access_token.return_value = new_access_token
        mock_jwt_service.create_refresh_token.return_value = new_refresh_token

        result = await use_case.execute(old_refresh_token)

        assert result is not None
        assert result[0] == new_access_token
        assert result[1] == new_refresh_token

        # Verify calls
        mock_jwt_service.verify_token.assert_called_once_with(
            old_refresh_token, expected_type="refresh"
        )
        mock_refresh_token_repo.find_by_token.assert_called_once_with(
            old_refresh_token
        )
        mock_refresh_token_repo.update.assert_called_once()
        mock_refresh_token_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_jwt(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test refresh with invalid JWT"""
        invalid_token = "invalid_token"

        mock_jwt_service.verify_token.side_effect = JWTError("Invalid token")

        result = await use_case.execute(invalid_token)

        assert result is None
        mock_jwt_service.verify_token.assert_called_once()
        mock_refresh_token_repo.find_by_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_token_not_found_in_db(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test refresh when token not found in database"""
        user_id = uuid4()
        refresh_token = "token_not_in_db"

        mock_jwt_service.verify_token.return_value = {
            "sub": str(user_id),
            "email": "user@example.com",
        }
        mock_refresh_token_repo.find_by_token.return_value = None

        result = await use_case.execute(refresh_token)

        assert result is None
        mock_refresh_token_repo.update.assert_not_called()
        mock_refresh_token_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_token_revoked(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test refresh with revoked token"""
        user_id = uuid4()
        revoked_token = "revoked_token"

        mock_jwt_service.verify_token.return_value = {
            "sub": str(user_id),
            "email": "user@example.com",
        }

        # Token is revoked
        token_entity = RefreshToken(
            user_id=user_id,
            token=revoked_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=True,
        )
        mock_refresh_token_repo.find_by_token.return_value = token_entity

        result = await use_case.execute(revoked_token)

        assert result is None
        mock_refresh_token_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_token_expired(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test refresh with expired token"""
        user_id = uuid4()
        expired_token = "expired_token"

        mock_jwt_service.verify_token.return_value = {
            "sub": str(user_id),
            "email": "user@example.com",
        }

        # Token is expired (created in the past, expired slightly after creation)
        created_time = datetime.utcnow() - timedelta(days=8)
        expired_time = datetime.utcnow() - timedelta(days=1)  # Expired
        token_entity = RefreshToken(
            user_id=user_id,
            token=expired_token,
            expires_at=expired_time,
            revoked=False,
            created_at=created_time,
        )
        mock_refresh_token_repo.find_by_token.return_value = token_entity

        result = await use_case.execute(expired_token)

        assert result is None

    @pytest.mark.asyncio
    async def test_refresh_token_revokes_old_token(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test that refresh revokes the old token"""
        user_id = uuid4()
        old_token = "old_token"

        mock_jwt_service.verify_token.return_value = {
            "sub": str(user_id),
            "email": "user@example.com",
        }

        token_entity = RefreshToken(
            user_id=user_id,
            token=old_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
        )
        mock_refresh_token_repo.find_by_token.return_value = token_entity
        mock_jwt_service.create_access_token.return_value = "new_access"
        mock_jwt_service.create_refresh_token.return_value = "new_refresh"

        await use_case.execute(old_token)

        # Verify old token was revoked
        assert token_entity.revoked is True
        mock_refresh_token_repo.update.assert_called_once_with(token_entity)

    @pytest.mark.asyncio
    async def test_refresh_token_creates_new_token(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test that refresh creates a new token entity"""
        user_id = uuid4()
        old_token = "old_token"
        new_refresh_token = "new_refresh_token"

        mock_jwt_service.verify_token.return_value = {
            "sub": str(user_id),
            "email": "user@example.com",
        }

        token_entity = RefreshToken(
            user_id=user_id,
            token=old_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
        )
        mock_refresh_token_repo.find_by_token.return_value = token_entity
        mock_jwt_service.create_access_token.return_value = "new_access"
        mock_jwt_service.create_refresh_token.return_value = new_refresh_token

        await use_case.execute(old_token)

        # Verify new token was created
        mock_refresh_token_repo.create.assert_called_once()
        call_args = mock_refresh_token_repo.create.call_args[0][0]
        assert isinstance(call_args, RefreshToken)
        assert call_args.token == new_refresh_token
        assert call_args.user_id == user_id
        assert call_args.revoked is False

    @pytest.mark.asyncio
    async def test_refresh_token_value_error(
        self, use_case, mock_refresh_token_repo, mock_jwt_service
    ):
        """Test refresh with ValueError from JWT service"""
        invalid_token = "invalid_token"

        mock_jwt_service.verify_token.side_effect = ValueError("Invalid token type")

        result = await use_case.execute(invalid_token)

        assert result is None
