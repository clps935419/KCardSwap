# Card Upload Flow Documentation

## Overview

The card upload system allows users to upload photo card images to Google Cloud Storage (GCS) using signed URLs. This approach provides:

- **Secure uploads**: Backend generates time-limited signed URLs
- **Direct-to-storage**: Files upload directly to GCS, reducing backend load
- **Quota management**: Enforces daily upload limits and storage quotas
- **Type validation**: Only JPEG and PNG images are allowed

## Architecture

```
┌─────────┐      1. Request      ┌─────────┐      2. Generate     ┌─────────┐
│ Mobile  │ ───────────────────> │ Backend │ ──────────────────> │   GCS   │
│  App    │    upload-url        │   API   │   Signed URL        │ Bucket  │
└─────────┘                       └─────────┘                     └─────────┘
     │                                 │                                │
     │ 3. Upload file                  │                                │
     │    (PUT to signed URL)          │                                │
     └─────────────────────────────────────────────────────────────────┘
     │                                 │
     │ 4. Confirm (optional)           │
     └─────────────────────────────────>
```

## Upload Process

### Step 1: Request Upload URL

**Client → Backend**: POST `/api/v1/cards/upload-url`

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

**Backend validates**:
- Content type (must be `image/jpeg` or `image/png`)
- File size (must be ≤ 10MB by default)
- Daily upload quota (free tier: 2 uploads/day)
- Total storage quota (free tier: 1GB total)

**Backend response** (on success):

```json
{
  "data": {
    "upload_url": "https://storage.googleapis.com/kcardswap/cards/user-id/card-id.jpg?X-Goog-Algorithm=...",
    "method": "PUT",
    "required_headers": {
      "Content-Type": "image/jpeg"
    },
    "image_url": "https://storage.googleapis.com/kcardswap/cards/user-id/card-id.jpg",
    "expires_at": "2024-01-15T10:30:00Z",
    "card_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "error": null
}
```

### Step 2: Upload File to GCS

**Client → GCS**: PUT to `upload_url`

```bash
curl -X PUT \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg \
  "https://storage.googleapis.com/kcardswap/cards/..."
```

**Important**: 
- Must use the exact `Content-Type` from `required_headers`
- Upload must complete within 15 minutes (signed URL expiration)
- Do NOT include `Authorization` header when uploading to signed URL
- Upload fails if Content-Type doesn't match

### Step 3: Verify Upload (Optional)

Client can verify the card was created:

```bash
GET /api/v1/cards/me
```

Returns list of user's cards including the newly uploaded one.

## Quota System

### Free Tier Limits

Default quotas for free users (configured via environment variables):

| Limit | Default Value | Config Variable |
|-------|---------------|-----------------|
| Daily uploads | 2 per day | `DAILY_UPLOAD_LIMIT_FREE` |
| Max file size | 10 MB | `MAX_FILE_SIZE_MB` |
| Total storage | 1 GB | `TOTAL_STORAGE_GB_FREE` |

### Quota Enforcement

Backend checks quotas **before** generating signed URL:

1. **Daily upload limit**: Counts uploads from current day (UTC)
2. **File size limit**: Validates `file_size_bytes` in request
3. **Total storage limit**: Sums `size_bytes` of all user's cards

### Checking Quota Status

```bash
GET /api/v1/cards/quota/status
```

Response:
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
  }
}
```

## Error Handling

### Quota Exceeded (422)

When any quota is exceeded:

```json
{
  "detail": {
    "code": "LIMIT_EXCEEDED",
    "message": "Daily upload limit of 2 reached",
    "limit_type": "daily"
  }
}
```

**Limit types**:
- `daily`: Daily upload limit exceeded
- `storage`: Total storage limit exceeded
- `file_size`: Individual file too large (caught during validation)

### Validation Errors (400)

Invalid request data:

```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid content type. Must be image/jpeg or image/png"
  }
}
```

Common validation errors:
- Invalid `content_type` (must be `image/jpeg` or `image/png`)
- Invalid `file_size_bytes` (must be > 0 and ≤ MAX_FILE_SIZE)
- Invalid `rarity` (must be one of: common, rare, epic, legendary)

### Authentication Errors (401)

Missing or invalid JWT token:

```json
{
  "detail": "Not authenticated"
}
```

### Signed URL Expired

If signed URL has expired (15 minutes), GCS returns 403:

```xml
<Error>
  <Code>AccessDenied</Code>
  <Message>Request has expired</Message>
