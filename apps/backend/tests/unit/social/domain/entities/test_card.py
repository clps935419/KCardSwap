"""
Unit tests for Card entity
"""

from datetime import datetime
from uuid import uuid4

import pytest

from app.modules.social.domain.entities.card import Card


class TestCardEntity:
    """Test Card entity business logic"""

    def test_create_card_with_required_fields(self):
        """Test creating a card with only required fields"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        assert card.owner_id == owner_id
        assert card.status == Card.STATUS_AVAILABLE
        assert card.upload_status == Card.UPLOAD_STATUS_PENDING
        assert card.upload_confirmed_at is None
        assert card.id is not None
        assert card.created_at is not None
        assert card.updated_at is not None

    def test_create_card_with_all_fields(self):
        """Test creating a card with all fields"""
        card_id = uuid4()
        owner_id = uuid4()
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
            image_url="https://storage.googleapis.com/bucket/path/image.jpg",
            size_bytes=1024 * 500,  # 500KB
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
        assert card.upload_status == Card.UPLOAD_STATUS_PENDING
        assert card.image_url == "https://storage.googleapis.com/bucket/path/image.jpg"
        assert card.size_bytes == 1024 * 500

    def test_create_card_without_owner_id_raises_error(self):
        """Test that creating a card without owner_id raises ValueError"""
        with pytest.raises(ValueError, match="owner_id is required"):
            Card(owner_id=None)

    def test_create_card_with_invalid_status_raises_error(self):
        """Test that creating a card with invalid status raises ValueError"""
        owner_id = uuid4()
        with pytest.raises(ValueError, match="Invalid status"):
            Card(owner_id=owner_id, status="invalid_status")

    def test_create_card_with_invalid_upload_status_raises_error(self):
        """Test that creating a card with invalid upload_status raises ValueError"""
        owner_id = uuid4()
        with pytest.raises(ValueError, match="Invalid upload_status"):
            Card(owner_id=owner_id, upload_status="invalid_upload_status")

    def test_create_card_with_invalid_rarity_raises_error(self):
        """Test that creating a card with invalid rarity raises ValueError"""
        owner_id = uuid4()
        with pytest.raises(ValueError, match="Invalid rarity"):
            Card(owner_id=owner_id, rarity="invalid_rarity")

    def test_create_card_with_negative_size_raises_error(self):
        """Test that creating a card with negative size raises ValueError"""
        owner_id = uuid4()
        with pytest.raises(ValueError, match="size_bytes must be non-negative"):
            Card(owner_id=owner_id, size_bytes=-1)

    def test_is_available(self):
        """Test is_available method"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_AVAILABLE)
        assert card.is_available() is True

        card_trading = Card(owner_id=owner_id, status=Card.STATUS_TRADING)
        assert card_trading.is_available() is False

    def test_mark_as_trading(self):
        """Test marking card as trading"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        card.mark_as_trading()
        assert card.status == Card.STATUS_TRADING

    def test_mark_as_traded(self):
        """Test marking card as traded"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        card.mark_as_traded()
        assert card.status == Card.STATUS_TRADED

    def test_mark_as_available(self):
        """Test marking card as available"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_TRADING)

        card.mark_as_available()
        assert card.status == Card.STATUS_AVAILABLE

    def test_cannot_trade_already_traded_card(self):
        """Test that marking a traded card as trading raises ValueError"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_TRADED)

        with pytest.raises(ValueError, match="Cannot trade an already traded card"):
            card.mark_as_trading()

    def test_cannot_make_traded_card_available(self):
        """Test that marking a traded card as available raises ValueError"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id, status=Card.STATUS_TRADED)

        with pytest.raises(
            ValueError, match="Cannot make a traded card available again"
        ):
            card.mark_as_available()

    def test_update_image(self):
        """Test updating card image"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        image_url = "https://storage.googleapis.com/bucket/path/new_image.jpg"
        size_bytes = 1024 * 300  # 300KB

        card.update_image(image_url, size_bytes)
        assert card.image_url == image_url
        assert card.size_bytes == size_bytes

    def test_update_image_with_negative_size_raises_error(self):
        """Test that updating image with negative size raises ValueError"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        with pytest.raises(ValueError, match="size_bytes must be non-negative"):
            card.update_image("https://example.com/image.jpg", -1)

    def test_confirm_upload(self):
        """Test confirming card upload"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        assert card.upload_status == Card.UPLOAD_STATUS_PENDING
        assert card.upload_confirmed_at is None

        card.confirm_upload()

        assert card.upload_status == Card.UPLOAD_STATUS_CONFIRMED
        assert card.upload_confirmed_at is not None
        assert card.is_upload_confirmed() is True

    def test_cannot_confirm_already_confirmed_upload(self):
        """Test that confirming an already confirmed upload raises ValueError"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        card.confirm_upload()

        with pytest.raises(ValueError, match="Upload already confirmed"):
            card.confirm_upload()

    def test_is_upload_confirmed(self):
        """Test is_upload_confirmed method"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        assert card.is_upload_confirmed() is False

        card.confirm_upload()
        assert card.is_upload_confirmed() is True

    def test_card_equality(self):
        """Test card equality based on ID"""
        card_id = uuid4()
        owner_id = uuid4()

        card1 = Card(id=card_id, owner_id=owner_id)
        card2 = Card(id=card_id, owner_id=owner_id)
        card3 = Card(id=uuid4(), owner_id=owner_id)

        assert card1 == card2
        assert card1 != card3
        assert card1 != "not a card"

    def test_card_hash(self):
        """Test card hashing based on ID"""
        card_id = uuid4()
        owner_id = uuid4()

        card1 = Card(id=card_id, owner_id=owner_id)
        card2 = Card(id=card_id, owner_id=owner_id)

        assert hash(card1) == hash(card2)

        # Can use cards in sets
        card_set = {card1, card2}
        assert len(card_set) == 1

    def test_card_repr(self):
        """Test card string representation"""
        owner_id = uuid4()
        card = Card(owner_id=owner_id)

        repr_str = repr(card)
        assert "Card" in repr_str
        assert str(card.id) in repr_str
        assert str(owner_id) in repr_str
        assert card.status in repr_str
