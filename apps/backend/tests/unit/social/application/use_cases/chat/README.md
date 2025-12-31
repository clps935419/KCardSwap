# Chat Module Test Coverage

This directory contains comprehensive tests for the chat functionality, covering all layers from domain entities to API endpoints.

## Test Structure

### Unit Tests

#### 1. Use Case Tests (`tests/unit/social/application/use_cases/chat/`)
- `test_get_messages_use_case.py` - Tests message retrieval business logic
- `test_send_message_use_case.py` - Tests message sending business logic

These tests verify that use cases correctly:
- Validate business rules (friendship, blocking)
- Handle authorization checks
- Coordinate between repositories

#### 2. Repository Tests (`tests/unit/social/infrastructure/repositories/`)
- `test_chat_room_repository_impl.py` - Tests ChatRoomRepositoryImpl

These tests verify that the repository:
- Correctly implements the interface methods (e.g., `get_rooms_by_user_id`)
- Properly converts between domain entities and database models
- Handles database operations correctly

**Key Test: `test_get_rooms_by_user_id_with_results`**
- Ensures the `get_rooms_by_user_id()` method exists and works correctly
- This test would have caught the original bug where `find_by_user()` was called

### Integration Tests

#### 3. Router Integration Tests (`tests/integration/modules/social/`)
- `test_chat_flow.py` - Tests complete chat router flow

These tests verify that the router:
- Calls the correct repository methods
- Accesses entity attributes properly (e.g., `participant_ids` not `user_a_id`/`user_b_id`)
- Constructs response schemas correctly
- Handles errors appropriately

**Key Tests:**
- `test_get_chat_rooms_repository_method_name` - Verifies `get_rooms_by_user_id()` is called
- `test_get_chat_rooms_participant_ids_iteration` - Verifies `participant_ids` is accessed correctly

## What Was Fixed

The original bug had two issues in `chat_router.py`:

1. **Wrong method name**: Called `find_by_user()` instead of `get_rooms_by_user_id()`
2. **Wrong attributes**: Accessed `room.user_a_id` and `room.user_b_id` instead of `room.participant_ids`

## Test Coverage Summary

| Layer | Component | Test Type | File |
|-------|-----------|-----------|------|
| Domain | ChatRoom Entity | Unit | (implicit in repository tests) |
| Application | GetMessagesUseCase | Unit | `test_get_messages_use_case.py` |
| Application | SendMessageUseCase | Unit | `test_send_message_use_case.py` |
| Infrastructure | ChatRoomRepositoryImpl | Unit | `test_chat_room_repository_impl.py` |
| Presentation | Chat Router | Integration | `test_chat_flow.py` |

## Running Tests

### All Chat Tests
```bash
# With Poetry
poetry run pytest tests/unit/social/application/use_cases/chat/ tests/unit/social/infrastructure/repositories/test_chat_room_repository_impl.py tests/integration/modules/social/test_chat_flow.py -v

# Or just the chat-related tests
poetry run pytest -k "chat" -v
```

### Repository Tests Only
```bash
poetry run pytest tests/unit/social/infrastructure/repositories/test_chat_room_repository_impl.py -v
```

### Integration Tests Only
```bash
poetry run pytest tests/integration/modules/social/test_chat_flow.py -v
```

## Why These Tests Matter

1. **Use Case Tests** - Verify business logic is correct but use mocks, so they don't catch implementation bugs
2. **Repository Tests** - Verify the actual repository implementation methods exist and work
3. **Integration Tests** - Verify the router correctly wires everything together

**The original bug was only caught by integration tests because:**
- Use case tests mocked the repository, so they didn't care about actual method names
- Repository tests verify the implementation exists
- Integration tests verify the router calls the right methods on the real implementation

This demonstrates why comprehensive testing at all layers is essential!
