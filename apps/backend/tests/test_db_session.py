"""
Test database session fixture with transaction rollback.

This test verifies that:
1. The db_session fixture uses the test database
2. Changes are automatically rolled back after each test
3. Multiple tests don't interfere with each other
"""

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_db_session_basic(db_session):
    """Test that db_session connects to the database."""
    result = await db_session.execute(text("SELECT 1 as value"))
    row = result.fetchone()
    assert row[0] == 1


@pytest.mark.asyncio
async def test_db_session_test_database(db_session):
    """Verify we're using the test database."""
    result = await db_session.execute(text("SELECT current_database()"))
    database_name = result.scalar()
    assert database_name == "kcardswap_test"


@pytest.mark.asyncio
async def test_transaction_rollback_part1(db_session):
    """Insert a user and verify it exists (will be rolled back)."""
    # Insert a test user
    await db_session.execute(
        text(
            """
            INSERT INTO users (google_id, email, role)
            VALUES (:google_id, :email, :role)
            """
        ),
        {
            "google_id": "test_rollback_123",
            "email": "rollback@test.com",
            "role": "user",
        },
    )
    await db_session.flush()

    # Verify the user exists in this transaction
    result = await db_session.execute(
        text("SELECT COUNT(*) FROM users WHERE google_id = :google_id"),
        {"google_id": "test_rollback_123"},
    )
    count = result.scalar()
    assert count == 1


@pytest.mark.asyncio
async def test_transaction_rollback_part2(db_session):
    """Verify that data from previous test was rolled back."""
    # Check that the user from previous test doesn't exist
    result = await db_session.execute(
        text("SELECT COUNT(*) FROM users WHERE google_id = :google_id"),
        {"google_id": "test_rollback_123"},
    )
    count = result.scalar()
    assert count == 0, "Previous test's data should have been rolled back"
