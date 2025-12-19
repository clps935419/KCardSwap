# Social Module - Cards API Documentation

## Overview

The Cards API provides endpoints for managing photo card uploads, retrieval, and deletion. It implements quota-based upload limits and uses Google Cloud Storage (GCS) signed URLs for direct-to-storage uploads.

## Base Path

All endpoints are prefixed with `/api/v1/cards`

## Authentication

All endpoints require JWT authentication via `Authorization: Bearer {token}` header.

---

## Endpoints

### POST /cards/upload-url

Generate a signed URL for uploading a card image to GCS.

**Authentication**: Required

#### Request

```json
{
  "content_type": "image/jpeg",
  "file_size_bytes": 5242880,
  "idol": "IU",
  "idol_group": "Solo",
  "album": "LILAC",
  "version": "Standard",
  "rarity": "rare"
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content_type` | string | Yes | MIME type (`image/jpeg` or `image/png`) |
| `file_size_bytes` | integer | Yes | File size in bytes (≤ 10MB by default) |
| `idol` | string | No | Idol name |
| `idol_group` | string | No | Idol group name |
| `album` | string | No | Album name |
| `version` | string | No | Card version |
| `rarity` | string | No | Card rarity (`common`, `rare`, `epic`, `legendary`) |

#### Response (200 OK)

```json
{
  "data": {
    "upload_url": "https://storage.googleapis.com/kcardswap/cards/...",
    "method": "PUT",
    "required_headers": {
      "Content-Type": "image/jpeg"
    },
    "image_url": "https://storage.googleapis.com/kcardswap/cards/...",
    "expires_at": "2024-01-15T10:30:00Z",
    "card_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "error": null
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `upload_url` | string | Signed URL for uploading (valid 15 minutes) |
| `method` | string | HTTP method to use (`PUT`) |
| `required_headers` | object | Headers required for upload |
| `image_url` | string | Public URL of uploaded image (after upload) |
| `expires_at` | string | ISO 8601 timestamp of signed URL expiration |
| `card_id` | UUID | ID of created card record |

#### Error Responses

**400 Bad Request** - Validation error

```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid content type. Must be image/jpeg or image/png"
  }
}
```

**422 Unprocessable Entity** - Quota exceeded

```json
{
  "detail": {
    "code": "LIMIT_EXCEEDED",
    "message": "Daily upload limit of 2 reached",
    "limit_type": "daily"
  }
}
```

**Limit Types**:
- `daily`: Daily upload limit exceeded
- `storage`: Total storage limit exceeded

#### Example

```bash
curl -X POST http://localhost:8080/api/v1/cards/upload-url \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "image/jpeg",
    "file_size_bytes": 5242880,
    "idol": "IU",
    "rarity": "rare"
  }'
```

---

### GET /cards/me

Retrieve all cards owned by the authenticated user.

**Authentication**: Required

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (`available`, `trading`, `traded`) |

#### Response (200 OK)

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "owner_id": "user-id",
      "idol": "IU",
      "idol_group": "Solo",
      "album": "LILAC",
      "version": "Standard",
      "rarity": "rare",
      "status": "available",
      "image_url": "https://storage.googleapis.com/kcardswap/cards/...",
      "size_bytes": 5242880,
      "created_at": "2024-01-15T10:15:00Z",
      "updated_at": "2024-01-15T10:15:00Z"
    }
  ],
  "error": null
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Card ID |
| `owner_id` | UUID | Owner user ID |
| `idol` | string | Idol name (nullable) |
| `idol_group` | string | Idol group (nullable) |
| `album` | string | Album name (nullable) |
| `version` | string | Card version (nullable) |
| `rarity` | string | Card rarity (nullable) |
| `status` | string | Card status (`available`, `trading`, `traded`) |
| `image_url` | string | Public image URL (nullable) |
| `size_bytes` | integer | File size in bytes (nullable) |
| `created_at` | string | ISO 8601 creation timestamp |
| `updated_at` | string | ISO 8601 update timestamp |

#### Example

```bash
# Get all cards
curl http://localhost:8080/api/v1/cards/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Filter by status
curl http://localhost:8080/api/v1/cards/me?status=available \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### DELETE /cards/{card_id}

Delete a card owned by the authenticated user.

**Authentication**: Required

**Note**: Cards in active trades cannot be deleted.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_id` | UUID | Yes | ID of the card to delete |

#### Response (204 No Content)

Empty response body on success.

#### Error Responses

**404 Not Found** - Card not found or not owned by user

```json
{
  "detail": {
    "code": "NOT_FOUND",
    "message": "Card not found or not owner"
  }
}
```

**400 Bad Request** - Card cannot be deleted

```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Cannot delete card in active trade"
  }
}
```

#### Example

```bash
curl -X DELETE http://localhost:8080/api/v1/cards/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### GET /cards/quota/status

Check current upload quota usage for the authenticated user.

**Authentication**: Required

