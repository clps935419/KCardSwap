"""
Integration tests for post likes (T067: create/delete/idempotent behavior)
Tests FR-008, FR-009 - Like functionality with accurate count and no duplicate counting
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_like_post_success(
    client: AsyncClient,
    auth_headers_user1: dict,
    sample_post_id: str,
):
    """Test successfully liking a post"""
    # Like the post
    response = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["liked"] is True
    assert data["like_count"] == 1


@pytest.mark.asyncio
async def test_unlike_post_success(
    client: AsyncClient,
    auth_headers_user1: dict,
    sample_post_id: str,
):
    """Test successfully unliking a post"""
    # First like the post
    await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )

    # Then unlike it
    response = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["liked"] is False
    assert data["like_count"] == 0


@pytest.mark.asyncio
async def test_like_unlike_like_idempotent(
    client: AsyncClient,
    auth_headers_user1: dict,
    sample_post_id: str,
):
    """
    Independent Test from spec: Like → Unlike → Like should work correctly
    Tests idempotent behavior and accurate count (FR-009)
    """
    # Like
    response1 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response1.status_code == 200
    assert response1.json()["data"]["liked"] is True
    assert response1.json()["data"]["like_count"] == 1

    # Unlike
    response2 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response2.status_code == 200
    assert response2.json()["data"]["liked"] is False
    assert response2.json()["data"]["like_count"] == 0

    # Like again
    response3 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response3.status_code == 200
    assert response3.json()["data"]["liked"] is True
    assert response3.json()["data"]["like_count"] == 1


@pytest.mark.asyncio
async def test_multiple_users_like_same_post(
    client: AsyncClient,
    auth_headers_user1: dict,
    auth_headers_user2: dict,
    sample_post_id: str,
):
    """Test that multiple users can like the same post and count is accurate"""
    # User 1 likes
    response1 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response1.status_code == 200
    assert response1.json()["data"]["like_count"] == 1

    # User 2 likes
    response2 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user2,
    )
    assert response2.status_code == 200
    assert response2.json()["data"]["like_count"] == 2

    # User 1 unlikes
    response3 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response3.status_code == 200
    assert response3.json()["data"]["like_count"] == 1


@pytest.mark.asyncio
async def test_like_count_in_post_list(
    client: AsyncClient,
    auth_headers_user1: dict,
    auth_headers_user2: dict,
    sample_post_id: str,
):
    """Test that like_count and liked_by_me appear correctly in post list"""
    # User 1 likes the post
    await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )

    # User 2 likes the post
    await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user2,
    )

    # User 1 lists posts - should see liked_by_me=True and like_count=2
    response1 = await client.get(
        "/api/v1/posts",
        headers=auth_headers_user1,
    )
    assert response1.status_code == 200
    posts1 = response1.json()["data"]["posts"]
    post1 = next((p for p in posts1 if p["id"] == sample_post_id), None)
    assert post1 is not None
    assert post1["like_count"] == 2
    assert post1["liked_by_me"] is True

    # User 2 lists posts - should see liked_by_me=True and like_count=2
    response2 = await client.get(
        "/api/v1/posts",
        headers=auth_headers_user2,
    )
    assert response2.status_code == 200
    posts2 = response2.json()["data"]["posts"]
    post2 = next((p for p in posts2 if p["id"] == sample_post_id), None)
    assert post2 is not None
    assert post2["like_count"] == 2
    assert post2["liked_by_me"] is True


@pytest.mark.asyncio
async def test_like_post_not_found(
    client: AsyncClient,
    auth_headers_user1: dict,
):
    """Test liking a non-existent post returns 404"""
    fake_post_id = str(uuid4())
    response = await client.post(
        f"/api/v1/posts/{fake_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_like_post_unauthorized(
    client: AsyncClient,
    sample_post_id: str,
):
    """Test liking without authentication returns 401"""
    response = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_like_does_not_duplicate_count(
    client: AsyncClient,
    auth_headers_user1: dict,
    sample_post_id: str,
):
    """
    Test FR-009: One like per user per post (no duplicate counting)
    Multiple like attempts should not increase count
    """
    # Like once
    response1 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response1.json()["data"]["like_count"] == 1

    # Unlike
    await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )

    # Like again
    response2 = await client.post(
        f"/api/v1/posts/{sample_post_id}/like",
        headers=auth_headers_user1,
    )
    assert response2.json()["data"]["like_count"] == 1

    # Count should still be 1 (not 2)
    response3 = await client.get(
        "/api/v1/posts",
        headers=auth_headers_user1,
    )
    posts = response3.json()["data"]["posts"]
    post = next((p for p in posts if p["id"] == sample_post_id), None)
    assert post["like_count"] == 1
