"""
Unit tests for RefreshTokenRepositoryImpl

Tests the refresh token repository implementation with mocked database session.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain.entities.refresh_token import RefreshToken
from app.modules.identity.infrastructure.database.models.refresh_token_model import (
    RefreshTokenModel,
)
from app.modules.identity.infrastructure.repositories.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)


class TestRefreshTokenRepositoryImpl:
    """Test RefreshTokenRepositoryImpl"""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return RefreshTokenRepositoryImpl(mock_session)

    @pytest.fixture
    def sample_refresh_token(self):
        """Create sample RefreshToken entity"""
        return RefreshToken(
            id=uuid4(),
            user_id=uuid4(),
            token="test-refresh-token-abc123",
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_token_model(self, sample_refresh_token):
        """Create sample RefreshTokenModel"""
        return RefreshTokenModel(
            id=sample_refresh_token.id,
            user_id=sample_refresh_token.user_id,
            token=sample_refresh_token.token,
            expires_at=sample_refresh_token.expires_at,
            revoked=sample_refresh_token.revoked,
            created_at=sample_refresh_token.created_at,
            updated_at=sample_refresh_token.updated_at,
        )

    @pytest.mark.asyncio
    async def test_create_refresh_token(
        self, repository, mock_session, sample_refresh_token
    ):
        """Test creating a new refresh token"""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Act
        result = await repository.create(sample_refresh_token)

        # Assert
        assert result is not None
        assert result.id == sample_refresh_token.id
        assert result.token == sample_refresh_token.token
        assert result.user_id == sample_refresh_token.user_id
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_token_found(
        self, repository, mock_session, sample_token_model
    ):
        """Test finding token by token string when it exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_token_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_token(sample_token_model.token)

        # Assert
        assert result is not None
        assert result.token == sample_token_model.token
        assert result.user_id == sample_token_model.user_id
        assert result.revoked == sample_token_model.revoked

    @pytest.mark.asyncio
    async def test_find_by_token_not_found(self, repository, mock_session):
        """Test finding token by token string when it doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_token("non-existent-token")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_user_id(self, repository, mock_session):
        """Test finding all tokens for a user"""
        # Arrange
        user_id = uuid4()
        token_models = [
            RefreshTokenModel(
                id=uuid4(),
                user_id=user_id,
                token=f"token-{i}",
                expires_at=datetime.utcnow() + timedelta(days=7),
                revoked=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = token_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.find_by_user_id(user_id)

        # Assert
        assert len(result) == 3
        for token in result:
            assert token.user_id == user_id

    @pytest.mark.asyncio
    async def test_update_refresh_token(
        self, repository, mock_session, sample_refresh_token, sample_token_model
    ):
        """Test updating a refresh token"""
        # Arrange
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.get = AsyncMock(return_value=sample_token_model)

        # Create modified token
        revoked_token = RefreshToken(
            id=sample_refresh_token.id,
            user_id=sample_refresh_token.user_id,
            token=sample_refresh_token.token,
            expires_at=sample_refresh_token.expires_at,
            revoked=True,
            created_at=sample_refresh_token.created_at,
            updated_at=datetime.utcnow(),
        )

        # Act
        result = await repository.update(revoked_token)

        # Assert
        assert result is not None
        assert result.id == revoked_token.id
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_non_existing_token(
        self, repository, mock_session, sample_refresh_token
    ):
        """Test updating a non-existing token raises error"""
        # Arrange
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError, match="RefreshToken with id .* not found"):
            await repository.update(sample_refresh_token)

    @pytest.mark.asyncio
    async def test_delete_existing_token(
        self, repository, mock_session, sample_token_model
    ):
        """Test deleting an existing token"""
        # Arrange
        mock_session.get = AsyncMock(return_value=sample_token_model)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.delete(sample_token_model.id)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_non_existing_token(self, repository, mock_session):
        """Test deleting a non-existing token"""
        # Arrange
        mock_session.get = AsyncMock(return_value=None)

        # Act
        result = await repository.delete(uuid4())

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_revoke_all_for_user(self, repository, mock_session):
        """Test revoking all tokens for a user"""
        # Arrange
        user_id = uuid4()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Act
        count = await repository.revoke_all_for_user(user_id)

        # Assert
        assert count == 3
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_token_success(
        self, repository, mock_session, sample_token_model
    ):
        """Test revoking a specific token"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_token_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        # Act
        result = await repository.revoke_token(
            sample_token_model.user_id, sample_token_model.token
        )

        # Assert
        assert result is True
        assert sample_token_model.revoked is True
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_token_not_found(self, repository, mock_session):
        """Test revoking a non-existing token"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await repository.revoke_token(uuid4(), "non-existent-token")

        # Assert
        assert result is False
        mock_session.flush.assert_not_called()
