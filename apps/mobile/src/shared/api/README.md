# API Directory

## ⚠️ Important: Legacy Client Deprecated

The old `client.ts` has been **deprecated** and **must not be used**.

### ✅ Correct Usage: Use SDK

**All API calls must use the hey-api generated SDK with TanStack Query:**

```typescript
// ✅ CORRECT: Use TanStack Query options/mutations
import { useQuery, useMutation } from '@tanstack/react-query';
import { getMyProfileOptions, updateMyProfileMutation } from '@/src/shared/api/sdk';

function MyComponent() {
  const { data, isLoading } = useQuery(getMyProfileOptions());
  const updateProfile = useMutation(updateMyProfileMutation());
  
  // ...
}
```

### ❌ Incorrect Usage: Legacy Client

```typescript
// ❌ WRONG: Do NOT import legacy client
import { apiClient } from '@/src/shared/api/client';  // ❌ Deprecated!

// ❌ WRONG: Do NOT call SDK functions directly
import { getMyProfile } from '@/src/shared/api/sdk';
const data = await getMyProfile();  // ❌ Must use TanStack Query!
```

### Exception: Signed URL Upload

**Only** Signed URL uploads should use independent `fetch()`:

```typescript
// ✅ CORRECT: Signed URL upload with independent fetch
async function uploadToSignedUrl(url: string, file: Blob, headers: Record<string, string>) {
  const response = await fetch(url, {
    method: 'PUT',
    headers, // Use required_headers from backend
    body: file,
  });
  
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }
}
```

## Directory Structure

```
src/shared/api/
├── sdk.ts                    # SDK configuration & exports (USE THIS)
├── generated/                # Generated SDK (auto-generated, DO NOT EDIT)
│   ├── @tanstack/
│   │   └── react-query.gen.ts  # TanStack Query options/mutations
│   ├── sdk.gen.ts            # API functions
│   ├── types.gen.ts          # TypeScript types
│   └── client/               # Client implementation
├── errorMapper.ts            # Error mapping utility
└── client.ts.deprecated      # ⚠️ DEPRECATED - DO NOT USE
```

## ESLint Protection

ESLint is configured to prevent importing the deprecated client:

```javascript
// This will cause an ESLint error:
import { apiClient } from '@/src/shared/api/client';
// Error: ❌ Legacy client is deprecated. Use SDK from "@/src/shared/api/sdk" instead.
```

## Documentation

- **SDK Usage Guide**: `apps/mobile/OPENAPI_SDK_GUIDE.md`
- **Tech Stack Documentation**: `apps/mobile/TECH_STACK.md`
- **README**: `apps/mobile/README.md`

## Need Help?

1. Read the [OpenAPI SDK Guide](../../OPENAPI_SDK_GUIDE.md)
2. Check examples in `src/features/profile/api/profileApi.ts`
3. See the profile screen: `app/(tabs)/profile.tsx`
