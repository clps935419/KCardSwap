# Task T005 完成報告：GCS Bucket 與測試分層規劃

## 任務概述

完成 GCS（Google Cloud Storage）基礎建設的 Mock 機制實作，確保開發和測試環境不需要直接連接真實 GCS，同時保留在 Staging/Nightly 環境執行真實 GCS smoke 測試的能力。

## 實作內容

### 1. Mock GCS Storage Service

**檔案位置**: `apps/backend/app/shared/infrastructure/external/mock_gcs_storage_service.py`

**主要功能**:
- 實作與真實 GCS 相同的介面
- 支援產生 Mock Signed URLs（upload/download）
- 強制執行路徑規則：
  - ✅ 允許：`cards/{user_id}/{uuid}.jpg`
  - ❌ 禁止：不以 `cards/` 開頭的路徑
  - ❌ 禁止：包含 `thumbs/` 的任何路徑
- 提供 in-memory blob 操作（exists, delete, metadata）

**驗證結果**:
```bash
✓ Mock service 可成功導入
✓ 正確產生 mock signed URLs
✓ 正確拒絕 invalid 路徑
✓ 正確拒絕包含 thumbs 的路徑
✓ Blob 操作功能正常
```

### 2. Storage Service Factory

**檔案位置**: `apps/backend/app/shared/infrastructure/external/storage_service_factory.py`

**主要功能**:
- 根據環境變數 `USE_MOCK_GCS` 自動選擇服務
- 使用 `TYPE_CHECKING` 避免開發環境的依賴問題
- 延遲導入真實 GCS 服務（只在 `USE_MOCK_GCS=false` 時）

**設計考量**:
- 開發環境預設不需要安裝 `google-cloud-storage`
- 真實 GCS 服務只在需要時才導入，避免啟動失敗

### 3. 配置更新

**檔案**: `apps/backend/app/config.py`

新增環境變數:
```python
USE_MOCK_GCS: bool = os.getenv("USE_MOCK_GCS", "true").lower() == "true"
RUN_GCS_SMOKE: bool = os.getenv("RUN_GCS_SMOKE", "false").lower() == "true"
```

### 4. 測試基礎設施

**檔案**: `apps/backend/tests/conftest.py`

新增內容:
- `pytest_configure`: 註冊 `gcs_smoke` marker
- `mock_gcs_service` fixture: 為每個測試提供新的 Mock GCS 實例

**檔案**: `apps/backend/pyproject.toml`

新增 pytest marker:
```toml
markers = [
    "gcs_smoke: GCS smoke tests that require real GCS connection (use RUN_GCS_SMOKE=1)",
]
```

### 5. 單元測試範例

**檔案**: `apps/backend/tests/unit/infrastructure/external/test_mock_gcs_storage_service.py`

包含測試:
- 有效路徑的 signed URL 產生
- 無效路徑的拒絕
- thumbs 路徑的拒絕
- Blob 操作功能
- Smoke 測試框架（標記為 `@pytest.mark.gcs_smoke`）

### 6. 文件更新

#### 後端 README.md
- 添加 GCS 環境變數說明
- 添加測試分層策略說明
- 添加如何執行 GCS smoke 測試的指令

#### GCS Mock 使用指南
**檔案**: `apps/backend/docs/gcs-mock-usage.md`

完整涵蓋:
- 環境配置說明
- 程式碼使用範例
- 路徑規則說明
- Mock Service 功能說明
- 測試策略（Unit/Integration/Smoke）
- 常見問題解答

#### 環境變數範例
更新 `.env.example` 檔案（根目錄和 backend 目錄）:
```bash
USE_MOCK_GCS=true
RUN_GCS_SMOKE=false
```

## 測試分層策略

### Unit Tests（永遠使用 Mock）
```python
def test_upload_service(mock_gcs_service):
    url = mock_gcs_service.generate_upload_signed_url("cards/test/card.jpg")
    assert url is not None
```

