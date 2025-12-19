# GCS Mock Service 使用指南

## 概述

本專案使用 Mock GCS Service 在開發和測試環境中替代真實的 Google Cloud Storage，避免外部依賴並加速開發流程。

## 環境配置

### 開發環境（預設使用 Mock）

```bash
# .env 或環境變數
USE_MOCK_GCS=true  # 預設值
```

### 生產環境（使用真實 GCS）

```bash
USE_MOCK_GCS=false
GCS_BUCKET_NAME=kcardswap-production
GCS_CREDENTIALS_PATH=/path/to/service-account-key.json
```

## 在程式碼中使用

### 使用 Storage Service Factory（推薦）

```python
from app.shared.infrastructure.external.storage_service_factory import storage_service

# 自動根據 USE_MOCK_GCS 選擇服務
url = storage_service.generate_upload_signed_url(
    blob_name="cards/user123/card456.jpg",
    content_type="image/jpeg",
    expiration_minutes=15
)
```

### 在測試中使用

```python
def test_card_upload(mock_gcs_service):
    """使用 mock_gcs_service fixture"""
    url = mock_gcs_service.generate_upload_signed_url("cards/test/card.jpg")
    assert "storage.googleapis.com" in url
```

## 路徑規則

### ✓ 允許的路徑

```python
# 正確：使用 cards/ 前綴
"cards/user_id/card_uuid.jpg"
"cards/user123/abc-def-456.jpg"
```

### ✗ 禁止的路徑

```python
# 錯誤：不使用 cards/ 前綴
"images/user_id/card.jpg"  # ValueError

# 錯誤：包含 thumbs
"cards/user_id/thumbs/card.jpg"  # ValueError
"thumbs/card.jpg"  # ValueError
```

## Mock Service 功能

### 產生 Signed URLs

```python
# 上傳 URL
upload_url = mock_gcs_service.generate_upload_signed_url(
    blob_name="cards/user123/card456.jpg",
    content_type="image/jpeg",
    expiration_minutes=15
)

# 下載 URL
download_url = mock_gcs_service.generate_download_signed_url(
    blob_name="cards/user123/card456.jpg",
    expiration_minutes=60
)
```

### Blob 操作（測試用）

```python
# 檢查 blob 是否存在
exists = mock_gcs_service.blob_exists("cards/user123/card456.jpg")

# 取得 blob metadata
metadata = mock_gcs_service.get_blob_metadata("cards/user123/card456.jpg")

# 刪除 blob
deleted = mock_gcs_service.delete_blob("cards/user123/card456.jpg")

# 新增 mock blob（僅供測試）
mock_gcs_service._add_mock_blob("cards/user123/card456.jpg", size=1024)
```

## 測試策略

### Unit Tests（永遠使用 Mock）

```python
def test_upload_service(mock_gcs_service):
    """單元測試永遠使用 mock_gcs_service fixture"""
    url = mock_gcs_service.generate_upload_signed_url("cards/test/card.jpg")
    assert url is not None
```

### Integration Tests（永遠使用 Mock）

```python
@pytest.mark.asyncio
async def test_card_upload_flow(client, mock_gcs_service):
    """整合測試也使用 mock"""
    # 測試完整流程，但不實際上傳到 GCS
    response = await client.post("/api/v1/cards/upload-url")
    assert response.status_code == 200
```

### Smoke Tests（僅在 Staging/Nightly 執行）

```python
@pytest.mark.gcs_smoke
def test_real_gcs_upload():
    """需要真實 GCS 的 Smoke 測試"""
    # 只在設定 RUN_GCS_SMOKE=1 時執行
    if not settings.RUN_GCS_SMOKE:
        pytest.skip("GCS smoke test skipped")
    
    from app.shared.infrastructure.external.gcs_storage_service import GCSStorageService
    service = GCSStorageService()
    url = service.generate_upload_signed_url("cards-smoke/test/card.jpg")
    assert url is not None
```

執行 Smoke 測試：

```bash
# 本地或 CI 中執行
RUN_GCS_SMOKE=1 poetry run pytest -m gcs_smoke
```

## 常見問題

### Q: 為什麼開發時看不到上傳的檔案？

A: 開發環境預設使用 Mock，不會真的上傳到 GCS。Mock Service 只在記憶體中模擬，重啟後資料會消失。

### Q: 如何在開發時測試真實 GCS？

A: 設定環境變數：

```bash
USE_MOCK_GCS=false
GCS_BUCKET_NAME=your-test-bucket
GCS_CREDENTIALS_PATH=/path/to/credentials.json
```

### Q: CI/CD 需要設定 GCS 憑證嗎？

A: 一般的 Unit/Integration 測試不需要。只有執行 Smoke 測試時（設定 RUN_GCS_SMOKE=1）才需要。

## 檔案位置

- Mock Service: `app/shared/infrastructure/external/mock_gcs_storage_service.py`
- Real Service: `app/shared/infrastructure/external/gcs_storage_service.py`
- Factory: `app/shared/infrastructure/external/storage_service_factory.py`
- Config: `app/config.py`
- Test Fixture: `tests/conftest.py`
- Test Example: `tests/unit/infrastructure/external/test_mock_gcs_storage_service.py`
