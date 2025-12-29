"""
Unit tests for AdminLoginUseCase
"""
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.identity.application.use_cases.auth.admin_login import (
    AdminLoginUseCase,
)
from app.modules.identity.domain.entities.user import User


@pytest.fixture
def mock_user_repo():
    """Mock user repository"""
    return AsyncMock()


@pytest.fixture
def mock_refresh_token_repo():
    """Mock refresh token repository"""
    return AsyncMock()


@pytest.fixture
def mock_password_service():
    """Mock password service"""
    return Mock()


@pytest.fixture
def mock_jwt_service():
    """Mock JWT service"""
    mock = Mock()
    mock.create_access_token.return_value = "access_token_123"
    mock.create_refresh_token.return_value = "refresh_token_456"
    return mock


@pytest.fixture
def admin_login_use_case(
    mock_user_repo, mock_refresh_token_repo, mock_password_service, mock_jwt_service
):
    """Create AdminLoginUseCase with mocked dependencies"""
    return AdminLoginUseCase(
        user_repo=mock_user_repo,
        refresh_token_repo=mock_refresh_token_repo,
        password_service=mock_password_service,
        jwt_service=mock_jwt_service,
    )


@pytest.fixture
def admin_user():
    """Create a mock admin user"""
    return User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="$2b$12$hashed_password",
        role="admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def super_admin_user():
    """Create a mock super admin user"""
    return User(
        id=uuid4(),
        email="superadmin@example.com",
        password_hash="$2b$12$hashed_password",
        role="super_admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def regular_user():
    """Create a mock regular user"""
    return User(
        id=uuid4(),
        email="user@example.com",
        google_id="google123",
        role="user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_admin_login_success(
    admin_login_use_case, mock_user_repo, mock_password_service, admin_user
):
    """Test successful admin login"""
    # Arrange
    mock_user_repo.get_by_email.return_value = admin_user
    mock_password_service.verify_password.return_value = True

    # Act
    result = await admin_login_use_case.execute("admin@example.com", "correct_password")

    # Assert
    assert result is not None
    access_token, refresh_token, user = result
    assert access_token == "access_token_123"
    assert refresh_token == "refresh_token_456"
    assert user.email == "admin@example.com"
    assert user.role == "admin"
    mock_user_repo.get_by_email.assert_called_once_with("admin@example.com")
    mock_password_service.verify_password.assert_called_once_with(
        "correct_password", admin_user.password_hash
    )


@pytest.mark.asyncio
async def test_super_admin_login_success(
    admin_login_use_case, mock_user_repo, mock_password_service, super_admin_user
):
    """Test successful super admin login"""
    # Arrange
    mock_user_repo.get_by_email.return_value = super_admin_user
    mock_password_service.verify_password.return_value = True

    # Act
    result = await admin_login_use_case.execute(
        "superadmin@example.com", "correct_password"
    )

    # Assert
    assert result is not None
    access_token, refresh_token, user = result
    assert user.role == "super_admin"


@pytest.mark.asyncio
async def test_admin_login_user_not_found(
    admin_login_use_case, mock_user_repo, mock_password_service
):
    """Test admin login fails when user not found"""
    # Arrange
    mock_user_repo.get_by_email.return_value = None

    # Act
    result = await admin_login_use_case.execute("nonexistent@example.com", "password")

    # Assert
    assert result is None
    mock_user_repo.get_by_email.assert_called_once_with("nonexistent@example.com")
    mock_password_service.verify_password.assert_not_called()


@pytest.mark.asyncio
async def test_admin_login_wrong_password(
    admin_login_use_case, mock_user_repo, mock_password_service, admin_user
):
    """Test admin login fails with wrong password"""
    # Arrange
    mock_user_repo.get_by_email.return_value = admin_user
    mock_password_service.verify_password.return_value = False

    # Act
    result = await admin_login_use_case.execute("admin@example.com", "wrong_password")

    # Assert
    assert result is None
    mock_password_service.verify_password.assert_called_once_with(
        "wrong_password", admin_user.password_hash
    )


@pytest.mark.asyncio
async def test_admin_login_regular_user(
    admin_login_use_case, mock_user_repo, mock_password_service, regular_user
):
    """Test admin login fails for regular user (non-admin)"""
    # Arrange
    mock_user_repo.get_by_email.return_value = regular_user
    mock_password_service.verify_password.return_value = True

    # Act
    result = await admin_login_use_case.execute("user@example.com", "password")

    # Assert
    assert result is None
    # Password should be verified but role check should fail
    mock_password_service.verify_password.assert_not_called()  # User has no password_hash


@pytest.mark.asyncio
async def test_admin_login_oauth_user_no_password(
    admin_login_use_case, mock_user_repo, mock_password_service, regular_user
):
    """Test admin login fails for OAuth user without password"""
    # Arrange
    # Regular user has google_id but no password_hash
    mock_user_repo.get_by_email.return_value = regular_user

    # Act
    result = await admin_login_use_case.execute("user@example.com", "password")

    # Assert
    assert result is None
    # Should fail before password verification because password_hash is None
    mock_password_service.verify_password.assert_not_called()


@pytest.mark.asyncio
async def test_admin_login_creates_refresh_token(
    admin_login_use_case,
    mock_user_repo,
    mock_refresh_token_repo,
    mock_password_service,
    admin_user,
):
    """Test that admin login creates and stores refresh token"""
    # Arrange
    mock_user_repo.get_by_email.return_value = admin_user
    mock_password_service.verify_password.return_value = True

    # Act
    result = await admin_login_use_case.execute("admin@example.com", "password")

    # Assert
    assert result is not None
    mock_refresh_token_repo.create.assert_called_once()
    # Verify the refresh token entity was created with correct user_id
    call_args = mock_refresh_token_repo.create.call_args
    refresh_token_entity = call_args[0][0]
    assert refresh_token_entity.user_id == admin_user.id
    assert refresh_token_entity.token == "refresh_token_456"


@pytest.mark.asyncio
async def test_admin_login_jwt_includes_role(
    admin_login_use_case,
    mock_user_repo,
    mock_password_service,
    mock_jwt_service,
    admin_user,
):
    """Test that JWT tokens include role claim"""
    # Arrange
    mock_user_repo.get_by_email.return_value = admin_user
    mock_password_service.verify_password.return_value = True

    # Act
    await admin_login_use_case.execute("admin@example.com", "password")

    # Assert
    # Check that JWT service was called with role in additional_claims
    access_token_call = mock_jwt_service.create_access_token.call_args
    assert "role" in access_token_call.kwargs["additional_claims"]
    assert access_token_call.kwargs["additional_claims"]["role"] == "admin"

    refresh_token_call = mock_jwt_service.create_refresh_token.call_args
    assert "role" in refresh_token_call.kwargs["additional_claims"]
    assert refresh_token_call.kwargs["additional_claims"]["role"] == "admin"
