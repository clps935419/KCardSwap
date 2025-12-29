"""
Unit tests for RefreshToken Entity
Testing token lifecycle management and validation
"""
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.modules.identity.domain.entities.refresh_token import RefreshToken


class TestRefreshTokenCreation:
    """Test refresh token entity creation and initialization"""

    def test_create_minimal_token(self):
        """Test creating a token with required fields"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        assert refresh_token.user_id == user_id
        assert refresh_token.token == token
        assert refresh_token.expires_at == expires_at
        assert isinstance(refresh_token.id, UUID)
        assert refresh_token.revoked is False
        assert isinstance(refresh_token.created_at, datetime)
        assert isinstance(refresh_token.updated_at, datetime)

    def test_create_full_token(self):
        """Test creating a token with all fields"""
        user_id = uuid4()
        token_id = uuid4()
        token = "test_token_abc123"
        now = datetime.utcnow()
        expires_at = now + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            id=token_id,
            revoked=True,
            created_at=now,
            updated_at=now,
        )

        assert refresh_token.id == token_id
        assert refresh_token.revoked is True
        assert refresh_token.created_at == now
        assert refresh_token.updated_at == now

    def test_default_revoked_is_false(self):
        """Test that default revoked status is False"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        assert refresh_token.revoked is False


class TestRefreshTokenValidation:
    """Test refresh token entity validation rules"""

    def test_empty_token_raises_error(self):
        """Test that empty token raises ValueError"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        with pytest.raises(ValueError, match="Token cannot be empty"):
            RefreshToken(
                user_id=user_id,
                token="",
                expires_at=expires_at,
            )

    def test_none_token_raises_error(self):
        """Test that None token raises ValueError"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        with pytest.raises(ValueError, match="Token cannot be empty"):
            RefreshToken(
                user_id=user_id,
                token=None,
                expires_at=expires_at,
            )

    def test_none_user_id_raises_error(self):
        """Test that None user_id raises ValueError"""
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        with pytest.raises(ValueError, match="User ID is required"):
            RefreshToken(
                user_id=None,
                token=token,
                expires_at=expires_at,
            )

    def test_expires_at_before_created_at_raises_error(self):
        """Test that expiration before creation raises ValueError"""
        user_id = uuid4()
        token = "test_token_abc123"
        now = datetime.utcnow()
        past_time = now - timedelta(days=1)

        with pytest.raises(
            ValueError, match="Expiration time must be after creation time"
        ):
            RefreshToken(
                user_id=user_id,
                token=token,
                expires_at=past_time,
                created_at=now,
            )

    def test_expires_at_equals_created_at_raises_error(self):
        """Test that expiration equal to creation raises ValueError"""
        user_id = uuid4()
        token = "test_token_abc123"
        now = datetime.utcnow()

        with pytest.raises(
            ValueError, match="Expiration time must be after creation time"
        ):
            RefreshToken(
                user_id=user_id,
                token=token,
                expires_at=now,
                created_at=now,
            )


