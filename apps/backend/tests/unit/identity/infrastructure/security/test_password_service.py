"""
Unit tests for PasswordService
Testing password hashing and verification
"""

from unittest.mock import patch

import pytest

from app.modules.identity.infrastructure.security.password_service import (
    PasswordService,
)


class TestPasswordServiceInitialization:
    """Test password service initialization"""

    def test_password_service_initialization(self):
        """Test that PasswordService initializes correctly"""
        service = PasswordService()

        assert service is not None
        assert hasattr(service, "_hasher")


class TestPasswordHashing:
    """Test password hashing functionality"""

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_hash_password(self, mock_hasher):
        """Test hashing a password"""
        mock_hasher.hash.return_value = "hashed_password_123"

        service = PasswordService()
        result = service.hash_password("plain_password")

        assert result == "hashed_password_123"
        mock_hasher.hash.assert_called_once_with("plain_password")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_hash_password_with_empty_string(self, mock_hasher):
        """Test hashing an empty password"""
        mock_hasher.hash.return_value = "hashed_empty"

        service = PasswordService()
        result = service.hash_password("")

        assert result == "hashed_empty"
        mock_hasher.hash.assert_called_once_with("")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_hash_password_with_special_characters(self, mock_hasher):
        """Test hashing a password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        mock_hasher.hash.return_value = "hashed_special"

        service = PasswordService()
        result = service.hash_password(password)

        assert result == "hashed_special"
        mock_hasher.hash.assert_called_once_with(password)

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_hash_password_with_unicode(self, mock_hasher):
        """Test hashing a password with unicode characters"""
        password = "密碼測試123"
        mock_hasher.hash.return_value = "hashed_unicode"

        service = PasswordService()
        result = service.hash_password(password)

        assert result == "hashed_unicode"
        mock_hasher.hash.assert_called_once_with(password)

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_hash_password_with_long_password(self, mock_hasher):
        """Test hashing a very long password"""
        password = "a" * 1000
        mock_hasher.hash.return_value = "hashed_long"

        service = PasswordService()
        result = service.hash_password(password)

        assert result == "hashed_long"
        mock_hasher.hash.assert_called_once_with(password)


class TestPasswordVerification:
    """Test password verification functionality"""

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_success(self, mock_hasher):
        """Test successful password verification"""
        mock_hasher.verify.return_value = True

        service = PasswordService()
        result = service.verify_password("plain_password", "hashed_password")

        assert result is True
        mock_hasher.verify.assert_called_once_with("plain_password", "hashed_password")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_failure(self, mock_hasher):
        """Test failed password verification"""
        mock_hasher.verify.return_value = False

        service = PasswordService()
        result = service.verify_password("wrong_password", "hashed_password")

        assert result is False
        mock_hasher.verify.assert_called_once_with("wrong_password", "hashed_password")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_with_empty_plain(self, mock_hasher):
        """Test verifying with empty plain password"""
        mock_hasher.verify.return_value = False

        service = PasswordService()
        result = service.verify_password("", "hashed_password")

        assert result is False
        mock_hasher.verify.assert_called_once_with("", "hashed_password")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_with_empty_hash(self, mock_hasher):
        """Test verifying against empty hash"""
        mock_hasher.verify.return_value = False

        service = PasswordService()
        result = service.verify_password("plain_password", "")

        assert result is False
        mock_hasher.verify.assert_called_once_with("plain_password", "")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_with_special_characters(self, mock_hasher):
        """Test verifying password with special characters"""
        password = "P@ssw0rd!#$%"
        mock_hasher.verify.return_value = True

        service = PasswordService()
        result = service.verify_password(password, "hashed_special")

        assert result is True
        mock_hasher.verify.assert_called_once_with(password, "hashed_special")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_with_unicode(self, mock_hasher):
        """Test verifying password with unicode characters"""
        password = "密碼測試123"
        mock_hasher.verify.return_value = True

        service = PasswordService()
        result = service.verify_password(password, "hashed_unicode")

        assert result is True
        mock_hasher.verify.assert_called_once_with(password, "hashed_unicode")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_case_sensitive(self, mock_hasher):
        """Test that password verification is case-sensitive"""
        mock_hasher.verify.return_value = False

        service = PasswordService()
        result = service.verify_password("Password", "hashed_password_lowercase")

        assert result is False
        mock_hasher.verify.assert_called_once_with(
            "Password", "hashed_password_lowercase"
        )


class TestPasswordServiceIntegration:
    """Test password service with multiple operations"""

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_hash_and_verify_workflow(self, mock_hasher):
        """Test complete hash and verify workflow"""
        # Setup mock to return different values for hash and verify
        mock_hasher.hash.return_value = "hashed_password_abc123"
        mock_hasher.verify.return_value = True

        service = PasswordService()

        # Hash password
        hashed = service.hash_password("my_password")
        assert hashed == "hashed_password_abc123"

        # Verify password
        is_valid = service.verify_password("my_password", hashed)
        assert is_valid is True

        # Verify calls
        mock_hasher.hash.assert_called_once_with("my_password")
        mock_hasher.verify.assert_called_once_with("my_password", hashed)

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_multiple_hash_calls(self, mock_hasher):
        """Test that multiple hash calls work correctly"""
        mock_hasher.hash.side_effect = ["hash1", "hash2", "hash3"]

        service = PasswordService()

        result1 = service.hash_password("password1")
        result2 = service.hash_password("password2")
        result3 = service.hash_password("password3")

        assert result1 == "hash1"
        assert result2 == "hash2"
        assert result3 == "hash3"
        assert mock_hasher.hash.call_count == 3

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_multiple_verify_calls(self, mock_hasher):
        """Test that multiple verify calls work correctly"""
        mock_hasher.verify.side_effect = [True, False, True]

        service = PasswordService()

        result1 = service.verify_password("pass1", "hash1")
        result2 = service.verify_password("pass2", "hash2")
        result3 = service.verify_password("pass3", "hash3")

        assert result1 is True
        assert result2 is False
        assert result3 is True
        assert mock_hasher.verify.call_count == 3


class TestPasswordServiceErrorHandling:
    """Test password service error handling"""

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_hash_password_exception(self, mock_hasher):
        """Test that exceptions from hasher are propagated"""
        mock_hasher.hash.side_effect = Exception("Hashing error")

        service = PasswordService()

        with pytest.raises(Exception, match="Hashing error"):
            service.hash_password("password")

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_verify_password_exception(self, mock_hasher):
        """Test that exceptions from verification are propagated"""
        mock_hasher.verify.side_effect = Exception("Verification error")

        service = PasswordService()

        with pytest.raises(Exception, match="Verification error"):
            service.verify_password("password", "hash")


class TestPasswordServiceUsagePatterns:
    """Test common usage patterns of password service"""

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_admin_authentication_pattern(self, mock_hasher):
        """Test typical admin authentication pattern"""
        # Simulate stored hash
        stored_hash = "stored_admin_hash"
        mock_hasher.verify.return_value = True

        service = PasswordService()

        # Admin tries to login
        is_authenticated = service.verify_password("admin_password", stored_hash)

        assert is_authenticated is True
        mock_hasher.verify.assert_called_once_with("admin_password", stored_hash)

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_user_registration_pattern(self, mock_hasher):
        """Test typical user registration pattern"""
        mock_hasher.hash.return_value = "new_user_hash"

        service = PasswordService()

        # User registers with password
        password_hash = service.hash_password("new_user_password")

        assert password_hash == "new_user_hash"
        # In real app, this hash would be stored in database
        assert password_hash is not None
        assert len(password_hash) > 0

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_password_change_pattern(self, mock_hasher):
        """Test typical password change pattern"""
        old_hash = "old_password_hash"
        mock_hasher.verify.return_value = True
        mock_hasher.hash.return_value = "new_password_hash"

        service = PasswordService()

        # Verify old password first
        is_old_valid = service.verify_password("old_password", old_hash)
        assert is_old_valid is True

        # Hash new password
        new_hash = service.hash_password("new_password")
        assert new_hash == "new_password_hash"
        assert new_hash != old_hash

    @patch(
        "app.modules.identity.infrastructure.security.password_service.password_hasher"
    )
    def test_failed_login_attempts(self, mock_hasher):
        """Test multiple failed login attempts"""
        stored_hash = "correct_hash"
        mock_hasher.verify.side_effect = [False, False, False, True]

        service = PasswordService()

        # First three attempts fail
        assert service.verify_password("wrong1", stored_hash) is False
        assert service.verify_password("wrong2", stored_hash) is False
        assert service.verify_password("wrong3", stored_hash) is False

        # Fourth attempt succeeds
        assert service.verify_password("correct", stored_hash) is True

        assert mock_hasher.verify.call_count == 4
