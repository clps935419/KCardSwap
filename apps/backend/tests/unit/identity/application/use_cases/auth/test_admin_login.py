"""
Unit tests for AdminLoginUseCase

Tests the admin login use case with mocked dependencies.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.identity.application.use_cases.auth.admin_login import (
    AdminLoginUseCase,
)
from app.modules.identity.domain.entities.user import User


class TestAdminLoginUseCase:
    """Test AdminLoginUseCase"""

    @pytest.fixture
    def mock_user_repo(self):
        """Create mock user repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_refresh_token_repo(self):
        """Create mock refresh token repository"""
        return AsyncMock()

    @pytest.fixture
    def mock_password_service(self):
        """Create mock password service"""
        return MagicMock()

    @pytest.fixture
    def mock_jwt_service(self):
        """Create mock JWT service"""
        return MagicMock()

    @pytest.fixture
    def use_case(
        self,
        mock_user_repo,
        mock_refresh_token_repo,
        mock_password_service,
        mock_jwt_service,
    ):
        """Create use case instance"""
        return AdminLoginUseCase(
            user_repo=mock_user_repo,
            refresh_token_repo=mock_refresh_token_repo,
            password_service=mock_password_service,
            jwt_service=mock_jwt_service,
        )

    @pytest.fixture
    def sample_admin_user(self):
        """Create sample admin user"""
        return User(
            id=uuid4(),
            email="admin@example.com",
            password_hash="$2b$12$hashedpassword",
            role="admin",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_admin_login_success(
        self,
        use_case,
        mock_user_repo,
        mock_refresh_token_repo,
        mock_password_service,
        mock_jwt_service,
        sample_admin_user,
    ):
        """Test successful admin login"""
        # Arrange
        email = "admin@example.com"
        password = "password123"

        mock_user_repo.get_by_email.return_value = sample_admin_user
        mock_password_service.verify_password.return_value = True
        mock_jwt_service.create_access_token.return_value = "access_token"
        mock_jwt_service.create_refresh_token.return_value = "refresh_token"
        mock_refresh_token_repo.create.return_value = None

        # Act
        result = await use_case.execute(email, password)

        # Assert
        assert result is not None
        access_token, refresh_token, user = result
        assert access_token == "access_token"
        assert refresh_token == "refresh_token"
        assert user.email == email
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_password_service.verify_password.assert_called_once_with(
            password, sample_admin_user.password_hash
        )
        mock_refresh_token_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_admin_login_user_not_found(
        self, use_case, mock_user_repo, mock_password_service
    ):
        """Test login fails when user doesn't exist"""
        # Arrange
        mock_user_repo.get_by_email.return_value = None

        # Act
        result = await use_case.execute("nonexistent@example.com", "password123")

        # Assert
        assert result is None
        mock_password_service.verify_password.assert_not_called()

    @pytest.mark.asyncio
    async def test_admin_login_no_password_hash(
        self, use_case, mock_user_repo, mock_password_service
    ):
        """Test login fails for OAuth users without password"""
        # Arrange
        oauth_user = User(
            id=uuid4(),
            email="oauth@example.com",
            password_hash=None,  # OAuth user
            role="admin",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_user_repo.get_by_email.return_value = oauth_user

        # Act
        result = await use_case.execute("oauth@example.com", "password123")

        # Assert
        assert result is None
        mock_password_service.verify_password.assert_not_called()

    @pytest.mark.asyncio
    async def test_admin_login_wrong_password(
        self, use_case, mock_user_repo, mock_password_service, sample_admin_user
    ):
        """Test login fails with wrong password"""
        # Arrange
        mock_user_repo.get_by_email.return_value = sample_admin_user
        mock_password_service.verify_password.return_value = False

        # Act
        result = await use_case.execute("admin@example.com", "wrongpassword")

        # Assert
        assert result is None
        mock_password_service.verify_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_admin_login_not_admin_role(
        self, use_case, mock_user_repo, mock_password_service
    ):
        """Test login fails for non-admin users"""
        # Arrange
        regular_user = User(
            id=uuid4(),
            email="user@example.com",
            password_hash="$2b$12$hashedpassword",
            role="user",  # Not admin
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_user_repo.get_by_email.return_value = regular_user
        mock_password_service.verify_password.return_value = True

        # Act
        result = await use_case.execute("user@example.com", "password123")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_admin_login_creates_refresh_token(
        self,
        use_case,
        mock_user_repo,
        mock_refresh_token_repo,
        mock_password_service,
        mock_jwt_service,
        sample_admin_user,
    ):
        """Test that login creates a refresh token in database"""
        # Arrange
        mock_user_repo.get_by_email.return_value = sample_admin_user
        mock_password_service.verify_password.return_value = True
        mock_jwt_service.create_access_token.return_value = "access_token"
        mock_jwt_service.create_refresh_token.return_value = "refresh_token"

        # Act
        await use_case.execute("admin@example.com", "password123")

        # Assert
        mock_refresh_token_repo.create.assert_called_once()
        created_token = mock_refresh_token_repo.create.call_args[0][0]
        assert created_token.user_id == sample_admin_user.id
        assert created_token.token == "refresh_token"
        assert created_token.revoked is False
