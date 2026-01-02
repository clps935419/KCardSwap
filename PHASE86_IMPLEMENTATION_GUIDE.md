# Phase 8.6 API Response Standardization - Implementation Guide

**Date**: 2026-01-02  
**Status**: In Progress (36% complete)  
**Assigned**: Development Team

## Overview

This document tracks the implementation of API Response Standardization across all backend modules and frontend integration.

## Completed Work ✅

### 1. Infrastructure (T1401, T1403, T1404)
- ✅ Created `/specs/001-kcardswap-complete-spec/response-format.md`
  - Comprehensive specification with examples
  - Error code standards
  - Migration strategy
  
- ✅ Created `/apps/backend/app/shared/presentation/schemas/response_envelope.py`
  - `ResponseEnvelope[T]` generic class
  - `SuccessResponse[T]`
  - `PaginatedResponse[T]`
  - `ErrorResponse`
  - `ErrorDetail` and `PaginationMeta` schemas

- ✅ Created `/apps/backend/app/shared/presentation/response.py`
  - `success(data)` helper
  - `paginated(data, total, page, page_size)` helper
  - `error_response(code, message, details)` helper

- ✅ Updated `/apps/backend/app/shared/presentation/middleware/error_handler.py`
  - All error handlers now return standardized envelope format
  - `{data: null, meta: null, error: {...}}`

### 2. Identity Module (T1405 - Partial)
- ✅ `auth_router.py` (4 endpoints)
  - POST /api/v1/auth/admin-login
  - POST /api/v1/auth/google-login
  - POST /api/v1/auth/google-callback
  - POST /api/v1/auth/refresh
  - All return `{data, meta: null, error: null}`

- ✅ `profile_router.py` (2 endpoints)
  - GET /api/v1/profile/me
  - PUT /api/v1/profile/me
  - All return `{data, meta: null, error: null}`

- ✅ Updated schemas:
  - `LoginResponse`: added `meta: None = None`
  - `ProfileResponseWrapper`: added `meta: None = None`
  - Removed `ErrorWrapper` classes

## Remaining Work 📋

### Phase 1: Complete Backend Standardization

#### T1405B: Identity - Subscription Router (Priority: High)
**File**: `apps/backend/app/modules/identity/presentation/routers/subscription_router.py`

**Endpoints to update**:
1. POST /api/v1/subscriptions/verify-receipt
2. GET /api/v1/subscriptions/status
3. POST /api/v1/subscriptions/expire-subscriptions (admin)

**Actions**:
- Update all response models to use envelope format
- Remove any direct dict returns
- Add `meta: None` to success responses
- Update response_model declarations

**Estimated Time**: 1 hour

#### T1406: Social Module - 7 Routers (Priority: High)
**Files**:
1. `apps/backend/app/modules/social/presentation/routers/cards_router.py`
2. `apps/backend/app/modules/social/presentation/routers/chat_router.py`
3. `apps/backend/app/modules/social/presentation/routers/friends_router.py`
4. `apps/backend/app/modules/social/presentation/routers/nearby_router.py`
5. `apps/backend/app/modules/social/presentation/routers/rating_router.py`
6. `apps/backend/app/modules/social/presentation/routers/report_router.py`
7. `apps/backend/app/modules/social/presentation/routers/trade_router.py`

**Pattern to follow**:
```python
# Before
return CardResponse(id=..., ...)

# After
from app.shared.presentation.response import success, paginated

# Single resource
return success(CardResponse(id=..., ...))

# List without pagination
return success([CardResponse(...), ...])

# List with pagination
return paginated(
    data=[CardResponse(...), ...],
    total=100,
    page=1,
    page_size=20
)
```

**Key points**:
- Update all schemas to use envelope
- Add pagination metadata to list endpoints
- Remove direct dict/model returns
- Update response_model declarations to envelope types

**Estimated Time**: 6-8 hours

#### T1407: Posts Module (Priority: High)
**File**: `apps/backend/app/modules/posts/presentation/routers/posts_router.py`

**Endpoints to update** (estimated 6-8):
- POST /api/v1/posts (create)
- GET /api/v1/posts (list - needs pagination)
- GET /api/v1/posts/{id} (detail)
- POST /api/v1/posts/{id}/interest
- POST /api/v1/posts/{id}/interests/{interest_id}/accept
- POST /api/v1/posts/{id}/interests/{interest_id}/reject
- POST /api/v1/posts/{id}/close
- GET /api/v1/posts/{id}/interests (list - needs pagination)

