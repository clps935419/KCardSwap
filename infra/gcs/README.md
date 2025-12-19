# GCS（Google Cloud Storage）使用規範與測試分層

本文件定義 KCardSwap 對 GCS 的使用範圍、Bucket/物件命名規則，以及「Mock → 真實 GCS」切換策略。

## 範圍（Scope）

- **後端只處理「原圖」**：後端僅負責產生 Signed URL（PUT 上傳）與上傳配額/限制檢查。
- **禁止任何縮圖後端業務**：後端不得產生/儲存/回傳縮圖相關欄位；Bucket/物件路徑不得出現 `thumbs/`。
- **縮圖為 Mobile-only**：Mobile 端本機產生 `200x200` WebP 縮圖並本機快取（不上傳、不入 DB、不入契約）。

## Bucket 與物件命名（Object Key）

- Bucket：由 `GCS_BUCKET_NAME` 指定（預設 `kcardswap`）
- **原圖路徑（唯一允許）**：
  - `cards/{user_id}/{uuid}.jpg`

> 注意：本專案不建立 `thumbs/` 目錄（也不允許 `cards/.../thumbs/...` 等變體）。

## Signed URL 行為（Backend）

後端服務：`apps/backend/app/shared/infrastructure/external/gcs_storage_service.py`

- 上傳：`generate_upload_signed_url(blob_name, content_type, expiration_minutes)`
  - method: `PUT`
  - version: `v4`
  - 預設 `content_type`: `image/jpeg`
- 下載：`generate_download_signed_url(blob_name, expiration_minutes)`

### 必要環境變數（Backend）

- `GCS_BUCKET_NAME`
- `GCS_CREDENTIALS_PATH`（選用；若不提供則走 Default Credentials）

### 上傳限制（Backend）

上傳限制由應用層驗證（不應由 GCS 端假設）。目前後端配置位於 `apps/backend/app/config.py`：

- `MAX_FILE_SIZE_MB`（預設 10）
- `DAILY_UPLOAD_LIMIT_FREE`（預設 2）
- `TOTAL_STORAGE_GB_FREE`（預設 1）

## 測試分層（Mock → 真實 GCS）

核心原則：**Unit/Integration 預設不打真實 GCS**，避免外網依賴造成 flaky；真實 GCS 僅用於 Staging/Nightly（或手動）Smoke 測試，驗證 IAM/CORS/Signed URL PUT 的真實可用性。

### 1) Unit Tests（永遠不打真實 GCS）

- 對 `GCSStorageService` 以 stub/mock 取代（例如 mock `generate_upload_signed_url` 回傳固定 URL）。
- 覆蓋：路徑組裝（僅 `cards/{user_id}/{uuid}.jpg`）、內容型別/過期時間傳遞、錯誤映射。

### 2) Integration Tests（預設不打真實 GCS）

- 仍以 mock/stub 外部依賴為主，避免 CI 需要雲端憑證。
- 若需要更貼近 HTTP 行為，可用「本地 fake server」模擬 Signed URL PUT 接收，但**不驗證 GCS 真實簽名**。

### 3) Staging / Nightly Smoke（才打真實 GCS）

目的：驗證「真實」GCS 上傳鏈路是否可用（憑證/IAM、Bucket CORS、Signed URL PUT、Content-Type、超時）。

建議約束：
- 使用**專用測試 Bucket**（例如 `kcardswap-staging-uploads`），避免汙染正式資料。
- 使用**專用 Service Account**，僅授權該測試 Bucket（最小權限）。
- 物件路徑加上固定前綴便於清理（例如 `cards-smoke/{user_id}/{uuid}.jpg` 或以日期分層）。
- 測試結束後清理物件（或設定 Bucket Lifecycle 自動刪除）。

#### 如何啟用 Smoke（用環境變數切換）

在 CI/CD（或手動）僅於 Staging/Nightly pipeline 注入：

- `GCS_BUCKET_NAME`
- `GCS_CREDENTIALS_PATH` 或 Workload Identity/Default Credentials
- `RUN_GCS_SMOKE=1`（建議）

測試端（pytest）建議：
- 將 Smoke 測試標記為 `gcs_smoke`
- 預設跳過，僅在 `RUN_GCS_SMOKE=1` 時才執行
- 在 Nightly job 使用：`pytest -m gcs_smoke`

> 重點：本地開發與一般 PR CI **不需要** 真實 GCS；只有要驗證 IAM/CORS/PUT 時才手動或在 Nightly 跑 smoke。

## CORS（前端直傳需求）

Mobile 會使用 Signed URL 直接上傳到 GCS，因此需在 Bucket 設定允許必要的 HTTP 方法與 headers。

- 方法：至少 `PUT`, `GET`, `OPTIONS`
- Headers：至少 `Content-Type`

具體 CORS 設定與套用流程，請在建立 `infra/gcs/cors-config.json` 後補上（對應 tasks：T088）。
