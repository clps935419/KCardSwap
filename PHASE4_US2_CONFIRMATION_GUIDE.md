# Phase 4 User Story 2 - 卡片上傳確認功能完成指南

## 📋 已完成項目

### ✅ T094A - 新增確認上傳 API (後端)

#### 1. Domain Layer 更新
- **Card Entity** (`apps/backend/app/modules/social/domain/entities/card.py`)
  - 新增 `upload_status` 欄位 (pending/confirmed)
  - 新增 `upload_confirmed_at` 欄位
  - 新增 `confirm_upload()` 方法
  - 新增 `is_upload_confirmed()` 方法
  
#### 2. Infrastructure Layer 更新
- **CardModel** (`apps/backend/app/modules/social/infrastructure/database/models/card_model.py`)
  - 新增 `upload_status` 和 `upload_confirmed_at` 欄位
- **CardRepositoryImpl** (`apps/backend/app/modules/social/infrastructure/repositories/card_repository_impl.py`)
  - 更新 `save()` 方法以保存新欄位
  - 更新 `_to_entity()` 方法以映射新欄位

#### 3. Application Layer 新增
- **ConfirmCardUploadUseCase** (`apps/backend/app/modules/social/application/use_cases/cards/confirm_upload.py`)
  - 驗證卡片存在且屬於使用者
  - 檢查 GCS 物件存在
  - 標記上傳狀態為已確認

#### 4. Presentation Layer 新增
- **Cards Router** (`apps/backend/app/modules/social/presentation/routers/cards_router.py`)
  - 新增端點: `POST /api/v1/cards/{card_id}/confirm-upload`
  - 完整錯誤處理 (200/400/403/404)

#### 5. Database Migration
- **Migration 013** (`apps/backend/alembic/versions/013_add_card_upload_confirmation.py`)
  - 新增 `upload_status` 欄位 (VARCHAR(50), NOT NULL, DEFAULT 'pending')
  - 新增 `upload_confirmed_at` 欄位 (TIMESTAMP, NULLABLE)
  - 新增索引 `idx_cards_upload_status`

#### 6. 單元測試
- **Card Entity Tests** (`tests/unit/social/domain/entities/test_card.py`)
  - 26 個測試案例涵蓋所有業務邏輯
- **ConfirmCardUploadUseCase Tests** (`tests/unit/social/application/use_cases/test_confirm_upload_use_case.py`)
  - 9 個測試案例涵蓋成功與錯誤情境

### ✅ M203B - 前端串接確認上傳 API (Mobile)

#### 1. API Client 更新
- **cardsApi.ts** (`apps/mobile/src/features/cards/api/cardsApi.ts`)
  - 新增 `confirmCardUpload()` 函數
  - 新增 `ConfirmUploadResponse` 介面
  - 更新 `UploadUrlResponse` 新增 `card_id` 欄位
  - 完整錯誤處理與重試邏輯

#### 2. Upload Hook 整合
- **useUploadCard.ts** (`apps/mobile/src/features/cards/hooks/useUploadCard.ts`)
  - 整合確認上傳步驟 (Step 4)
  - 新增 'confirming' 進度狀態 (75%)
  - 確認失敗視為致命錯誤，需重新上傳

## 🔧 需要在實際環境執行的步驟

### 步驟 1: 執行 Database Migration

```bash
cd apps/backend
alembic upgrade head
```

**驗證**:
```bash
# 連線到資料庫檢查新欄位
psql -U kcardswap -d kcardswap -c "\\d cards"
```

應該看到:
- `upload_status` 欄位 (character varying(50), NOT NULL, DEFAULT 'pending')
- `upload_confirmed_at` 欄位 (timestamp with time zone, NULLABLE)
- `idx_cards_upload_status` 索引

### 步驟 2: 執行單元測試

```bash
cd apps/backend
pytest tests/unit/social/ -v
```

**預期結果**:
- `test_card.py`: 26 個測試通過
- `test_confirm_upload_use_case.py`: 9 個測試通過

### 步驟 3: 產生 OpenAPI 規格

```bash
cd apps/backend
poetry run python scripts/generate_openapi.py
```

或使用 Makefile:
```bash
make generate-openapi
```

**驗證**:
- 檢查 `openapi/openapi.json` 已更新
- 確認包含 `/api/v1/cards/{card_id}/confirm-upload` 端點

