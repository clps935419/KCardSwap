"""Integration tests for Posts V2: create and list with scope/category filtering

Tests FR-003, FR-004, FR-005:
- Create global posts
- Create city posts (with city_code)
- List global (includes all posts)
- List city-specific (only city posts)
- Category filtering
- Authentication required
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.posts.domain.entities.post_enums import PostCategory, PostScope


class TestPostsCreateAndListV2:
    """Test posts creation and listing with V2 features (scope/category)"""

    @pytest.mark.asyncio
    async def test_create_global_post(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test creating a global post (FR-003)"""
        payload = {
            "scope": "global",
            "category": "trade",
            "title": "Looking for BTS cards globally",
            "content": "I have duplicate Jungkook cards to trade",
        }

        response = await async_client.post(
            "/api/v1/posts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["scope"] == "global"
        assert data["city_code"] is None
        assert data["category"] == "trade"
        assert data["title"] == payload["title"]
        assert data["status"] == "open"

    @pytest.mark.asyncio
    async def test_create_city_post(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test creating a city post with city_code (FR-003, FR-004)"""
        payload = {
            "scope": "city",
            "city_code": "TPE",
            "category": "giveaway",
            "title": "Free cards in Taipei",
            "content": "Giving away duplicate cards",
        }

        response = await async_client.post(
            "/api/v1/posts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["scope"] == "city"
        assert data["city_code"] == "TPE"
        assert data["category"] == "giveaway"

    @pytest.mark.asyncio
    async def test_create_city_post_without_city_code_fails(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test that scope=city requires city_code (FR-004)"""
        payload = {
            "scope": "city",
            "category": "trade",
            "title": "Test",
            "content": "Test content",
        }

        response = await async_client.post(
            "/api/v1/posts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "city_code" in response.text.lower()

    @pytest.mark.asyncio
    async def test_create_global_post_with_city_code_fails(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test that scope=global must not have city_code (FR-004)"""
        payload = {
            "scope": "global",
            "city_code": "TPE",
            "category": "trade",
            "title": "Test",
            "content": "Test content",
        }

        response = await async_client.post(
            "/api/v1/posts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "city_code" in response.text.lower()

    @pytest.mark.asyncio
    async def test_list_global_includes_all_posts(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test that global list includes all posts (FR-005)"""
        # Create 1 global post
        await async_client.post(
            "/api/v1/posts",
            json={
                "scope": "global",
                "category": "trade",
                "title": "Global post",
                "content": "Content",
            },
            headers=auth_headers,
        )

        # Create 1 city post
        await async_client.post(
            "/api/v1/posts",
            json={
                "scope": "city",
                "city_code": "TPE",
                "category": "giveaway",
                "title": "Taipei post",
                "content": "Content",
            },
            headers=auth_headers,
        )

        # List without city_code (global view)
        response = await async_client.get(
            "/api/v1/posts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total"] >= 2
        
        # Should include both global and city posts
        scopes = [post["scope"] for post in data["posts"]]
        assert "global" in scopes
        assert "city" in scopes

    @pytest.mark.asyncio
    async def test_list_city_only_includes_city_posts(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test that city list only includes city-specific posts (FR-005)"""
        # Create posts for different cities
        await async_client.post(
            "/api/v1/posts",
            json={
                "scope": "city",
                "city_code": "TPE",
                "category": "trade",
                "title": "Taipei post",
                "content": "Content",
            },
            headers=auth_headers,
        )

        await async_client.post(
            "/api/v1/posts",
            json={
                "scope": "city",
                "city_code": "KHH",
                "category": "trade",
                "title": "Kaohsiung post",
                "content": "Content",
            },
            headers=auth_headers,
        )

        # List with city_code=TPE
        response = await async_client.get(
            "/api/v1/posts?city_code=TPE",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()["data"]
        
        # Should only include TPE posts
        for post in data["posts"]:
            assert post["city_code"] == "TPE"
            assert post["scope"] == "city"

    @pytest.mark.asyncio
    async def test_category_filtering(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test filtering by category (FR-002)"""
        # Create posts with different categories
        await async_client.post(
            "/api/v1/posts",
            json={
                "scope": "global",
                "category": "trade",
                "title": "Trade post",
                "content": "Content",
            },
            headers=auth_headers,
        )

        await async_client.post(
            "/api/v1/posts",
            json={
                "scope": "global",
                "category": "giveaway",
                "title": "Giveaway post",
                "content": "Content",
            },
            headers=auth_headers,
        )

        # Filter by category=trade
        response = await async_client.get(
            "/api/v1/posts?category=trade",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()["data"]
        
        # Should only include trade posts
        for post in data["posts"]:
            assert post["category"] == "trade"

    @pytest.mark.asyncio
    async def test_list_posts_requires_authentication(
        self,
        async_client: AsyncClient,
    ):
        """Test that listing posts requires login (FR-001)"""
        response = await async_client.get("/api/v1/posts")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_post_requires_authentication(
        self,
        async_client: AsyncClient,
    ):
        """Test that creating posts requires login (FR-001)"""
        payload = {
            "scope": "global",
            "category": "trade",
            "title": "Test",
            "content": "Test content",
        }

        response = await async_client.post(
            "/api/v1/posts",
            json=payload,
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_all_categories_are_valid(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test that all defined categories are accepted (FR-002)"""
        categories = ["trade", "giveaway", "group", "showcase", "help", "announcement"]
        
        for category in categories:
            payload = {
                "scope": "global",
                "category": category,
                "title": f"Test {category}",
                "content": "Test content",
            }

            response = await async_client.post(
                "/api/v1/posts",
                json=payload,
                headers=auth_headers,
            )

            assert response.status_code == 201
            data = response.json()["data"]
            assert data["category"] == category