class TestRefreshTokenBusinessLogic:
    """Test refresh token business logic methods"""

    def test_is_expired_for_future_token(self):
        """Test is_expired returns False for non-expired token"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        assert refresh_token.is_expired() is False

    def test_is_expired_for_past_token(self):
        """Test is_expired returns True for expired token"""
        user_id = uuid4()
        token = "test_token_abc123"
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=1)
        created_at = now - timedelta(days=1)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            created_at=created_at,
        )

        # Token expires in the past relative to "now"
        # We need to test with a token that's already expired
        past_token = RefreshToken(
            user_id=user_id,
            token="old_token",
            expires_at=datetime.utcnow() - timedelta(days=1),
            created_at=datetime.utcnow() - timedelta(days=8),
        )

        assert past_token.is_expired() is True

    def test_is_expired_at_exact_expiration(self):
        """Test is_expired at exact expiration time"""
        user_id = uuid4()
        token = "test_token_abc123"
        # Token that expires right now
        expires_at = datetime.utcnow()
        created_at = datetime.utcnow() - timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            created_at=created_at,
        )

        # At exact expiration, should be considered expired
        assert refresh_token.is_expired() is True

    def test_is_valid_for_active_token(self):
        """Test is_valid returns True for valid token"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        assert refresh_token.is_valid() is True

    def test_is_valid_for_expired_token(self):
        """Test is_valid returns False for expired token"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() - timedelta(days=1)
        created_at = datetime.utcnow() - timedelta(days=8)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            created_at=created_at,
        )

        assert refresh_token.is_valid() is False

    def test_is_valid_for_revoked_token(self):
        """Test is_valid returns False for revoked token"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=True,
        )

        assert refresh_token.is_valid() is False

    def test_is_valid_for_expired_and_revoked_token(self):
        """Test is_valid returns False for expired and revoked token"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() - timedelta(days=1)
        created_at = datetime.utcnow() - timedelta(days=8)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            created_at=created_at,
            revoked=True,
        )

        assert refresh_token.is_valid() is False

    def test_revoke_token(self):
        """Test revoking a token"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        assert refresh_token.revoked is False
        old_updated_at = refresh_token.updated_at

        refresh_token.revoke()

        assert refresh_token.revoked is True
        assert refresh_token.updated_at > old_updated_at

    def test_revoke_already_revoked_token_raises_error(self):
        """Test that revoking an already revoked token raises ValueError"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=True,
        )

        with pytest.raises(ValueError, match="Token is already revoked"):
            refresh_token.revoke()

    def test_revoke_makes_token_invalid(self):
        """Test that revoking a token makes it invalid"""
        user_id = uuid4()
        token = "test_token_abc123"
        expires_at = datetime.utcnow() + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        assert refresh_token.is_valid() is True

        refresh_token.revoke()

        assert refresh_token.is_valid() is False


class TestRefreshTokenEquality:
    """Test refresh token entity equality and hashing"""

    def test_tokens_with_same_id_are_equal(self):
        """Test that tokens with same ID are equal"""
        token_id = uuid4()
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        token1 = RefreshToken(
            id=token_id,
            user_id=user_id,
            token="token1",
            expires_at=expires_at,
        )
        token2 = RefreshToken(
            id=token_id,
            user_id=uuid4(),
            token="token2",
            expires_at=expires_at,
        )

        assert token1 == token2

    def test_tokens_with_different_ids_are_not_equal(self):
        """Test that tokens with different IDs are not equal"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        token1 = RefreshToken(
            user_id=user_id,
            token="same_token",
            expires_at=expires_at,
        )
        token2 = RefreshToken(
            user_id=user_id,
            token="same_token",
            expires_at=expires_at,
        )

        assert token1 != token2

    def test_token_not_equal_to_non_token(self):
        """Test that token is not equal to non-RefreshToken object"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        token = RefreshToken(
            user_id=user_id,
            token="test_token",
            expires_at=expires_at,
        )

        assert token != "not a token"
        assert token != 123
        assert token != None

    def test_token_hash(self):
        """Test that token can be hashed"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        token = RefreshToken(
            user_id=user_id,
            token="test_token",
            expires_at=expires_at,
        )

        # Should not raise
        hash(token)

        # Should be usable in sets
        token_set = {token}
        assert token in token_set

    def test_token_repr(self):
        """Test token string representation"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        token = RefreshToken(
            user_id=user_id,
            token="test_token",
            expires_at=expires_at,
        )

        repr_str = repr(token)
        assert "RefreshToken" in repr_str
        assert str(token.id) in repr_str
        assert str(user_id) in repr_str
        assert "expired=" in repr_str
        assert "revoked=" in repr_str


class TestRefreshTokenProperties:
    """Test refresh token property access"""

    def test_all_properties_accessible(self):
        """Test that all properties can be accessed"""
        user_id = uuid4()
        token_id = uuid4()
        token = "test_token_abc123"
        now = datetime.utcnow()
        expires_at = now + timedelta(days=7)

        refresh_token = RefreshToken(
            id=token_id,
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=True,
            created_at=now,
            updated_at=now,
        )

        assert refresh_token.id == token_id
        assert refresh_token.user_id == user_id
        assert refresh_token.token == token
        assert refresh_token.expires_at == expires_at
        assert refresh_token.revoked is True
        assert refresh_token.created_at == now
        assert refresh_token.updated_at == now

    def test_properties_are_read_only(self):
        """Test that properties cannot be directly modified"""
        user_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=7)

        token = RefreshToken(
            user_id=user_id,
            token="test_token",
            expires_at=expires_at,
        )

        # Properties should not have setters
        with pytest.raises(AttributeError):
            token.token = "new_token"

        with pytest.raises(AttributeError):
            token.user_id = uuid4()

        with pytest.raises(AttributeError):
            token.revoked = True

        with pytest.raises(AttributeError):
            token.expires_at = datetime.utcnow()
