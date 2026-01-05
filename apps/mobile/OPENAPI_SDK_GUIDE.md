# OpenAPI SDK Generation Guide

## Overview

This project uses **hey-api/openapi-ts** to generate a type-safe TypeScript SDK from the backend's OpenAPI specification. The SDK includes:

- **Axios client** for HTTP requests
- **TanStack Query query/mutation options** for React components
- **Full TypeScript types** for all endpoints

## Architecture

### Key Files

```
├── openapi/
│   └── openapi.json                    # OpenAPI snapshot (generated from backend code; not a pre-dev contract)
├── apps/mobile/
│   ├── openapi-ts.config.ts           # hey-api configuration
│   ├── src/shared/api/
│   │   ├── sdk.ts                     # Runtime configuration & exports
│   │   └── generated/                 # Generated SDK (committed; treat as dependency)
│   │       ├── @tanstack/
│   │       │   └── react-query.gen.ts # TanStack Query options/mutations
│   │       ├── client/                # Client implementation
│   │       ├── sdk.gen.ts             # API functions
│   │       └── types.gen.ts           # TypeScript types
```

### Why OpenAPI Snapshot in Repo?

We commit an **OpenAPI snapshot** generated from backend code because:

1. **CI/CD Reliability**: No dependency on a running backend during mobile builds
2. **Cloud Agent Compatible**: Agents can generate SDK without network access
3. **Version Control**: API schema changes are visible in git diffs
4. **Offline Development**: Developers can work without running backend locally
5. **Faster Builds**: No need to wait for backend startup

> Note: This snapshot reflects the **implemented API** at the time it was generated. Product requirements still come from the User Stories / spec / plan / tasks.

> Important: The snapshot can be **stale** if the backend changed (or documents/tasks changed) but `openapi/openapi.json` was not regenerated and committed yet. Do not use the snapshot to infer product requirements or completion status; use it for deterministic SDK generation and verification only.

## Subscriptions (US6) Note

- `POST /api/v1/subscriptions/verify-receipt` 與 `GET /api/v1/subscriptions/status` 會在後端端點實作完成後，透過 `make generate-openapi` 生成並更新到 `openapi/openapi.json`。
- **禁止手動編輯** `openapi/openapi.json` 來「先加端點」：snapshot 必須反映實作。
- Mobile 端呼叫仍必須遵循本文件規範：使用 generated TanStack Query options/mutations；並以 `verify-receipt` 回傳的 `entitlement_active` 作為「購買成功」判準。

## Usage

### 1. Generating the SDK

```bash
cd apps/mobile

# Generate SDK from OpenAPI snapshot
npm run sdk:generate

# Clean generated files (before regenerating)
npm run sdk:clean
```

**重要規則**：
- 生成輸出（`src/shared/api/generated/`）會被提交進 repo（方便單人開發與 CI）
- **嚴格禁止手動修改** generated 檔案
- 任何變更必須透過更新 `openapi/openapi.json` 後再執行 `sdk:generate`
- generated 檔案視為 dependency，如同 node_modules

### 2. Configuring the SDK (One-time setup)

In your app's root component (`app/_layout.tsx`):

```typescript
import { configureSDK } from '@/src/shared/api/sdk';

export default function RootLayout() {
  // Configure SDK once at app startup
  useEffect(() => {
    configureSDK();
  }, []);

  return (
    // Your app layout
  );
}
```

### 3. Using the SDK in Components

**重要規範：僅使用 TanStack Query Options/Mutations**

本專案**禁止**直接呼叫 SDK 函式（如 `getMyProfile()`），**必須**使用 TanStack Query options/mutations 搭配 `useQuery` / `useMutation`。

#### ✅ 正確用法：TanStack Query Options (Required)

```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { getGetProfileMeQueryOptions, useUpdateProfileMeMutation } from '@/src/shared/api/sdk';
import { Box, Button, ButtonText, Spinner, Text } from '@/src/shared/ui/components';

function ProfileScreen() {
  // 使用 generated query options
  const { data, isLoading, error } = useQuery(getGetProfileMeQueryOptions());

  // 使用 generated mutation hook
  const updateProfile = useUpdateProfileMeMutation();

  const handleUpdate = async () => {
    await updateProfile.mutateAsync({
      body: {
        nickname: 'New Name',
        bio: 'Updated bio',
      },
    });
  };

  if (isLoading) return <Spinner />;
  if (error) return <Text>載入失敗</Text>;

  // Phase 8.6+: 從 envelope 提取資料
  const profile = data?.data; // data 是 ProfileResponseWrapper，data.data 是 ProfileResponse

  return (
    <Box>
      <Text>{profile?.nickname}</Text>
      <Button onPress={handleUpdate}>
        <ButtonText>Update</ButtonText>
      </Button>
    </Box>
  );
}
```

#### ❌ 錯誤用法：禁止直接呼叫 SDK 函式

```typescript
// ❌ 禁止這樣使用
import { getMyProfile, updateMyProfile } from '@/src/shared/api/sdk';

async function fetchProfile() {
  const response = await getMyProfile(); // ❌ 不允許
  return response.data;
}
```

