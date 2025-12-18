"""
Unit tests for GoogleLoginUseCase (T056)

Tests the Google OAuth login flow including:
- User creation for new users
- User retrieval for existing users
- Profile creation for new users
- JWT token generation
- Refresh token creation and storage
- Error handling for invalid tokens
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.modules.identity.application.use_cases.auth.login_with_google import (
    GoogleLoginUseCase,
)
from app.modules.identity.domain.entities.user import User
from app.modules.identity.domain.entities.profile import Profile
from app.modules.identity.domain.entities.refresh_token import RefreshToken


@pytest.fixture
def mock_user_repo():
    """Mock user repository"""
    repo = Mock()
    repo.get_by_google_id = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_profile_repo():
    """Mock profile repository"""
    repo = Mock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_refresh_token_repo():
    """Mock refresh token repository"""
    repo = Mock()
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def mock_google_oauth_service():
    """Mock Google OAuth service"""
    service = Mock()
    service.verify_google_token = AsyncMock()
    return service


@pytest.fixture
def mock_jwt_service():
    """Mock JWT service"""
    service = Mock()
    service.create_access_token = Mock(return_value="mock_access_token")
    service.create_refresh_token = Mock(return_value="mock_refresh_token")
    return service


@pytest.fixture
def use_case(
    mock_user_repo,
    mock_profile_repo,
    mock_refresh_token_repo,
    mock_google_oauth_service,
    mock_jwt_service,
):
    """Create GoogleLoginUseCase with mocked dependencies"""
    return GoogleLoginUseCase(
        user_repo=mock_user_repo,
        profile_repo=mock_profile_repo,
        refresh_token_repo=mock_refresh_token_repo,
        google_oauth_service=mock_google_oauth_service,
        jwt_service=mock_jwt_service,
    )


class TestGoogleLoginUseCaseNewUser:
    """Test Google login flow for new users"""

    @pytest.mark.asyncio
    async def test_successful_login_creates_new_user(
        self, use_case, mock_user_repo, mock_google_oauth_service
    ):
        """Test that a new user is created when logging in for the first time"""
        # Arrange
        google_token = "valid_google_token"
        user_info = {
            "google_id": "google_123",
            "email": "newuser@example.com",
            "name": "New User",
            "picture": "https://example.com/avatar.jpg",
        }
        mock_google_oauth_service.verify_google_token.return_value = user_info
        mock_user_repo.get_by_google_id.return_value = None  # User doesn't exist

        # Create a user that will be returned by save
        new_user = User(
            id=uuid4(),
            google_id=user_info["google_id"],
            email=user_info["email"],
        )
        mock_user_repo.save.return_value = new_user

        # Act
        result = await use_case.execute(google_token)

        # Assert
        assert result is not None
        access_token, refresh_token, user = result
        assert access_token == "mock_access_token"
        assert refresh_token == "mock_refresh_token"
        assert user.email == "newuser@example.com"
        assert user.google_id == "google_123"
        mock_user_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_new_user_creates_default_profile(
        self, use_case, mock_profile_repo, mock_google_oauth_service, mock_user_repo
    ):
        """Test that a default profile is created for new users"""
        # Arrange
        user_info = {
            "google_id": "google_123",
            "email": "newuser@example.com",
            "picture": "https://example.com/avatar.jpg",
        }
        mock_google_oauth_service.verify_google_token.return_value = user_info
        mock_user_repo.get_by_google_id.return_value = None

        new_user = User(
            id=uuid4(),
            google_id=user_info["google_id"],
            email=user_info["email"],
        )
        mock_user_repo.save.return_value = new_user

        # Act
        await use_case.execute("valid_token")

        # Assert
        mock_profile_repo.save.assert_awaited_once()
        # Verify profile was created with correct user_id and avatar
        call_args = mock_profile_repo.save.call_args[0][0]
        assert isinstance(call_args, Profile)
        assert call_args.user_id == new_user.id
        assert call_args.avatar_url == user_info["picture"]


class TestGoogleLoginUseCaseExistingUser:
    """Test Google login flow for existing users"""

    @pytest.mark.asyncio
    async def test_successful_login_retrieves_existing_user(
        self, use_case, mock_user_repo, mock_google_oauth_service, mock_profile_repo
    ):
        """Test that existing user is retrieved instead of creating new one"""
        # Arrange
        existing_user = User(
            id=uuid4(),
            google_id="google_123",
            email="existing@example.com",
        )
        user_info = {
            "google_id": "google_123",
            "email": "existing@example.com",
            "picture": "https://example.com/avatar.jpg",
        }
        mock_google_oauth_service.verify_google_token.return_value = user_info
        mock_user_repo.get_by_google_id.return_value = existing_user

        # Act
        result = await use_case.execute("valid_token")

        # Assert
        assert result is not None
        access_token, refresh_token, user = result
        assert user.id == existing_user.id
        assert user.email == existing_user.email
        # Should not save a new user
        mock_user_repo.save.assert_not_awaited()
        # Should not create a new profile
        mock_profile_repo.save.assert_not_awaited()


class TestGoogleLoginUseCaseTokenGeneration:
    """Test JWT token generation in login flow"""

    @pytest.mark.asyncio
    async def test_generates_access_and_refresh_tokens(
        self,
        use_case,
        mock_jwt_service,
        mock_google_oauth_service,
        mock_user_repo,
    ):
        """Test that both access and refresh tokens are generated"""
        # Arrange
        user = User(id=uuid4(), google_id="google_123", email="test@example.com")
        mock_google_oauth_service.verify_google_token.return_value = {
            "google_id": "google_123",
            "email": "test@example.com",
        }
        mock_user_repo.get_by_google_id.return_value = user

        # Act
        result = await use_case.execute("valid_token")

        # Assert
        assert result is not None
        access_token, refresh_token, _ = result
        assert access_token == "mock_access_token"
        assert refresh_token == "mock_refresh_token"
        mock_jwt_service.create_access_token.assert_called_once()
        mock_jwt_service.create_refresh_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_jwt_tokens_include_user_id_and_email(
        self,
        use_case,
        mock_jwt_service,
        mock_google_oauth_service,
        mock_user_repo,
    ):
        """Test that JWT tokens include user ID as subject and email in claims"""
        # Arrange
        user_id = uuid4()
        user = User(id=user_id, google_id="google_123", email="test@example.com")
        mock_google_oauth_service.verify_google_token.return_value = {
            "google_id": "google_123",
            "email": "test@example.com",
        }
        mock_user_repo.get_by_google_id.return_value = user

        # Act
        await use_case.execute("valid_token")

        # Assert
        # Check access token
        access_call = mock_jwt_service.create_access_token.call_args
        assert access_call[1]["subject"] == str(user_id)
        assert access_call[1]["additional_claims"]["email"] == "test@example.com"

        # Check refresh token
        refresh_call = mock_jwt_service.create_refresh_token.call_args
        assert refresh_call[1]["subject"] == str(user_id)
        assert refresh_call[1]["additional_claims"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_saves_refresh_token_to_database(
        self,
        use_case,
        mock_refresh_token_repo,
        mock_google_oauth_service,
        mock_user_repo,
    ):
        """Test that refresh token is saved to database"""
        # Arrange
        user = User(id=uuid4(), google_id="google_123", email="test@example.com")
        mock_google_oauth_service.verify_google_token.return_value = {
            "google_id": "google_123",
            "email": "test@example.com",
        }
        mock_user_repo.get_by_google_id.return_value = user

        # Act
        await use_case.execute("valid_token")

        # Assert
        mock_refresh_token_repo.create.assert_awaited_once()
        saved_token = mock_refresh_token_repo.create.call_args[0][0]
        assert isinstance(saved_token, RefreshToken)
        assert saved_token.user_id == user.id
        assert saved_token.token == "mock_refresh_token"
        assert saved_token.revoked is False


class TestGoogleLoginUseCaseErrorHandling:
    """Test error handling in Google login flow"""

    @pytest.mark.asyncio
    async def test_invalid_google_token_returns_none(
        self, use_case, mock_google_oauth_service
    ):
        """Test that invalid Google token returns None"""
        # Arrange
        mock_google_oauth_service.verify_google_token.return_value = None

        # Act
        result = await use_case.execute("invalid_token")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_missing_email_returns_none(
        self, use_case, mock_google_oauth_service
    ):
        """Test that missing email in user info returns None"""
        # Arrange
        mock_google_oauth_service.verify_google_token.return_value = {
            "google_id": "google_123",
            # email is missing
        }

        # Act
        result = await use_case.execute("valid_token")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_missing_google_id_returns_none(
        self, use_case, mock_google_oauth_service
    ):
        """Test that missing google_id in user info returns None"""
        # Arrange
        mock_google_oauth_service.verify_google_token.return_value = {
            # google_id is missing
            "email": "test@example.com",
        }

        # Act
        result = await use_case.execute("valid_token")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_empty_user_info_returns_none(
        self, use_case, mock_google_oauth_service
    ):
        """Test that empty user info returns None"""
        # Arrange
        mock_google_oauth_service.verify_google_token.return_value = {}

        # Act
        result = await use_case.execute("valid_token")

        # Assert
        assert result is None


class TestGoogleLoginUseCaseRefreshTokenExpiry:
    """Test refresh token expiry handling"""

    @pytest.mark.asyncio
    async def test_refresh_token_has_expiry_date(
        self,
        use_case,
        mock_refresh_token_repo,
        mock_google_oauth_service,
        mock_user_repo,
    ):
        """Test that refresh token has an expiry date set"""
        # Arrange
        user = User(id=uuid4(), google_id="google_123", email="test@example.com")
        mock_google_oauth_service.verify_google_token.return_value = {
            "google_id": "google_123",
            "email": "test@example.com",
        }
        mock_user_repo.get_by_google_id.return_value = user

        # Act
        await use_case.execute("valid_token")

        # Assert
        saved_token = mock_refresh_token_repo.create.call_args[0][0]
        assert saved_token.expires_at is not None
        # Should expire roughly 7 days from now
        expected_expiry = datetime.utcnow() + timedelta(days=7)
        # Allow 5 seconds tolerance for test execution time
        assert abs((saved_token.expires_at - expected_expiry).total_seconds()) < 5
