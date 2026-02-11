# 小卡上傳流程文件

## 概覽

小卡上傳系統透過 Signed URL 讓使用者將小卡圖片直接上傳到 Google Cloud Storage（GCS）。此設計具備：

- **安全上傳**：後端產生具時效性的 Signed URL
- **直傳儲存**：檔案直接上傳到 GCS，降低後端負載
- **配額管理**：限制每日上傳張數與總儲存容量
- **型別驗證**：僅允許 JPEG/PNG/WEBP/HEIC/HEIF

**重要（目前實作）**：
- 後端在 `POST /api/v1/cards/upload-url` 這一步就會建立小卡資料庫紀錄。
- 目前程式碼尚未提供「確認上傳（confirm upload）」API。
- 已規劃新增 `POST /api/v1/cards/{card_id}/confirm-upload`（尚未實作）；在此端點完成前，若取得 Signed URL 後沒有成功把檔案 PUT 到 GCS，資料庫仍可能存在一筆小卡紀錄，且會被納入配額計算。

## 架構

```
┌─────────┐      1. Request      ┌─────────┐      2. Generate     ┌─────────┐
│ Mobile  │ ───────────────────> │ Backend │ ──────────────────> │   GCS   │
│  App    │    upload-url        │   API   │   Signed URL        │ Bucket  │
└─────────┘                       └─────────┘                     └─────────┘
     │                                 │                                │
     │ 3. Upload file                  │                                │
     │    (PUT to signed URL)          │                                │
     └─────────────────────────────────────────────────────────────────┘
    │
    │ 注意：目前後端尚未提供「確認上傳」端點。
    │ 小卡資料庫紀錄會在 Step 1（upload-url）建立。
```

## 上傳流程

### Step 1：請求上傳 URL

**Client → Backend**：POST `/api/v1/cards/upload-url`

```json
{
  "content_type": "image/jpeg",
  "file_size_bytes": 2097152,
  "idol": "IU",
  "idol_group": "Solo",
  "album": "LILAC",
  "version": "Standard",
  "rarity": "rare"
}
```

**後端驗證項目**：
- Content-Type（必須是 `image/jpeg`、`image/png`、`image/webp`、`image/heic` 或 `image/heif`）
- 檔案大小（預設 ≤ 2MB）
- 每日上傳配額（目前預設：2 張/天）
- 總容量配額（目前預設：1GB）

**重要行為（目前實作）**：
- 後端在這一步就會建立小卡資料庫紀錄（因此會消耗每日張數、也會把 `file_size_bytes` 納入總容量計算）。

**後端回應**（成功時）：

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

### Step 2：上傳檔案到 GCS

**Client → GCS**：PUT 到 `upload_url`

```bash
curl -X PUT \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg \
  "https://storage.googleapis.com/kcardswap/cards/..."
```

**重要**：
- 必須使用回應中的 `required_headers.Content-Type`
- 必須在 15 分鐘內完成上傳（Signed URL 過期）
- 上傳 Signed URL 時不要附帶 `Authorization` header
- Content-Type 不一致會導致上傳失敗（簽章不匹配）

### Step 3：確認上傳完成（規劃中 / 尚未實作）

**Client → Backend**：POST `/api/v1/cards/{card_id}/confirm-upload`

用途：在成功 PUT 到 Signed URL 後，由客戶端呼叫後端進行「物件存在性」驗證（例如 HEAD/metadata），並把該卡片標記為已完成上傳（避免幽靈紀錄）。

**注意**：此端點目前尚未實作；本文件會在端點完成後更新為正式流程。

### Step 4：確認小卡紀錄（可選）

Client 可以確認小卡「資料庫紀錄」是否存在：

```bash
GET /api/v1/cards/me
```

會回傳使用者的小卡清單，包含剛建立的那張。

**注意**：此步驟只代表資料庫紀錄存在，不保證對應的 GCS 檔案已成功上傳。

## 配額系統

### 免費方案限制

免費方案的預設配額（可由環境變數調整）：

| Limit | Default Value | Config Variable |
|-------|---------------|-----------------|
| Daily uploads | 2 per day | `DAILY_UPLOAD_LIMIT_FREE` |
| Max file size | 2 MB | `MAX_FILE_SIZE_MB` |
| Total storage | 1 GB | `TOTAL_STORAGE_GB_FREE` |

### 配額檢查時機

後端會在產生 Signed URL 前先檢查配額：

1. **每日張數**：計算「今天（UTC 00:00 起）建立的小卡資料庫紀錄數」（也就是成功呼叫 `POST /cards/upload-url` 的次數）
2. **File size limit**: Validates `file_size_bytes` in request
3. **總容量**：把所有小卡的 `size_bytes` 加總（此值來自 upload-url 請求的 `file_size_bytes`）

### 查詢配額狀態

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
- Invalid `content_type` (must be `image/jpeg`, `image/png`, `image/webp`, `image/heic`, or `image/heif`)
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

**解法**：重新向後端請求新的 Signed URL。

### Content-Type Mismatch

If upload uses wrong Content-Type, GCS returns 403:

```xml
<Error>
  <Code>SignatureDoesNotMatch</Code>
  <Message>The request signature we calculated does not match</Message>
</Error>
```

**解法**：使用回應中的 `required_headers` 指定的 Content-Type。

## API Endpoints

### POST /api/v1/cards/upload-url

產生用於上傳小卡圖片的 Signed URL。

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

### POST /api/v1/cards/{card_id}/confirm-upload（規劃中 / 尚未實作）

確認指定小卡的原圖已成功上傳到 GCS，並將該卡片標記為「已完成上傳」。

- 觸發時機：客戶端成功 PUT 到 Signed URL 之後
- 後端行為：驗證 GCS 物件存在（例如 HEAD/metadata），成功才更新狀態
- 失敗行為：若物件不存在，回傳可辨識錯誤以引導重取 Signed URL 並重傳（錯誤碼/狀態碼以實作為準）

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
- `ext`: File extension (`.jpg`, `.png`, `.webp`, `.heic`, `.heif`)

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

   注意：這只確認資料庫紀錄存在，不代表 GCS 檔案一定存在。

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
4. Confirm upload with backend (planned: `POST /api/v1/cards/{card_id}/confirm-upload`)
5. Generate thumbnail locally (200x200 WebP, cache only)
6. Refresh card list

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
2. 配額是依資料庫 `created_at` 計算
3. 取得 Signed URL 後未完成上傳（仍會計入）

**Solutions**:
1. Check server time is UTC
2. Verify `count_uploads_today` uses UTC date
3. Check database query filters by date correctly

若需要清理一筆未完成上傳的紀錄，可使用 `DELETE /api/v1/cards/{card_id}` 刪除（前提是該卡不在進行中交易內）。

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