#### 例外：Signed URL 直傳（不經過後端 API）

```typescript
// ✅ Signed URL 上傳必須使用獨立 fetch()
async function uploadToSignedUrl(url: string, file: Blob, headers: Record<string, string>) {
  const response = await fetch(url, {
    method: 'PUT',
    headers, // 使用後端回傳的 required_headers
    body: file,
  });
  
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }
}
```

## API Response Envelope Format (Phase 8.6+)

### Overview

All backend APIs now return responses in a standardized **envelope format**:

```typescript
{
  data: T | T[] | null,     // The actual data payload
  meta: {                   // Pagination metadata (for list endpoints only)
    total: number,
    page: number,
    page_size: number,
    total_pages: number
  } | null,
  error: {                  // Error details (when request fails)
    code: string,
    message: string,
    details: object
  } | null
}
```

### Generated Wrapper Types

The SDK automatically generates `*ResponseWrapper` types for all endpoints:

- `ProfileResponseWrapper` - wraps `ProfileResponse`
- `CardListResponseWrapper` - wraps `CardResponse[]`
- `TradeHistoryResponseWrapper` - wraps `TradeHistoryResponse`
- etc.

### Extracting Data from Envelopes

#### In Query Hooks

```typescript
// Example: Profile query
const result = useQuery({
  ...getMyProfileOptions(),
});

// Extract the actual profile from envelope
const profile = result.data?.data; // Type: ProfileResponse | undefined

// In a transformed hook
export function useMyProfile() {
  const result = useQuery(getMyProfileOptions());
  
  return {
    ...result,
    data: result.data?.data, // Extract ProfileResponse from ProfileResponseWrapper
  };
}
```

#### In Mutation Hooks

```typescript
// Example: Trade mutation
export function useAcceptTrade() {
  return useMutation({
    mutationFn: async (tradeId: string) => {
      const response = await acceptTradeMutation().mutationFn({ 
        path: { trade_id: tradeId } 
      });
      
      // Extract data from envelope
      return response?.data as TradeResponse;
    },
  });
}
```

#### With List Endpoints

```typescript
// List endpoints return array directly in data
const result = useQuery(getMyCardsOptions());

// CardListResponseWrapper.data is already CardResponse[]
const cards = result.data?.data || [];

// Pagination metadata is in meta (if backend provides it)
const totalCards = result.data?.meta?.total;
```

### Error Handling with Envelopes

Success responses have `data` populated and `error = null`:
```typescript
{
  data: { /* actual data */ },
  meta: null,
  error: null
}
```

Error responses have `error` populated and `data = null`:
```typescript
{
  data: null,
  meta: null,
  error: {
    code: "VALIDATION_ERROR",
    message: "Invalid input",
    details: { field: "nickname" }
  }
}
```

TanStack Query handles HTTP errors automatically. For envelope-level errors, check `response.data.error` if needed.

### 4. Using TypeScript Types

```typescript
import type { 
  ProfileResponseWrapper, 
  ProfileResponse, 
  UpdateMyProfileData 
} from '@/src/shared/api/sdk';

// Working with envelope wrapper
function handleProfileResponse(wrapper: ProfileResponseWrapper) {
  const profile = wrapper.data; // Type: ProfileResponse
  console.log(profile?.nickname);
}

// Type-safe request payload
const updatePayload: UpdateMyProfileData = {
  body: {
    nickname: 'John',
    bio: 'Hello world',
  },
};
```

## SDK Configuration Features

### Base URL

The SDK automatically configures the base URL from environment variables:

```env
# .env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8080
```

**Important**: The base URL should be **host-only** (no `/api/v1`), because OpenAPI paths already include the `/api/v1` prefix.

✅ Correct: `http://localhost:8080`  
❌ Wrong: `http://localhost:8080/api/v1` (would result in `/api/v1/api/v1`)

### Authentication

The SDK handles authentication automatically:

1. **Request Interceptor**: Adds JWT token to all requests
2. **Token Expiration Check**: Refreshes token if expired (< 5 minutes remaining)
3. **Automatic Refresh**: Calls `/auth/refresh` transparently
4. **Error Handling**: Clears auth data on 401 errors

### Error Handling

The SDK handles errors gracefully:

- Network errors
- 401 Unauthorized (triggers token refresh)
- 4xx/5xx HTTP errors
- Validation errors

TanStack Query provides additional error handling with retry logic and error boundaries.

## Updating the OpenAPI Snapshot

When the backend API changes, update the snapshot:

### Method 1: Generate from Backend Code (Recommended) ✅

**No need to start the backend server**. Generate directly from FastAPI code:

```bash
# From repo root
make generate-openapi
```

**Advantages:**
- ✅ No database required
- ✅ No Kong gateway required
- ✅ No environment variables or network setup needed
- ✅ Extracts directly from code, guaranteed to match implementation
- ✅ Can be automated in CI/CD pipeline