#### Response (200 OK)

```json
{
  "data": {
    "uploads_today": 1,
    "daily_limit": 2,
    "remaining_uploads": 1,
    "storage_used_bytes": 5242880,
    "storage_limit_bytes": 1073741824,
    "remaining_storage_bytes": 1068499168,
    "storage_used_mb": 5.0,
    "storage_limit_mb": 1024.0,
    "remaining_storage_mb": 1019.0
  },
  "error": null
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `uploads_today` | integer | Number of uploads today |
| `daily_limit` | integer | Daily upload limit |
| `remaining_uploads` | integer | Remaining uploads today |
| `storage_used_bytes` | integer | Total storage used (bytes) |
| `storage_limit_bytes` | integer | Total storage limit (bytes) |
| `remaining_storage_bytes` | integer | Remaining storage (bytes) |
| `storage_used_mb` | float | Storage used (MB) |
| `storage_limit_mb` | float | Storage limit (MB) |
| `remaining_storage_mb` | float | Remaining storage (MB) |

#### Example

```bash
curl http://localhost:8080/api/v1/cards/quota/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Upload Flow

### Complete Upload Process

1. **Request Upload URL**
   ```bash
   POST /api/v1/cards/upload-url
   # Backend validates quotas and generates signed URL
   ```

2. **Upload File to GCS**
   ```bash
   PUT {upload_url}
   # Direct upload to GCS using signed URL
   # Must include exact Content-Type from step 1
   ```

3. **Verify Upload** (optional)
   ```bash
   GET /api/v1/cards/me
   # Check that card appears in list
   ```

### Important Notes

- **Signed URL Expiration**: 15 minutes
- **Content-Type**: Must match exactly (from `required_headers`)
- **No Authorization Header**: When uploading to signed URL
- **Single Use**: Each upload requires a new signed URL

---

## Quota System

### Free Tier (Default)

| Quota | Limit | Config Variable |
|-------|-------|-----------------|
| Daily uploads | 2 per day | `DAILY_UPLOAD_LIMIT_FREE` |
| Max file size | 10 MB | `MAX_FILE_SIZE_MB` |
| Total storage | 1 GB | `TOTAL_STORAGE_GB_FREE` |

### Premium Tier (Future)

To be implemented in Phase 8 (User Story 6).

---

## Error Codes

### Standard Error Response

```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `LIMIT_EXCEEDED` | 422 | Quota limit exceeded |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Not authenticated |
| `FORBIDDEN` | 403 | Not authorized |

### Quota Error Details

When `LIMIT_EXCEEDED` is returned, `limit_type` indicates which limit:

- `daily`: Daily upload limit
- `storage`: Total storage limit
- `file_size`: File size limit (in validation)

---

## Data Models

### Card

```typescript
interface Card {
  id: string;              // UUID
  owner_id: string;        // UUID
  idol?: string;           // nullable
  idol_group?: string;     // nullable
  album?: string;          // nullable
  version?: string;        // nullable
  rarity?: string;         // nullable: common, rare, epic, legendary
  status: string;          // available, trading, traded
  image_url?: string;      // nullable
  size_bytes?: number;     // nullable
  created_at: string;      // ISO 8601
  updated_at: string;      // ISO 8601
}
```

### UploadUrlResponse

```typescript
interface UploadUrlResponse {
  upload_url: string;         // Signed URL
  method: string;             // "PUT"
  required_headers: {         // Headers for upload
    "Content-Type": string;
  };
  image_url: string;          // Public URL
  expires_at: string;         // ISO 8601
  card_id: string;            // UUID
}
```

### QuotaStatus

```typescript
interface QuotaStatus {
  uploads_today: number;
  daily_limit: number;
  remaining_uploads: number;
  storage_used_bytes: number;
  storage_limit_bytes: number;
  remaining_storage_bytes: number;
  storage_used_mb: number;
  storage_limit_mb: number;
  remaining_storage_mb: number;
}
```

---

## Security

### Authentication

All endpoints require valid JWT token in Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Authorization

- Users can only access their own cards
- Users can only delete their own cards
- Cards in active trades cannot be deleted

### Signed URLs

- Time-limited (15 minutes)
- Action-specific (PUT only)
- Content-Type locked
- Single-use recommended

---

## Testing

### Unit Tests

```bash
pytest apps/backend/tests/unit/modules/social/
```

### Integration Tests

```bash
pytest apps/backend/tests/integration/modules/social/
```

### Manual Testing

See examples in each endpoint section above.

---

## Related Documentation

- [Card Upload Flow](../card-upload.md) - Detailed upload process
- [GCS Configuration](../../../infra/gcs/README.md) - GCS setup guide
- [Authentication](../authentication.md) - JWT authentication
- [API Overview](./README.md) - General API documentation

---

## Contract

API contracts are defined in:
```
specs/001-kcardswap-complete-spec/contracts/cards/upload_url.json
```

All responses must conform to the contract specification.
