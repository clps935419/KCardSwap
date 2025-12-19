# Card Upload API Documentation

## Overview

The Card Upload API allows users to upload photo cards to GCS (Google Cloud Storage) with quota management for free and premium users.

## Endpoints

### 1. Get Upload Signed URL

Generate a signed URL for uploading a card image.

**Endpoint**: `POST /api/v1/cards/upload-url`

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "content_type": "image/jpeg",
  "file_size_bytes": 1234567,
  "idol": "IU",
  "idol_group": "Solo",
  "album": "Love Poem",
  "version": "Version A",
  "rarity": "rare"
}
```

**Response** (200 OK):
```json
{
  "upload_url": "https://storage.googleapis.com/bucket/path?signature=...",
  "method": "PUT",
  "required_headers": {
    "Content-Type": "image/jpeg"
  },
  "image_url": "https://storage.googleapis.com/bucket/cards/user_id/card_id.jpg",
  "expires_at": "2025-01-01T00:15:00Z",
  "card_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid file type or size
- `401 Unauthorized`: Missing or invalid token
- `422 Unprocessable Entity`: Quota exceeded

**Example - Quota Exceeded**:
```json
{
  "detail": {
    "code": "LIMIT_EXCEEDED",
    "message": "Daily upload limit of 2 reached",
    "limit_type": "daily"
  }
}
```

### 2. Upload File to GCS

After receiving the signed URL, upload the file directly to GCS:

**Request**:
```bash
curl -X PUT "https://storage.googleapis.com/..." \
  -H "Content-Type: image/jpeg" \
  --data-binary @image.jpg
```

**Note**: 
- Use the `method` and `required_headers` from the upload URL response
- Upload must complete within 15 minutes (URL expiration)

### 3. Get My Cards

Retrieve all cards owned by the authenticated user.

**Endpoint**: `GET /api/v1/cards/me`

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `status` (optional): Filter by status (available/trading/traded)

**Response** (200 OK):
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "owner_id": "987e6543-e21b-12d3-a456-426614174000",
    "idol": "IU",
    "idol_group": "Solo",
    "album": "Love Poem",
    "version": "Version A",
    "rarity": "rare",
    "status": "available",
    "image_url": "https://storage.googleapis.com/...",
    "size_bytes": 1234567,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 4. Delete Card

Delete a card owned by the authenticated user.

**Endpoint**: `DELETE /api/v1/cards/{card_id}`

**Authentication**: Required (Bearer token)

**Response**: `204 No Content` (success)

**Error Responses**:
- `400 Bad Request`: Card is in active trade
- `404 Not Found`: Card not found or not owner

### 5. Check Quota Status

Get current quota usage for the authenticated user.

**Endpoint**: `GET /api/v1/cards/quota/status`

**Authentication**: Required (Bearer token)

**Response** (200 OK):
```json
{
  "uploads_today": 1,
  "daily_limit": 2,
  "remaining_uploads": 1,
  "storage_used_bytes": 5242880,
  "storage_limit_bytes": 1073741824,
  "remaining_storage_bytes": 1068498944,
  "storage_used_mb": 5.0,
  "storage_limit_mb": 1024.0,
  "remaining_storage_mb": 1019.0
}
```

## Upload Quotas

### Free Tier
- **Daily Upload Limit**: 2 cards per day
- **Max File Size**: 10MB per file
- **Total Storage**: 1GB
- **Allowed Types**: JPEG, PNG

### Premium Tier (Phase 8)
- **Daily Upload Limit**: Unlimited
- **Max File Size**: 10MB per file
- **Total Storage**: 10GB
- **Allowed Types**: JPEG, PNG

## File Upload Flow

```
1. Client calls POST /cards/upload-url
   └─> Backend validates quota and creates card record
   └─> Backend generates GCS signed URL
   └─> Backend returns upload URL and card info

2. Client uploads file directly to GCS
   └─> PUT request to signed URL
   └─> Include Content-Type header
   └─> Upload must complete within 15 minutes

3. Client can now fetch the card via GET /cards/me
```

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid file type or size |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `NOT_FOUND` | 404 | Card not found or not owner |
| `LIMIT_EXCEEDED` | 422 | Quota exceeded (daily/storage/size) |

## Mobile Thumbnail Handling

- **Backend**: Does NOT generate or store thumbnails
- **Mobile**: Should generate 200x200 WebP thumbnails locally
- **Caching**: Thumbnails cached on device, fallback to original image
- **Key**: Use card_id or image_url hash as cache key

## Configuration

Environment variables for quota limits:

```bash
MAX_FILE_SIZE_MB=10
DAILY_UPLOAD_LIMIT_FREE=2
TOTAL_STORAGE_GB_FREE=1
```

## Testing

Access Swagger UI for interactive testing:
- **Local**: http://localhost:8000/api/v1/docs
- **Docker**: http://localhost:8080/api/v1/docs (via Kong Gateway)

## Security

- All endpoints require JWT authentication
- Signed URLs expire after 15 minutes
- Users can only delete their own cards
- Cards in active trades cannot be deleted
- GCS signed URLs prevent unauthorized uploads