### Automated Update (CI/CD)

In CI/CD pipeline:

```yaml
# .github/workflows/update-openapi.yml
- name: Generate OpenAPI spec from code
  run: make generate-openapi

- name: Generate Mobile SDK
  run: |
    cd apps/mobile
    npm run sdk:generate
    npm run type-check
```

## Available Endpoints (Current)

Generated from `openapi/openapi.json`:

### Authentication

- `POST /auth/google-callback` - Google OAuth with PKCE
- `POST /auth/refresh` - Refresh access token

### Profile

- `GET /profile/me` - Get current user profile
- `PUT /profile/me` - Update current user profile

### Cards

- `GET /cards/me` - Get my cards

## Development Workflow

### ⚠️ Critical: When Backend API Changes

**Always follow this order to maintain type safety:**

```bash
# 1. Backend developer adds/modifies endpoint
# Edit: apps/backend/app/modules/.../routers/*.py

# 2. Generate new OpenAPI spec (MUST DO FIRST)
make generate-openapi

# 3. Regenerate Mobile SDK (BEFORE editing frontend)
cd apps/mobile
npm run sdk:clean
npm run sdk:generate

# 4. Verify types
npm run type-check

# 5. Now frontend developer can use new SDK
# Import from @/src/shared/api/sdk and get full type safety

# 6. Commit changes
git add ../../openapi/openapi.json
# Commit generated output too (but never edit generated files manually)
git add src/shared/api/generated
```

### Why This Order Matters

1. **Type Safety**: Frontend TypeScript will know about new endpoints immediately
2. **Prevent Errors**: Regenerating SDK before frontend changes avoids using outdated API definitions
3. **Developer Experience**: IDE autocomplete and type checking work correctly
4. **Team Collaboration**: Backend and frontend stay in sync

### Adding a New Endpoint

1. **Backend**: Add new endpoint to FastAPI
2. **Update OpenAPI**: Generate from code: `make generate-openapi`
3. **Regenerate SDK**: `cd apps/mobile && npm run sdk:generate`
4. **Use in Mobile**: Import new options/mutations from `@/src/shared/api/sdk`
5. **Type Safety**: TypeScript will ensure correct usage

### Example: Querying a New Endpoint

```typescript
import { useQuery } from '@tanstack/react-query';

import { getMyCardsOptions } from '@/src/shared/api/sdk';
import { Box, Spinner, Text } from '@/src/shared/ui/components';

function MyCardsScreen() {
  const { data, isLoading, error } = useQuery(getMyCardsOptions());

  if (isLoading) return <Spinner />;
  if (error) return <Text>載入失敗</Text>;

  return (
    <Box>
      <Text>共 {data?.data?.length ?? 0} 張</Text>
    </Box>
  );
}
```

## Best Practices

### ✅ DO

- **僅使用 TanStack Query options/mutations**（不直接呼叫 SDK 函式）
- Always regenerate SDK after backend API changes
- Configure SDK once at app startup
- Commit generated files, but **never edit them manually**
- Use TypeScript types from the SDK
- Handle loading and error states
- Signed URL 上傳必須使用獨立 `fetch()` 並依照 `required_headers`

### ❌ DON'T

- **禁止直接呼叫 SDK 函式**（如 `getMyProfile()`），必須用 options/mutations
- **禁止 import 舊的 `@/src/shared/api/client`**（legacy，已廢除）
- Modify generated files manually
- Use direct `fetch()` calls for backend API (except Signed URL upload)
- Hardcode API URLs (use SDK configuration)
- Ignore TypeScript errors from SDK

## Troubleshooting

### SDK Generation Fails

```bash
# Check OpenAPI file is valid JSON
cat ../../openapi/openapi.json | jq .

# Clean and retry
npm run sdk:clean
npm run sdk:generate
```

### Type Errors After Generation

```bash
# Ensure you're using TanStack Query options, not direct SDK calls
# ❌ import { getMyProfile } from '@/src/shared/api/sdk'
# ❌ import { apiClient } from '@/src/shared/api/client'
# ✅ import { getGetProfileMeQueryOptions } from '@/src/shared/api/sdk'

# Run type check
npm run type-check
```

### Authentication Not Working

```bash
# Verify SDK is configured
# Should be called in app/_layout.tsx:
configureSDK();

# Check environment variables
cat .env | grep EXPO_PUBLIC_API_BASE_URL
```

### 401 Errors

The SDK automatically handles 401 by:
1. Trying to refresh the token
2. Clearing auth data if refresh fails
3. App should redirect to login screen

Implement in your auth store:

```typescript
// src/shared/state/authStore.ts
import { clearAuthData } from '@/src/shared/auth/session';

const useAuthStore = create((set) => ({
  // ...
  handleUnauthorized: async () => {
    await clearAuthData();
    set({ isAuthenticated: false });
    router.push('/auth/login');
  },
}));
```

## Further Reading

- [hey-api Documentation](https://heyapi.vercel.app/)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [OpenAPI Specification](https://swagger.io/specification/)
