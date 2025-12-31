# Social Module Infrastructure Tests

Comprehensive unit tests for all repository implementations in the social module infrastructure layer.

## Test Coverage

### Repository Tests (`tests/unit/social/infrastructure/repositories/`)

All repository implementations in `app/modules/social/infrastructure/repositories/` are now tested:

| Repository | Test File | Methods Tested |
|------------|-----------|----------------|
| `CardRepositoryImpl` | `test_card_repository_impl.py` | save, find_by_id, find_by_owner, delete, count_uploads_today, get_total_storage_used, find_by_status, find_nearby_cards |
| `ChatRoomRepositoryImpl` | `test_chat_room_repository_impl.py` | create, get_by_id, get_by_participants, get_rooms_by_user_id, delete, entity conversion |
| `FriendshipRepositoryImpl` | `test_friendship_repository_impl.py` | create, get_by_id, get_by_users, get_friends_by_user_id, update, delete, is_blocked, are_friends |
| `MessageRepositoryImpl` | `test_message_repository_impl.py` | create, get_by_id, get_messages_by_room_id, update, delete, get_unread_count_by_room_id, mark_messages_as_read |
| `RatingRepositoryImpl` | `test_rating_repository_impl.py` | create, get_by_id, get_by_trade_id, get_ratings_for_user, get_ratings_by_user, get_average_rating, has_user_rated_trade, delete |
| `ReportRepositoryImpl` | `test_report_repository_impl.py` | create, get_by_id, get_reports_by_reported_user_id, get_reports_by_reporter_id, get_unresolved_reports, update, get_report_count_by_user, delete |
| `TradeRepositoryImpl` | `test_trade_repository_impl.py` | create, get_by_id, get_items_by_trade_id, update, get_user_trades, get_active_trades_between_users, count_active_trades_between_users |

### Test Statistics

- **Total repository implementations**: 7
- **Total test files**: 7
- **Total test cases**: ~120+ tests
- **Coverage**: 100% of repository implementations

## What These Tests Verify

Each repository test suite verifies:

1. **Create Operations**: Entities are properly saved to the database
2. **Read Operations**: 
   - Finding by ID (found and not found cases)
   - Querying with filters
   - Aggregations (counts, averages)
3. **Update Operations**: Entities can be modified
4. **Delete Operations**: Entities can be removed
5. **Business Logic**: 
   - Special queries (e.g., `are_friends`, `is_blocked`, `get_nearby_cards`)
   - Cursor-based pagination
   - Bidirectional relationships
6. **Entity Conversion**: Proper conversion between domain entities and database models

## Why This Matters

### Previous State
- Only use case tests existed, which used mocked repositories
- No tests verified actual repository method implementations
- Integration bugs (like incorrect method names) went undetected

### Current State  
- All repository implementations are tested
- Method signatures are verified
- Entity conversions are validated
- Business logic in repositories is tested

### Benefits
1. **Catches Integration Bugs**: Verifies methods actually exist and work
2. **Validates Contracts**: Ensures implementations match interfaces
3. **Prevents Regressions**: Changes to repositories are validated
4. **Documents Behavior**: Tests serve as documentation for how repositories work

## Running Tests

### All Repository Tests
```bash
poetry run pytest tests/unit/social/infrastructure/repositories/ -v
```

### Specific Repository
```bash
poetry run pytest tests/unit/social/infrastructure/repositories/test_chat_room_repository_impl.py -v
```

### With Coverage
```bash
poetry run pytest tests/unit/social/infrastructure/repositories/ --cov=app.modules.social.infrastructure.repositories
```

## Test Structure

Each repository test follows this pattern:

```python
class TestXxxRepositoryImpl:
    """Test XxxRepositoryImpl"""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance"""
        return XxxRepositoryImpl(mock_session)
    
    @pytest.mark.asyncio
    async def test_method_name(self, repository, mock_session):
        """Test specific repository method"""
        # Arrange - set up mocks
        # Act - call the method
        # Assert - verify behavior
```

## Next Steps

For complete test coverage, consider adding:

1. **Integration Tests**: Test repositories with a real database
2. **Performance Tests**: Verify query performance with large datasets
3. **Error Handling Tests**: Test database error scenarios
4. **Transaction Tests**: Verify transaction handling and rollback

## Related Documentation

- [Chat Module Test Coverage](../application/use_cases/chat/README.md)
- [Social Module Architecture](../../../../../../docs/architecture/)
