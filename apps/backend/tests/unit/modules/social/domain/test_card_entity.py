"""
Unit tests for Card Entity (T084)
Following DDD principles and test patterns from test_user_entity.py
"""
import pytest
from datetime import datetime
from uuid import uuid4, UUID

from app.modules.social.domain.entities.card import Card


class TestCardCreation:
    """Test card entity creation and validation"""

    def test_card_creation_with_required_fields(self):
        """Test card creation with only required fields"""
        owner_id = uuid4()

        card = Card(owner_id=owner_id)

        assert card.owner_id == owner_id
        assert card.id is not None
        assert isinstance(card.id, UUID)
        assert card.status == Card.STATUS_AVAILABLE
        assert card.created_at is not None
        assert card.updated_at is not None
        assert card.idol is None
        assert card.idol_group is None
        assert card.album is None
        assert card.version is None
        assert card.rarity is None
        assert card.image_url is None
        assert card.size_bytes is None

    def test_card_creation_with_all_fields(self):
        """Test card creation with all fields populated"""
        owner_id = uuid4()
        card_id = uuid4()
        created_at = datetime.utcnow()

        card = Card(
            id=card_id,
            owner_id=owner_id,
            idol="IU",
            idol_group="Solo",
            album="LILAC",
            version="Standard",
            rarity=Card.RARITY_RARE,
            status=Card.STATUS_AVAILABLE,
            image_url="https://storage.googleapis.com/kcardswap/cards/test.jpg",
            size_bytes=1024000,
            created_at=created_at,
        )

        assert card.id == card_id
        assert card.owner_id == owner_id
        assert card.idol == "IU"
        assert card.idol_group == "Solo"
        assert card.album == "LILAC"
        assert card.version == "Standard"
        assert card.rarity == Card.RARITY_RARE
        assert card.status == Card.STATUS_AVAILABLE
        assert (
            card.image_url == "https://storage.googleapis.com/kcardswap/cards/test.jpg"
        )
        assert card.size_bytes == 1024000
        assert card.created_at == created_at

    def test_card_validation_requires_owner_id(self):
        """Test that card creation requires owner_id"""
        with pytest.raises(TypeError):
            Card()  # Missing required owner_id parameter

    def test_card_validation_invalid_status(self):
        """Test validation fails for invalid status"""
        owner_id = uuid4()

        with pytest.raises(ValueError, match="Invalid status"):
            Card(owner_id=owner_id, status="invalid_status")

    def test_card_validation_invalid_rarity(self):
        """Test validation fails for invalid rarity"""
        owner_id = uuid4()

        with pytest.raises(ValueError, match="Invalid rarity"):
            Card(owner_id=owner_id, rarity="super_ultra_rare")

    def test_card_validation_negative_size(self):
        """Test validation fails for negative size_bytes"""
        owner_id = uuid4()

        with pytest.raises(ValueError, match="size_bytes must be non-negative"):
            Card(owner_id=owner_id, size_bytes=-100)