</Error>
```

**Solution**: Request a new signed URL from backend.

### Content-Type Mismatch

If upload uses wrong Content-Type, GCS returns 403:

```xml
<Error>
  <Code>SignatureDoesNotMatch</Code>
  <Message>The request signature we calculated does not match</Message>
</Error>
```

**Solution**: Use exact `Content-Type` from `required_headers`.

## API Endpoints

### POST /api/v1/cards/upload-url

Generate signed URL for uploading a card image.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "content_type": "image/jpeg",
  "file_size_bytes": 5242880,
  "idol": "IU",          // optional
  "idol_group": "Solo",  // optional
  "album": "LILAC",      // optional
  "version": "Standard", // optional
  "rarity": "rare"       // optional: common, rare, epic, legendary
}
```

**Response**: `UploadUrlResponse` (see Step 1 above)

**Status Codes**:
- `200`: Success
- `400`: Validation error
- `401`: Not authenticated
- `422`: Quota exceeded

### GET /api/v1/cards/me

Get all cards owned by the authenticated user.

**Authentication**: Required (JWT)

**Query Parameters**:
- `status` (optional): Filter by status (`available`, `trading`, `traded`)

**Response**:
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
  ]
}
```

### DELETE /api/v1/cards/{card_id}

Delete a card owned by the authenticated user.

**Authentication**: Required (JWT)

**Path Parameters**:
- `card_id`: UUID of the card to delete

**Response**: `204 No Content` (success)

**Status Codes**:
- `204`: Successfully deleted
- `401`: Not authenticated
- `403`: Not the card owner
- `404`: Card not found

**Note**: Cards in active trades cannot be deleted.

### GET /api/v1/cards/quota/status

Check current upload quota usage.

**Authentication**: Required (JWT)

**Response**: `QuotaStatusResponse` (see Checking Quota Status above)

## File Storage

### Blob Path Format

```
cards/{user_id}/{card_id}.{ext}
```

Example:
```
cards/550e8400-e29b-41d4-a716-446655440000/a1b2c3d4-5678-90ab-cdef-1234567890ab.jpg
```

- `user_id`: UUID of the card owner
- `card_id`: UUID of the card record
- `ext`: File extension (`.jpg` or `.png`)

### Public Access

Image URLs are publicly accessible:

```
https://storage.googleapis.com/kcardswap/cards/...
```

No authentication needed to view images (for sharing).

## Configuration

### Environment Variables

Backend configuration (in `apps/backend/.env`):

```bash
# GCS Configuration
GCS_BUCKET_NAME=kcardswap
GCS_CREDENTIALS_PATH=/path/to/service-account-key.json
USE_MOCK_GCS=false  # true for dev/test, false for production