**Actions**:
- Update schemas to use envelope
- Add pagination to list endpoints
- Update all returns to use helpers
- Ensure meta field present

**Estimated Time**: 3-4 hours

#### T1407A: Locations Module (Priority: Medium)
**File**: `apps/backend/app/modules/locations/presentation/routers/location_router.py`

**Endpoints to update**:
- GET /api/v1/locations/cities

**Actions**:
- Simple list endpoint, wrap in envelope
- No pagination needed (small dataset)

**Estimated Time**: 30 minutes

### Phase 2: Testing Updates

#### T1408: Integration Tests (Priority: High)
**Files**: All `tests/integration/**/*.py` files

**Actions**:
1. Update all response assertions from:
   ```python
   assert response.json()["id"] == ...
   ```
   To:
   ```python
   data = response.json()
   assert data["error"] is None
   assert data["data"]["id"] == ...
   ```

2. Add pagination meta assertions for list endpoints:
   ```python
   data = response.json()
   assert data["meta"]["total"] == ...
   assert data["meta"]["page"] == 1
   assert data["meta"]["page_size"] == 20
   ```

3. Update error response assertions:
   ```python
   data = response.json()
   assert data["data"] is None
   assert data["error"]["code"] == "404_NOT_FOUND"
   ```

**Test Files to Update** (estimate):
- `tests/integration/modules/identity/test_auth_flow.py`
- `tests/integration/modules/identity/test_profile_flow.py`
- `tests/integration/modules/identity/test_subscription_flow.py`
- `tests/integration/modules/social/test_card_upload_flow.py`
- `tests/integration/modules/social/test_nearby_search_flow.py`
- `tests/integration/modules/social/test_posts_flow.py`
- All other integration tests

**Estimated Time**: 6-8 hours

### Phase 3: Documentation & OpenAPI

#### T1402: Backend Documentation (Priority: Medium)
**Files**:
- `apps/backend/README.md`
- `apps/backend/docs/api/README.md`

**Actions**:
1. Add "API Response Format" section
2. Include envelope structure example
3. Link to complete specification
4. Add code examples for success/error/pagination

**Content to add**:
```markdown
## API Response Format

All API endpoints return responses in a standardized envelope format:

\`\`\`json
{
  "data": <response_data> | null,
  "meta": <pagination_metadata> | null,
  "error": <error_object> | null
}
\`\`\`

See `/specs/001-kcardswap-complete-spec/response-format.md` for complete specification.
```

**Estimated Time**: 1 hour

#### T1409: OpenAPI Snapshot (Priority: Critical)
**Files**: 
- `openapi/openapi.json`
- `openapi/README.md`

**Actions**:
1. After ALL backend routers are updated, run:
   ```bash
   cd apps/backend
   python3 scripts/generate_openapi.py
   ```

2. Verify generated spec includes envelope format

3. Update `openapi/README.md` to note the new format version

4. Commit the updated `openapi/openapi.json`

**Important**: 
- ⚠️ Do NOT run this until all backend routers are updated
- This is a blocking step for mobile development
- Mobile SDK generation depends on this

**Estimated Time**: 30 minutes

### Phase 4: Mobile Updates

#### T1410: Regenerate Mobile SDK (Priority: Critical)
**Location**: `apps/mobile`

**Actions**:
1. After T1409 complete, run:
   ```bash
   cd apps/mobile
   npm run sdk:generate
   ```

2. Verify generated types include envelope structure

3. Update documentation:
   - `apps/mobile/README.md`
   - `apps/mobile/TECH_STACK.md`
   - `apps/mobile/OPENAPI_SDK_GUIDE.md`

4. Add section on handling envelope responses:
   ```typescript
   // Example usage
   const { data, error } = await getProfile();
   if (error) {
     // Handle error
     showError(error.message);
   } else {
     // Use data
     setProfile(data);
   }
   ```

**Estimated Time**: 2 hours

#### T1411: Update Mobile API Calls (Priority: High)
**Locations**: All `apps/mobile/src/features/*/hooks/*.ts` files