class TestCardStatusTransitions:
    """Test card status transitions and business logic"""

    def test_mark_as_trading(self):
        """Test marking card as trading"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_AVAILABLE)
        original_updated_at = card.updated_at

        card.mark_as_trading()

        assert card.status == Card.STATUS_TRADING
        assert card.updated_at > original_updated_at

    def test_mark_as_traded(self):
        """Test marking card as traded"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_TRADING)
        original_updated_at = card.updated_at

        card.mark_as_traded()

        assert card.status == Card.STATUS_TRADED
        assert card.updated_at > original_updated_at

    def test_mark_as_available(self):
        """Test marking card as available"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_TRADING)
        original_updated_at = card.updated_at

        card.mark_as_available()

        assert card.status == Card.STATUS_AVAILABLE
        assert card.updated_at > original_updated_at

    def test_cannot_trade_already_traded_card(self):
        """Test that a traded card cannot be marked as trading"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_TRADED)

        with pytest.raises(ValueError, match="Cannot trade an already traded card"):
            card.mark_as_trading()

    def test_cannot_make_traded_card_available(self):
        """Test that a traded card cannot be made available again"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_TRADED)

        with pytest.raises(
            ValueError, match="Cannot make a traded card available again"
        ):
            card.mark_as_available()

    def test_is_available(self):
        """Test is_available method"""
        owner_id = uuid4()

        available_card = Card(owner_id=owner_id, status=Card.STATUS_AVAILABLE)
        trading_card = Card(owner_id=owner_id, status=Card.STATUS_TRADING)
        traded_card = Card(owner_id=owner_id, status=Card.STATUS_TRADED)

        assert available_card.is_available() is True
        assert trading_card.is_available() is False
        assert traded_card.is_available() is False


class TestCardImageOperations:
    """Test card image update operations"""

    def test_update_image(self):
        """Test updating card image URL and size"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)
        original_updated_at = card.updated_at

        new_url = "https://storage.googleapis.com/kcardswap/cards/new.jpg"
        new_size = 2048000

        card.update_image(new_url, new_size)

        assert card.image_url == new_url
        assert card.size_bytes == new_size
        assert card.updated_at > original_updated_at

    def test_update_image_validates_size(self):
        """Test that update_image validates size_bytes"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        with pytest.raises(ValueError, match="size_bytes must be non-negative"):
            card.update_image("https://example.com/image.jpg", -100)


class TestCardEquality:
    """Test card equality and hashing"""

    def test_card_equality_by_id(self):
        """Test cards are equal if they have the same ID"""
        card_id = uuid4()
        owner_id1 = uuid4()
        owner_id2 = uuid4()

        card1 = Card(id=card_id, owner_id=owner_id1)
        card2 = Card(id=card_id, owner_id=owner_id2)
        card3 = Card(owner_id=owner_id1)

        assert card1 == card2  # Same ID
        assert card1 != card3  # Different ID

    def test_card_hash(self):
        """Test card can be hashed for use in sets and dicts"""
        card_id = uuid4()
        owner_id = uuid4()

        card1 = Card(id=card_id, owner_id=owner_id)
        card2 = Card(id=card_id, owner_id=owner_id)

        # Cards with same ID should have same hash
        assert hash(card1) == hash(card2)

        # Can be used in sets
        card_set = {card1, card2}
        assert len(card_set) == 1  # Same card

    def test_card_repr(self):
        """Test card string representation"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_AVAILABLE)

        repr_str = repr(card)

        assert "Card" in repr_str
        assert str(card.id) in repr_str
        assert str(owner_id) in repr_str
        assert "available" in repr_str


class TestCardConstants:
    """Test card constants are properly defined"""

    def test_valid_statuses(self):
        """Test valid status constants"""
        assert Card.STATUS_AVAILABLE == "available"
        assert Card.STATUS_TRADING == "trading"
        assert Card.STATUS_TRADED == "traded"
        assert len(Card.VALID_STATUSES) == 3
        assert Card.STATUS_AVAILABLE in Card.VALID_STATUSES
        assert Card.STATUS_TRADING in Card.VALID_STATUSES
        assert Card.STATUS_TRADED in Card.VALID_STATUSES

    def test_valid_rarities(self):
        """Test valid rarity constants"""
        assert Card.RARITY_COMMON == "common"
        assert Card.RARITY_RARE == "rare"
        assert Card.RARITY_EPIC == "epic"
        assert Card.RARITY_LEGENDARY == "legendary"
        assert len(Card.VALID_RARITIES) == 4
        assert Card.RARITY_COMMON in Card.VALID_RARITIES
        assert Card.RARITY_RARE in Card.VALID_RARITIES
        assert Card.RARITY_EPIC in Card.VALID_RARITIES
        assert Card.RARITY_LEGENDARY in Card.VALID_RARITIES
