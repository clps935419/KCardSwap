"""
Unit tests for PasswordHasher

Tests password hashing and verification functionality.
"""

import pytest

from app.shared.infrastructure.security.password_hasher import PasswordHasher


class TestPasswordHasher:
    """Test PasswordHasher"""

    @pytest.fixture
    def hasher(self):
        """Create hasher instance"""
        return PasswordHasher()

    def test_hash_password(self, hasher):
        """Test password hashing"""
        # Arrange
        password = "MySecurePassword123!"

        # Act
        hashed = hasher.hash(password)

        # Assert
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_hash_different_passwords_produce_different_hashes(self, hasher):
        """Test that different passwords produce different hashes"""
        # Arrange
        password1 = "password123"
        password2 = "password456"

        # Act
        hash1 = hasher.hash(password1)
        hash2 = hasher.hash(password2)

        # Assert
        assert hash1 != hash2

    def test_hash_same_password_produces_different_salts(self, hasher):
        """Test that hashing the same password twice produces different results (due to salt)"""
        # Arrange
        password = "SamePassword123"

        # Act
        hash1 = hasher.hash(password)
        hash2 = hasher.hash(password)

        # Assert
        assert hash1 != hash2  # Different salts

    def test_verify_correct_password(self, hasher):
        """Test verification with correct password"""
        # Arrange
        password = "CorrectPassword123!"
        hashed = hasher.hash(password)

        # Act
        result = hasher.verify(password, hashed)

        # Assert
        assert result is True

    def test_verify_incorrect_password(self, hasher):
        """Test verification with incorrect password"""
        # Arrange
        correct_password = "CorrectPassword123!"
        incorrect_password = "WrongPassword456!"
        hashed = hasher.hash(correct_password)

        # Act
        result = hasher.verify(incorrect_password, hashed)

        # Assert
        assert result is False

    def test_verify_empty_password_fails(self, hasher):
        """Test that empty password verification fails"""
        # Arrange
        password = "password123"
        hashed = hasher.hash(password)

        # Act
        result = hasher.verify("", hashed)

        # Assert
        assert result is False

    def test_verify_case_sensitive(self, hasher):
        """Test that password verification is case-sensitive"""
        # Arrange
        password = "Password123"
        hashed = hasher.hash(password)

        # Act
        result_upper = hasher.verify("PASSWORD123", hashed)
        result_lower = hasher.verify("password123", hashed)

        # Assert
        assert result_upper is False
        assert result_lower is False

    def test_needs_update_new_hash(self, hasher):
        """Test that newly created hash doesn't need update"""
        # Arrange
        password = "TestPassword123"
        hashed = hasher.hash(password)

        # Act
        needs_update = hasher.needs_update(hashed)

        # Assert
        assert needs_update is False

    def test_hash_unicode_password(self, hasher):
        """Test hashing password with unicode characters"""
        # Arrange
        password = "密碼123!@#"

        # Act
        hashed = hasher.hash(password)
        result = hasher.verify(password, hashed)

        # Assert
        assert hashed is not None
        assert result is True

    def test_hash_long_password(self, hasher):
        """Test hashing a very long password"""
        # Arrange
        password = "A" * 200

        # Act
        hashed = hasher.hash(password)
        result = hasher.verify(password, hashed)

        # Assert
        assert hashed is not None
        assert result is True

    def test_hash_password_with_special_characters(self, hasher):
        """Test hashing password with special characters"""
        # Arrange
        password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/"

        # Act
        hashed = hasher.hash(password)
        result = hasher.verify(password, hashed)

        # Assert
        assert hashed is not None
        assert result is True

    def test_verify_with_whitespace(self, hasher):
        """Test that whitespace in passwords matters"""
        # Arrange
        password_with_space = "pass word"
        password_without_space = "password"
        hashed = hasher.hash(password_with_space)

        # Act
        result_correct = hasher.verify(password_with_space, hashed)
        result_incorrect = hasher.verify(password_without_space, hashed)

        # Assert
        assert result_correct is True
        assert result_incorrect is False