### Integration Tests（永遠使用 Mock）
```python
@pytest.mark.asyncio
async def test_card_upload_flow(client, mock_gcs_service):
    response = await client.post("/api/v1/cards/upload-url")
    assert response.status_code == 200
```

### Smoke Tests（僅 Staging/Nightly）
```bash
# 執行真實 GCS 測試
RUN_GCS_SMOKE=1 poetry run pytest -m gcs_smoke
```

## 驗證清單

- [x] Mock GCS Service 實作完成
- [x] Storage Service Factory 實作完成
- [x] 配置更新完成（config.py, .env.example）
- [x] 測試基礎設施建立（fixtures, markers）
- [x] 單元測試範例建立
- [x] 文件更新完成（README, usage guide）
- [x] 程式碼通過 Ruff 檢查
- [x] 手動功能驗證通過
- [x] 路徑規則驗證通過

## 使用方式

### 開發環境（預設）
```bash
# .env 或不設定（使用預設值）
USE_MOCK_GCS=true
```

### 生產環境
```bash
USE_MOCK_GCS=false
GCS_BUCKET_NAME=kcardswap-production
GCS_CREDENTIALS_PATH=/path/to/service-account-key.json
```

### 程式碼中使用
```python
from app.shared.infrastructure.external.storage_service_factory import storage_service

# 自動根據環境變數選擇 Mock 或真實服務
url = storage_service.generate_upload_signed_url(
    blob_name="cards/user123/card456.jpg",
    content_type="image/jpeg",
    expiration_minutes=15
)
```

## 核心原則遵循

✅ **開發/測試不打真實 GCS**: 預設使用 Mock，避免外部依賴
✅ **僅 Staging/Nightly 執行 Smoke 測試**: 透過 `RUN_GCS_SMOKE=1` 控制
✅ **後端只處理原圖**: 路徑僅允許 `cards/`，禁止 `thumbs/`
✅ **測試分層明確**: Unit/Integration 永遠 Mock，Smoke 測試分離

## 後續建議

1. **CI/CD 整合**
   - Unit/Integration tests: 不需設定 GCS 相關環境變數
   - Nightly builds: 設定 `RUN_GCS_SMOKE=1` 執行 smoke 測試

2. **真實 GCS Smoke 測試**
   - 建立專用測試 Bucket（如 `kcardswap-staging-uploads`）
   - 配置專用 Service Account（最小權限）
   - 測試後自動清理或設定 Lifecycle Policy

3. **使用 Mock Service 的服務**
   - 當實作卡片上傳相關功能時，使用 `storage_service_factory`
   - 在測試中注入 `mock_gcs_service` fixture

## 檔案清單

### 新增檔案
- `apps/backend/app/shared/infrastructure/external/mock_gcs_storage_service.py`
- `apps/backend/app/shared/infrastructure/external/storage_service_factory.py`
- `apps/backend/tests/unit/infrastructure/external/test_mock_gcs_storage_service.py`
- `apps/backend/tests/unit/infrastructure/external/__init__.py`
- `apps/backend/docs/gcs-mock-usage.md`

### 修改檔案
- `apps/backend/app/config.py` - 新增 USE_MOCK_GCS, RUN_GCS_SMOKE
- `apps/backend/tests/conftest.py` - 新增 mock_gcs_service fixture
- `apps/backend/pyproject.toml` - 新增 gcs_smoke marker
- `apps/backend/README.md` - 新增 GCS 相關說明
- `apps/backend/.env.example` - 新增 GCS 環境變數
- `.env.example` - 新增 GCS 環境變數

## 結論

Task T005 已完成所有要求的基礎建設：

1. ✅ 建立完整的 Mock GCS Service
2. ✅ 實作測試分層策略（Unit/Integration 使用 Mock，Smoke 使用真實 GCS）
3. ✅ 強制執行路徑規則（僅 cards/，禁止 thumbs/）
4. ✅ 提供完整文件和使用範例
5. ✅ 通過程式碼品質檢查

開發人員現在可以在不需要真實 GCS 憑證的情況下進行開發和測試，同時保留在需要時執行真實 GCS 驗證的能力。