### 步驟 4: 產生前端 SDK

```bash
cd apps/mobile
npm run sdk:clean
npm run sdk:generate
```

**驗證**:
- 檢查 `apps/mobile/src/shared/api/generated/` 目錄已更新
- 確認包含 `confirmCardUpload` 相關的型別和函數

### 步驟 5: 更新前端使用 SDK

在前端 SDK 生成完成後，更新 `cardsApi.ts` 以使用生成的 SDK:

```typescript
// TODO: 將以下臨時實作替換為 SDK 生成的函數
// export { confirmCardUploadMutation, confirmCardUploadMutationKey } from '@/src/shared/api/sdk';
```

### 步驟 6: 測試完整上傳流程

#### 後端測試 (使用 curl 或 Postman)

1. **取得 JWT Token** (登入)
```bash
# 假設已有 access token
TOKEN="your-access-token"
```

2. **取得上傳 URL**
```bash
curl -X POST http://localhost:8080/api/v1/cards/upload-url \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "image/jpeg",
    "file_size_bytes": 512000,
    "idol": "測試偶像",
    "idol_group": "測試團體"
  }'
```

記下回應中的 `card_id`, `upload_url`, 和 `image_url`。

3. **上傳檔案到 Signed URL**
```bash
curl -X PUT "上傳_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary "@test-image.jpg"
```

4. **確認上傳**
```bash
curl -X POST "http://localhost:8080/api/v1/cards/{card_id}/confirm-upload" \
  -H "Authorization: Bearer $TOKEN"
```

**預期回應**:
```json
{
  "message": "Upload confirmed successfully",
  "card_id": "uuid-here"
}
```

5. **驗證卡片狀態**
```bash
curl -X GET http://localhost:8080/api/v1/cards/me \
  -H "Authorization: Bearer $TOKEN"
```

確認卡片的 `upload_status` 為 `"confirmed"`。

#### 前端測試 (Mobile App)

1. **啟動 Mobile App**
```bash
cd apps/mobile
npm start
```

2. **測試上傳流程**
   - 開啟上傳卡片畫面
   - 選擇或拍攝圖片
   - 觀察上傳進度:
     - ✓ 取得上傳連結 (20%)
     - ✓ 上傳中 (40-70%)
     - ✓ 確認上傳 (75%) ⭐ 新步驟
     - ✓ 產生縮圖 (85%)
     - ✓ 完成 (100%)
   - 確認卡片出現在我的卡冊列表

3. **測試錯誤情境**
   - 測試網路中斷時確認上傳失敗
   - 測試重複確認 (應顯示已確認錯誤)
   - 測試未上傳檔案就確認 (應顯示檔案不存在錯誤)

### 步驟 7: 更新 tasks.md

標記以下任務為完成:

```markdown
- [x] T094A [US2] 新增確認上傳 API：POST /api/v1/cards/{id}/confirm-upload
- [x] M203B [US2] 上傳成功後呼叫確認上傳 API
```

## 📊 API 規格

### POST /api/v1/cards/{card_id}/confirm-upload

確認卡片圖片已成功上傳到 GCS。

#### 請求
- **方法**: POST
- **路徑**: `/api/v1/cards/{card_id}/confirm-upload`
- **認證**: Bearer Token (Required)
- **路徑參數**:
  - `card_id` (UUID): 卡片 ID

#### 回應

**200 OK** - 確認成功
```json
{
  "message": "Upload confirmed successfully",
  "card_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**400 Bad Request** - 驗證錯誤
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Upload already confirmed"
}
```

**403 Forbidden** - 無權限
```json
{
  "code": "FORBIDDEN",
  "message": "Not authorized to confirm this card"
}
```

**404 Not Found** - 卡片或圖片不存在
```json
{
  "code": "CARD_NOT_FOUND",
  "message": "Card not found"
}
```

或

```json
{
  "code": "IMAGE_NOT_FOUND",
  "message": "Image file not found in storage. Please upload the file first."
}
```

## 🎯 功能說明

### 為什麼需要確認上傳 API?

1. **避免幽靈紀錄**: 防止卡片建立後，使用者未實際上傳圖片就離開
2. **資料一致性**: 確保資料庫記錄與實際 GCS 儲存一致
3. **配額計算準確**: 只計算真正完成上傳的卡片

