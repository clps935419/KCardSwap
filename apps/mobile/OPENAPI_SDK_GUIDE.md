# OpenAPI SDK Generation Guide

## Overview

This project uses **hey-api/openapi-ts** to generate a type-safe TypeScript SDK from the backend's OpenAPI specification. The SDK includes:

- **Axios client** for HTTP requests
- **TanStack Query hooks** for React components
- **Full TypeScript types** for all endpoints

## Architecture

### Key Files

```
├── openapi/
│   └── openapi.json                    # OpenAPI snapshot (source of truth)
├── apps/mobile/
│   ├── openapi-ts.config.ts           # hey-api configuration
│   ├── src/shared/api/
│   │   ├── sdk.ts                     # Runtime configuration & exports
│   │   └── generated/                 # Generated SDK (not committed)
│   │       ├── @tanstack/
│   │       │   └── react-query.gen.ts # TanStack Query hooks
│   │       ├── client/                # Client implementation
│   │       ├── sdk.gen.ts             # API functions
│   │       └── types.gen.ts           # TypeScript types
```

### Why Strategy B (OpenAPI Snapshot in Repo)?

We use **Strategy B** (repo-internal snapshot) instead of Strategy A (direct network access) because:

1. **CI/CD Reliability**: No dependency on backend being available during mobile builds
2. **Cloud Agent Compatible**: Agents can generate SDK without network access to backend
3. **Version Control**: Changes to API schema are visible in git diffs
4. **Offline Development**: Developers can work without running backend locally
5. **Faster Builds**: No need to wait for backend startup

## Usage

### 1. Generating the SDK

```bash
cd apps/mobile

# Generate SDK from OpenAPI snapshot
npm run sdk:generate

# Clean generated files (before regenerating)
npm run sdk:clean
```

**Note**: Generated files are in `.gitignore` and should NOT be committed.

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

#### Option A: TanStack Query Hooks (Recommended)

```typescript
import { useGetMyProfileQuery, useUpdateMyProfileMutation } from '@/src/shared/api/sdk';

function ProfileScreen() {
  // Automatic caching, refetching, loading states
  const { data, isLoading, error } = useGetMyProfileQuery();

  // Mutations with optimistic updates
  const updateProfile = useUpdateMyProfileMutation();

  const handleUpdate = async () => {
    await updateProfile.mutateAsync({
      body: {
        nickname: 'New Name',
        bio: 'Updated bio',
      },
    });
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <View>
      <Text>{data?.data?.nickname}</Text>
      <Button onPress={handleUpdate}>Update</Button>
    </View>
  );
}
```

#### Option B: Direct API Calls

```typescript
import { getMyProfile, updateMyProfile } from '@/src/shared/api/sdk';

async function fetchProfile() {
  const response = await getMyProfile();
  return response.data;
}

async function updateProfile(nickname: string) {
  const response = await updateMyProfile({
    body: { nickname },
  });
  return response.data;
}
```

### 4. Using TypeScript Types

```typescript
import type { ProfileResponse, UpdateProfileRequest } from '@/src/shared/api/sdk';

// Type-safe function parameters
function displayProfile(profile: ProfileResponse['data']) {
  console.log(profile.nickname);
}

// Type-safe form data
const formData: UpdateProfileRequest = {
  nickname: 'John',
  bio: 'Hello world',
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

# Or from backend directory
cd apps/backend
python scripts/generate_openapi.py

# Using Docker (if you don't have Python locally)
make generate-openapi-docker
```

**Advantages:**
- ✅ No database required
- ✅ No Kong gateway required
- ✅ No environment variables or network setup needed
- ✅ Extracts directly from code, guaranteed to match implementation
- ✅ Can be automated in CI/CD pipeline

### Method 2: Fetch from Running Backend

If the backend is already running:

```bash
# Start the backend first
cd apps/backend
docker compose up -d

# Wait for backend to be ready, then fetch OpenAPI
curl -s http://localhost:8080/api/v1/openapi.json > ../../openapi/openapi.json

# Regenerate SDK
cd ../mobile
npm run sdk:clean
npm run sdk:generate

# Verify types
npm run type-check
```

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

### Adding a New Endpoint

1. **Backend**: Add new endpoint to FastAPI
2. **Update OpenAPI**: Generate from code: `make generate-openapi`
3. **Regenerate SDK**: `cd apps/mobile && npm run sdk:generate`
4. **Use in Mobile**: Import new hooks/functions from `@/src/shared/api/sdk`
5. **Type Safety**: TypeScript will ensure correct usage

### Example: Adding a Card Upload Endpoint

```typescript
// After backend adds POST /cards/upload-url and you regenerate SDK:

import { useUploadCardMutation } from '@/src/shared/api/sdk';

function UploadCardScreen() {
  const uploadCard = useUploadCardMutation();

  const handleUpload = async (imageData: string) => {
    const result = await uploadCard.mutateAsync({
      body: {
        idol: 'IU',
        idol_group: 'Solo',
        image_data: imageData,
      },
    });

    console.log('Upload URL:', result.data?.upload_url);
  };

  return <Button onPress={handleUpload}>Upload</Button>;
}
```

## Best Practices

### ✅ DO

- Always regenerate SDK after backend API changes
- Use TanStack Query hooks for components
- Configure SDK once at app startup
- Keep generated files in `.gitignore`
- Use TypeScript types from the SDK
- Handle loading and error states

### ❌ DON'T

- Commit generated files to git
- Modify generated files manually
- Use direct `fetch()` calls (use SDK instead)
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
# Ensure you're importing from the SDK, not old client
# ❌ import { apiClient } from '@/src/shared/api/client'
# ✅ import { useGetMyProfileQuery } from '@/src/shared/api/sdk'

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