**Pattern**:
```typescript
// Before
const { data } = useQuery({
  queryFn: async () => {
    const response = await api.get('/cards/me');
    return response.data; // Direct access
  }
});

// After  
const { data } = useQuery({
  queryFn: async () => {
    const response = await api.get('/cards/me');
    if (response.error) {
      throw new Error(response.error.message);
    }
    return response.data; // Extract from envelope
  }
});

// For paginated endpoints
const { data } = useQuery({
  queryFn: async () => {
    const response = await api.get('/cards/me?page=1&page_size=20');
    if (response.error) throw new Error(response.error.message);
    return {
      items: response.data,
      total: response.meta.total,
      page: response.meta.page,
      totalPages: response.meta.total_pages
    };
  }
});
```

**Files to update** (estimate):
- `apps/mobile/src/features/auth/hooks/*.ts`
- `apps/mobile/src/features/profile/hooks/*.ts`
- `apps/mobile/src/features/cards/hooks/*.ts`
- `apps/mobile/src/features/chat/hooks/*.ts`
- `apps/mobile/src/features/friends/hooks/*.ts`
- `apps/mobile/src/features/posts/hooks/*.ts`
- `apps/mobile/src/features/trade/hooks/*.ts`
- `apps/mobile/src/features/subscription/hooks/*.ts`

**Estimated Time**: 8-10 hours

#### T1412: Update Error Handling (Priority: High)
**Files**:
- `apps/mobile/src/shared/api/errorMapper.ts`
- All feature components that display errors

**Actions**:
1. Update errorMapper to handle envelope error structure:
   ```typescript
   export const mapApiError = (response: any): string => {
     if (response.error) {
       const { code, message, details } = response.error;
       // Map error codes to user-friendly messages
       return errorMessages[code] || message;
     }
     return 'An unexpected error occurred';
   };
   ```

2. Update all error displays in components
3. Ensure loading/error/empty states work correctly

**Estimated Time**: 4-5 hours

#### T1413: Mobile Verification (Priority: High)
**Actions**:
1. Run type checking:
   ```bash
   cd apps/mobile
   npm run type-check
   ```

2. Run tests:
   ```bash
   npm run test
   ```

3. Manual testing checklist:
   - [ ] Login/Logout flow
   - [ ] Profile view/edit
   - [ ] Cards list (with pagination)
   - [ ] Card upload
   - [ ] Posts list (with pagination)
   - [ ] Chat messages (with pagination)
   - [ ] Trade history (with pagination)
   - [ ] Error messages display correctly
   - [ ] Loading states work
   - [ ] Empty states work

**Estimated Time**: 4-5 hours

## Total Estimated Time

- **Backend**: 12-15 hours
- **Tests**: 7-9 hours
- **Mobile**: 18-22 hours
- **Documentation**: 1.5 hours

**Total**: 38-47 hours (approximately 5-6 working days)

## Critical Path

1. Complete all backend routers (T1405B, T1406, T1407, T1407A)
2. Update integration tests (T1408)
3. Generate OpenAPI snapshot (T1409) ⚠️ **BLOCKING POINT**
4. Regenerate Mobile SDK (T1410)
5. Update Mobile code (T1411, T1412)
6. Test and verify (T1413)

## Risk Mitigation

### Breaking Change Management
- ⚠️ This is a breaking change for all API consumers
- Backend and Mobile must be deployed together
- Consider feature flags if gradual rollout needed

### Testing Strategy
- Update tests incrementally as routers are updated
- Run full integration test suite before OpenAPI generation
- Mobile tests after SDK regeneration

### Rollback Plan
- Keep previous OpenAPI snapshot as backup
- Document rollback steps in case of issues
- Have rollback deployment ready

## Success Criteria

- [ ] All backend endpoints return standardized envelope
- [ ] All integration tests pass with new format
- [ ] OpenAPI spec reflects new format
- [ ] Mobile SDK successfully generated
- [ ] All Mobile API calls updated
- [ ] Mobile app builds and runs without errors
- [ ] Manual testing checklist 100% complete
- [ ] Documentation updated

## Notes

- Error handler middleware is complete - it will automatically wrap any exceptions in envelope format
- Use helper functions (`success`, `paginated`) for consistency
- For pagination, always include meta with total, page, page_size, total_pages
- Keep error codes consistent with specification (format: `{HTTP_STATUS}_{ERROR_TYPE}`)

## Contact

For questions or clarifications:
- Refer to `/specs/001-kcardswap-complete-spec/response-format.md`
- Check completed examples in auth_router.py and profile_router.py
- Review response.py helper functions for usage patterns