### 上傳流程

```
使用者選擇圖片
    ↓
前端: 取得 Signed URL (M202)
    ↓ 回傳 {upload_url, card_id}
    ↓
前端: 直接上傳到 GCS (M203)
    ↓ 上傳成功
    ↓
前端: 呼叫確認 API (M203B) ⭐ 新增
    ↓ 後端驗證 GCS 物件存在
    ↓ 標記 upload_status = "confirmed"
    ↓
前端: 產生縮圖並快取 (M203A)
    ↓
完成
```

### 錯誤處理策略

| 錯誤情境 | HTTP 狀態碼 | 錯誤碼 | 處理方式 |
|---------|-----------|-------|---------|
| 卡片不存在 | 404 | CARD_NOT_FOUND | 提示重新上傳 |
| GCS 檔案不存在 | 404 | IMAGE_NOT_FOUND | 提示重新上傳檔案 |
| 非卡片擁有者 | 403 | FORBIDDEN | 提示無權限 |
| 已確認過 | 400 | VALIDATION_ERROR | 提示已完成 |
| 網路錯誤 | - | - | 自動重試 |

## 📝 程式碼範例

### 後端使用範例

```python
# 在 use case 中呼叫
from app.modules.social.application.use_cases.cards.confirm_upload import ConfirmCardUploadUseCase

use_case = ConfirmCardUploadUseCase(
    card_repository=card_repo,
    gcs_service=gcs_service,
)

try:
    await use_case.execute(card_id=card_id, owner_id=current_user_id)
    # 確認成功
except ValueError as e:
    # 處理錯誤
    if "not found" in str(e).lower():
        # 卡片或檔案不存在
    elif "not authorized" in str(e).lower():
        # 無權限
    elif "already confirmed" in str(e).lower():
        # 已確認
```

### 前端使用範例

```typescript
import { confirmCardUpload } from '@/src/features/cards/api/cardsApi';

// 在上傳成功後呼叫
try {
  await confirmCardUpload(uploadUrlResponse.card_id);
  console.log('Upload confirmed successfully');
} catch (error) {
  if (error.message.includes('not found')) {
    // 提示重新上傳
  } else if (error.message.includes('not authorized')) {
    // 提示無權限
  } else if (error.message.includes('already confirmed')) {
    // 已確認，不需處理
  } else {
    // 其他錯誤，提示重試
  }
}
```

## 🐛 故障排除

### 問題 1: Migration 執行失敗

**錯誤**: `Table 'cards' does not exist`

**解決方案**:
```bash
# 檢查現有 migrations
alembic current

# 執行所有 migrations
alembic upgrade head
```

### 問題 2: 單元測試失敗

**錯誤**: `ModuleNotFoundError: No module named 'app'`

**解決方案**:
```bash
# 確保在正確的目錄
cd apps/backend

# 使用 poetry 執行測試
poetry run pytest tests/unit/social/ -v
```

### 問題 3: SDK 生成失敗

**錯誤**: `openapi/openapi.json not found`

**解決方案**:
```bash
# 先產生 OpenAPI spec
cd apps/backend
make generate-openapi

# 再產生 SDK
cd apps/mobile
npm run sdk:generate
```

### 問題 4: 確認上傳回傳 404

**可能原因**:
1. GCS 物件未上傳成功
2. Signed URL 過期後才上傳
3. 檔案名稱不匹配

**檢查方式**:
```bash
# 檢查 GCS bucket
gsutil ls gs://your-bucket/cards/
```

## ✅ 完成檢查清單

在結束前，請確認:

- [ ] Migration 執行成功，資料庫包含新欄位
- [ ] 單元測試全部通過 (35 個測試)
- [ ] OpenAPI spec 已更新並包含新端點
- [ ] 前端 SDK 已重新產生
- [ ] 完整上傳流程測試通過
- [ ] 錯誤情境測試通過
- [ ] tasks.md 已更新標記完成
- [ ] 程式碼已 commit 並 push

## 🎉 完成！

恭喜完成 Phase 4 User Story 2 的確認上傳功能！

此功能確保每個卡片記錄都對應到實際的 GCS 儲存檔案，避免資料不一致的問題。

**下一步**: 繼續完成 Phase 4 的其他任務，或進入 Phase 5。