# Upload Limits
MAX_FILE_SIZE_MB=10
DAILY_UPLOAD_LIMIT_FREE=2
TOTAL_STORAGE_GB_FREE=1
```

### CORS Configuration

GCS bucket must have CORS enabled for direct uploads. See `infra/gcs/cors-config.json`:

```json
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type", "Content-Length", "Content-MD5"],
    "maxAgeSeconds": 3600
  }
]
```

Apply with:
```bash
gsutil cors set infra/gcs/cors-config.json gs://kcardswap
```

## Security Considerations

### Signed URLs

- **Time-limited**: Valid for 15 minutes only
- **Action-specific**: PUT only (no GET/DELETE)
- **Content-Type locked**: Must match specified type
- **Single-use**: Each upload requires new signed URL

### Backend Validation

Backend validates **before** generating signed URL:

1. File type (JPEG/PNG only)
2. File size (≤ 10MB)
3. User quotas (daily, storage)
4. User authentication

### GCS Permissions

Service account needs minimal permissions:

- `roles/storage.objectCreator` - Generate signed URLs
- `roles/storage.objectViewer` - Read objects (optional)

**Do not grant** `roles/storage.admin` in production.

## Testing

### Unit Tests

Located in `apps/backend/tests/unit/modules/social/`:

- `domain/test_card_entity.py`: Card entity validation
- `domain/test_upload_quota.py`: Quota logic
- `application/test_upload_card_use_case.py`: Upload use case

Run:
```bash
pytest apps/backend/tests/unit/modules/social/
```

### Integration Tests

Located in `apps/backend/tests/integration/modules/social/`:

- `test_card_upload_flow.py`: Complete upload flow

Run:
```bash
pytest apps/backend/tests/integration/modules/social/
```

### Manual Testing

1. **Get upload URL**:
   ```bash
   curl -X POST http://localhost:8080/api/v1/cards/upload-url \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "content_type": "image/jpeg",
       "file_size_bytes": 5242880
     }'
   ```

2. **Upload to signed URL**:
   ```bash
   curl -X PUT \
     -H "Content-Type: image/jpeg" \
     --data-binary @test.jpg \
     "SIGNED_URL_FROM_STEP_1"
   ```

3. **Verify upload**:
   ```bash
   curl http://localhost:8080/api/v1/cards/me \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## Mobile App Integration

Mobile app implementation: `apps/mobile/src/features/cards/`

### Image Selection & Compression

```typescript
import * as ImagePicker from 'expo-image-picker';
import * as ImageManipulator from 'expo-image-manipulator';

// Select image
const result = await ImagePicker.launchImageLibraryAsync({
  mediaTypes: ImagePicker.MediaTypeOptions.Images,
  allowsEditing: true,
  quality: 0.8,
});

// Compress to ≤10MB
const compressed = await ImageManipulator.manipulateAsync(
  result.uri,
  [{ resize: { width: 2000 } }],
  { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
);
```

### Upload Flow

1. Get file info (size, type)
2. Request signed URL from backend
3. Upload file to signed URL (use `fetch`, not API client)
4. Generate thumbnail locally (200x200 WebP, cache only)
5. Refresh card list

### Error Handling

- **Quota exceeded**: Show upgrade prompt or retry tomorrow
- **File too large**: Compress more or show error
- **Upload failed**: Retry with new signed URL
- **Network error**: Show retry button

## Troubleshooting

### Problem: Upload fails with 403

**Causes**:
1. Signed URL expired (>15 minutes old)
2. Wrong Content-Type header
3. Modified signed URL (even whitespace)

**Solutions**:
1. Request new signed URL
2. Use exact `Content-Type` from backend response
3. Don't modify URL, use as-is

### Problem: CORS error in browser/mobile

**Causes**:
1. CORS not configured on bucket
2. Preflight request failing
3. Wrong origin in CORS config

**Solutions**:
1. Apply CORS config: `gsutil cors set cors-config.json gs://bucket`
2. Check preflight OPTIONS request succeeds
3. Update CORS origins to include your domain

### Problem: Daily limit not resetting

**Causes**:
1. Timezone mismatch (backend uses UTC)
2. Quota tracked in database, not clearing

**Solutions**:
1. Check server time is UTC
2. Verify `count_uploads_today` uses UTC date
3. Check database query filters by date correctly

### Problem: Images not loading

**Causes**:
1. Wrong bucket permissions
2. Image URL format incorrect
3. CORS blocking image load

**Solutions**:
1. Make bucket publicly readable
2. Verify URL format: `https://storage.googleapis.com/bucket/path`
3. Add `Access-Control-Allow-Origin` to bucket CORS

## References

- [GCS Signed URLs](https://cloud.google.com/storage/docs/access-control/signed-urls)
- [GCS CORS Configuration](https://cloud.google.com/storage/docs/configuring-cors)
- [API Documentation](./api/social-module-cards.md)
- [GCS Setup Guide](../../infra/gcs/README.md)
