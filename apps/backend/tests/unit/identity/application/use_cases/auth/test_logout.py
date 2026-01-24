"""
Unit tests for LogoutUseCase
Testing logout functionality and token revocation
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.identity.application.use_cases.auth.logout import LogoutUseCase


class TestLogoutUseCase:
    """Test logout use case"""

    @pytest.fixture
    def mock_refresh_token_repo(self):
        """Mock refresh token repository"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_refresh_token_repo):
        """Create logout use case with mocked dependencies"""
        return LogoutUseCase(refresh_token_repo=mock_refresh_token_repo)

    @pytest.mark.asyncio
    async def test_logout_success(self, use_case, mock_refresh_token_repo):
        """Test successful logout"""
        user_id = uuid4()
        refresh_token = "valid_refresh_token"

        mock_refresh_token_repo.revoke_token.return_value = True

        result = await use_case.execute(user_id, refresh_token)

        assert result is True
        mock_refresh_token_repo.revoke_token.assert_called_once_with(
            user_id, refresh_token
        )

    @pytest.mark.asyncio
    async def test_logout_token_not_found(self, use_case, mock_refresh_token_repo):
        """Test logout when token is not found"""
        user_id = uuid4()
        refresh_token = "non_existent_token"

        mock_refresh_token_repo.revoke_token.return_value = False

        result = await use_case.execute(user_id, refresh_token)

        assert result is False
        mock_refresh_token_repo.revoke_token.assert_called_once_with(
            user_id, refresh_token
        )

    @pytest.mark.asyncio
    async def test_logout_with_different_user_ids(
        self, use_case, mock_refresh_token_repo
    ):
        """Test logout with different user IDs"""
        user_id_1 = uuid4()
        user_id_2 = uuid4()
        refresh_token_1 = "token_1"
        refresh_token_2 = "token_2"

        mock_refresh_token_repo.revoke_token.return_value = True

        result_1 = await use_case.execute(user_id_1, refresh_token_1)
        result_2 = await use_case.execute(user_id_2, refresh_token_2)

        assert result_1 is True
        assert result_2 is True
        assert mock_refresh_token_repo.revoke_token.call_count == 2

    @pytest.mark.asyncio
    async def test_logout_propagates_exception(
        self, use_case, mock_refresh_token_repo
    ):
        """Test that exceptions from repository are propagated"""
        user_id = uuid4()
        refresh_token = "token"

        mock_refresh_token_repo.revoke_token.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(user_id, refresh_token)

    @pytest.mark.asyncio
    async def test_logout_calls_repository_method(
        self, use_case, mock_refresh_token_repo
    ):
        """Test that logout calls the correct repository method"""
        user_id = uuid4()
        refresh_token = "token"

        mock_refresh_token_repo.revoke_token.return_value = True

        await use_case.execute(user_id, refresh_token)

        # Verify the correct method was called
        assert hasattr(mock_refresh_token_repo, "revoke_token")
        mock_refresh_token_repo.revoke_token.assert_called_once()
