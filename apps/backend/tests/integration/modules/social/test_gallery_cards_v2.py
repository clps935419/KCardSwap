"""
Integration tests for Gallery Cards CRUD and reorder operations.
Tests for User Story 2: Manage personal gallery cards and view others' galleries.
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestGalleryCardsCRUD:
    """Test gallery cards creation, retrieval, update, and deletion."""

    async def test_create_gallery_card_success(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test creating a gallery card successfully."""
        # Arrange
        card_data = {
            "title": "My First Card",
            "description": "A beautiful card",
            "idol_name": "IU",
            "era": "Love Poem",
        }

        # Act
        response = await async_client.post(
            "/api/v1/gallery/cards",
            json=card_data,
            headers=auth_headers_user1,
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == card_data["title"]
        assert data["description"] == card_data["description"]
        assert data["idol_name"] == card_data["idol_name"]
        assert data["era"] == card_data["era"]
        assert "id" in data
        assert "user_id" in data
        assert "display_order" in data
        assert "created_at" in data

    async def test_get_my_gallery_cards(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test retrieving my own gallery cards."""
        # Arrange - Create 3 cards
        cards_data = [
            {"title": f"Card {i}", "idol_name": "IU", "era": f"Era {i}"}
            for i in range(1, 4)
        ]
        
        for card_data in cards_data:
            await async_client.post(
                "/api/v1/gallery/cards",
                json=card_data,
                headers=auth_headers_user1,
            )

        # Act
        response = await async_client.get(
            "/api/v1/gallery/cards/me",
            headers=auth_headers_user1,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert all(card["title"] in ["Card 1", "Card 2", "Card 3"] for card in data["items"])

    async def test_get_user_gallery_cards(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        auth_headers_user2: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test viewing another user's gallery cards."""
        # Arrange - User1 creates cards
        card_data = {"title": "User1 Card", "idol_name": "IU", "era": "Love Poem"}
        create_response = await async_client.post(
            "/api/v1/gallery/cards",
            json=card_data,
            headers=auth_headers_user1,
        )
        assert create_response.status_code == 201
        user1_id = create_response.json()["user_id"]

        # Act - User2 views User1's gallery
        response = await async_client.get(
            f"/api/v1/users/{user1_id}/gallery/cards",
            headers=auth_headers_user2,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert any(card["title"] == "User1 Card" for card in data["items"])

    async def test_delete_gallery_card_success(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test deleting a gallery card."""
        # Arrange - Create a card
        card_data = {"title": "To Delete", "idol_name": "IU", "era": "Love Poem"}
        create_response = await async_client.post(
            "/api/v1/gallery/cards",
            json=card_data,
            headers=auth_headers_user1,
        )
        assert create_response.status_code == 201
        card_id = create_response.json()["id"]

        # Act
        delete_response = await async_client.delete(
            f"/api/v1/gallery/cards/{card_id}",
            headers=auth_headers_user1,
        )

        # Assert
        assert delete_response.status_code == 204

        # Verify card is deleted
        get_response = await async_client.get(
            "/api/v1/gallery/cards/me",
            headers=auth_headers_user1,
        )
        assert get_response.status_code == 200
        cards = get_response.json()["items"]
        assert not any(card["id"] == card_id for card in cards)

    async def test_delete_gallery_card_not_owner(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        auth_headers_user2: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test that users cannot delete other users' cards."""
        # Arrange - User1 creates a card
        card_data = {"title": "User1 Card", "idol_name": "IU", "era": "Love Poem"}
        create_response = await async_client.post(
            "/api/v1/gallery/cards",
            json=card_data,
            headers=auth_headers_user1,
        )
        assert create_response.status_code == 201
        card_id = create_response.json()["id"]

        # Act - User2 tries to delete User1's card
        delete_response = await async_client.delete(
            f"/api/v1/gallery/cards/{card_id}",
            headers=auth_headers_user2,
        )

        # Assert
        assert delete_response.status_code == 403


@pytest.mark.asyncio
class TestGalleryCardsReorder:
    """Test gallery cards reordering functionality."""

    async def test_reorder_gallery_cards_success(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test reordering gallery cards."""
        # Arrange - Create 3 cards
        card_ids = []
        for i in range(1, 4):
            card_data = {"title": f"Card {i}", "idol_name": "IU", "era": f"Era {i}"}
            response = await async_client.post(
                "/api/v1/gallery/cards",
                json=card_data,
                headers=auth_headers_user1,
            )
            assert response.status_code == 201
            card_ids.append(response.json()["id"])

        # Act - Reorder cards (reverse order)
        reorder_data = {"card_ids": list(reversed(card_ids))}
        reorder_response = await async_client.put(
            "/api/v1/gallery/cards/reorder",
            json=reorder_data,
            headers=auth_headers_user1,
        )

        # Assert
        assert reorder_response.status_code == 200

        # Verify new order
        get_response = await async_client.get(
            "/api/v1/gallery/cards/me",
            headers=auth_headers_user1,
        )
        assert get_response.status_code == 200
        cards = get_response.json()["items"]
        
        # Cards should be in the new order (reversed)
        returned_ids = [card["id"] for card in cards]
        assert returned_ids[:3] == list(reversed(card_ids))

    async def test_reorder_gallery_cards_partial_list(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test reordering with only some card IDs provided."""
        # Arrange - Create 3 cards
        card_ids = []
        for i in range(1, 4):
            card_data = {"title": f"Card {i}", "idol_name": "IU", "era": f"Era {i}"}
            response = await async_client.post(
                "/api/v1/gallery/cards",
                json=card_data,
                headers=auth_headers_user1,
            )
            assert response.status_code == 201
            card_ids.append(response.json()["id"])

        # Act - Reorder only first 2 cards
        reorder_data = {"card_ids": [card_ids[1], card_ids[0]]}
        reorder_response = await async_client.put(
            "/api/v1/gallery/cards/reorder",
            json=reorder_data,
            headers=auth_headers_user1,
        )

        # Assert
        assert reorder_response.status_code == 200

        # Verify cards are reordered (first two swapped, third remains at end)
        get_response = await async_client.get(
            "/api/v1/gallery/cards/me",
            headers=auth_headers_user1,
        )
        assert get_response.status_code == 200
        cards = get_response.json()["items"]
        returned_ids = [card["id"] for card in cards]
        
        # First two should be swapped
        assert returned_ids[0] == card_ids[1]
        assert returned_ids[1] == card_ids[0]

    async def test_reorder_gallery_cards_not_owner(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
        auth_headers_user2: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test that users cannot reorder other users' cards."""
        # Arrange - User1 creates cards
        card_ids = []
        for i in range(1, 3):
            card_data = {"title": f"Card {i}", "idol_name": "IU", "era": f"Era {i}"}
            response = await async_client.post(
                "/api/v1/gallery/cards",
                json=card_data,
                headers=auth_headers_user1,
            )
            assert response.status_code == 201
            card_ids.append(response.json()["id"])

        # Act - User2 tries to reorder User1's cards
        reorder_data = {"card_ids": list(reversed(card_ids))}
        reorder_response = await async_client.put(
            "/api/v1/gallery/cards/reorder",
            json=reorder_data,
            headers=auth_headers_user2,
        )

        # Assert
        assert reorder_response.status_code in [400, 403, 404]


@pytest.mark.asyncio
class TestGalleryCardsEdgeCases:
    """Test edge cases and error conditions."""

    async def test_create_gallery_card_missing_required_fields(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
    ):
        """Test creating a gallery card with missing required fields."""
        # Act
        response = await async_client.post(
            "/api/v1/gallery/cards",
            json={"title": "Incomplete Card"},
            headers=auth_headers_user1,
        )

        # Assert
        assert response.status_code == 400

    async def test_get_gallery_cards_requires_authentication(
        self,
        async_client: AsyncClient,
    ):
        """Test that viewing gallery requires authentication."""
        # Act
        response = await async_client.get("/api/v1/gallery/cards/me")

        # Assert
        assert response.status_code == 401

    async def test_delete_nonexistent_gallery_card(
        self,
        async_client: AsyncClient,
        auth_headers_user1: dict[str, str],
    ):
        """Test deleting a card that doesn't exist."""
        # Act
        response = await async_client.delete(
            f"/api/v1/gallery/cards/{uuid4()}",
            headers=auth_headers_user1,
        )

        # Assert
        assert response.status_code == 404
