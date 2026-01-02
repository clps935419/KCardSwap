# KCardSwap Backend Documentation

FastAPI + PostgreSQL + Alembic + Poetry

## 📚 文件索引

### 🚀 快速開始
- [開發環境設置](#開發環境設置) - 如何啟動本地開發環境
- [環境變數配置](#環境變數) - 必要的環境變數說明
- [Docker 開發流程](docs/setup/docker-dev-workflow.md) - Docker 開發最佳實務

### 🏗️ 架構設計
- [IoC 容器實作](docs/architecture/ioc-implementation.md) - 依賴注入容器設計
- [資料庫架構](docs/database-architecture.md) - 資料庫設計與關係
- [認證系統](docs/authentication.md) - Google OAuth 與 JWT 認證
- [資料庫遷移](docs/database-migrations.md) - Alembic 遷移管理
- [查詢優化](docs/query-optimization.md) - 資料庫查詢最佳化

### 📖 API 文件
- [**API Overview & Response Format**](docs/api/README.md) - API 概覽與統一回應格式 ⭐
- [Identity Module API](docs/api/identity-module.md) - 身份驗證與個人檔案 API
- [Response Format Specification](../../specs/001-kcardswap-complete-spec/response-format.md) - 完整回應格式規範

### 🔧 開發指南
- [初始化資料設計](docs/setup/init-data-design.md) - Init data 與 seed 策略
- [Google OAuth 設定](docs/setup/google-oauth-setup.md) - OAuth 配置步驟
- [密鑰管理](docs/setup/secrets.md) - 敏感資料處理指南

---

## 開發環境設置

### 前置需求
- Python 3.11+
- Poetry 1.7+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### 安裝 Poetry

**macOS / Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 首次設置

```bash
# 1. 進入 backend 目錄
cd apps/backend

# 2. 安裝依賴
poetry install

# 3. 執行資料庫遷移
poetry run alembic upgrade head

# 4. 初始化管理員（可選）
poetry run python scripts/init_admin.py

# 5. 啟動開發伺服器
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 使用 Docker（推薦）

```bash
# 從專案根目錄啟動
docker compose up -d

# 查看日誌
docker compose logs -f backend
```

## 環境變數

```bash
# 資料庫
DATABASE_URL=postgresql+asyncpg://kcardswap:kcardswap@localhost:5432/kcardswap

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GCS (Google Cloud Storage)
GCS_BUCKET_NAME=kcardswap
GCS_CREDENTIALS_PATH=/path/to/service-account-key.json
# 開發/測試使用 Mock GCS (預設: true)
USE_MOCK_GCS=true
# 啟用 GCS Smoke 測試 (僅用於 Staging/Nightly CI)
RUN_GCS_SMOKE=false

# 管理員初始化
INIT_DEFAULT_ADMIN=true
DEFAULT_ADMIN_EMAIL=admin@kcardswap.local
DEFAULT_ADMIN_PASSWORD=your-password
```

### GCS 測試分層說明

本專案採用 Mock GCS 策略，避免開發和測試環境直接連接真實 GCS：

- **開發環境（預設）**：`USE_MOCK_GCS=true` - 使用 MockGCSStorageService
- **Unit/Integration 測試**：永遠使用 Mock，不打真實 GCS
- **Staging/Nightly Smoke 測試**：設定 `RUN_GCS_SMOKE=1` 執行真實 GCS 測試

執行 GCS Smoke 測試：
```bash
# 僅執行標記為 gcs_smoke 的測試
RUN_GCS_SMOKE=1 poetry run pytest -m gcs_smoke
```

詳細規範請參考 [infra/gcs/README.md](/infra/gcs/README.md)

## 常用命令

### Poetry
```bash
poetry install              # 安裝依賴
poetry add package-name     # 新增依賴
poetry run <command>        # 執行命令
```

### 資料庫遷移
```bash
poetry run alembic upgrade head              # 執行遷移
poetry run alembic revision --autogenerate   # 建立遷移
```

### 管理員
```bash
# Idempotent（可重複執行）
poetry run python scripts/init_admin.py

# Fail-fast（重複會報錯）
poetry run python scripts/create_admin.py --email admin@example.com --password pass123
```

### 測試
```bash
poetry run pytest
poetry run pytest --cov=app
```

### Linting
```bash
poetry run ruff check .
poetry run ruff check --fix .
```

### OpenAPI 規格
```bash
# 方法 1: 使用 Poetry（完整環境）
poetry run python scripts/generate_openapi.py

# 方法 2: 直接執行（最小依賴，不需要 Poetry）
pip3 install fastapi pydantic sqlalchemy injector asyncpg python-jose passlib bcrypt email-validator google-auth google-cloud-storage firebase-admin httpx python-multipart
python3 scripts/generate_openapi.py

# 方法 3: 使用 Makefile
make generate-openapi
```

產生的 `openapi/openapi.json` 位於專案根目錄的 `openapi/` 資料夾，用於前端 SDK 生成。

## API 文件

### 互動式文件

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json
- **Kong Gateway**: http://localhost:8080/api/v1

### 統一回應格式

自 2026-01-02 起，所有 API 端點採用統一的 envelope 回應格式：

```json
{
  "data": <response_data> | null,
  "meta": <metadata> | null,
  "error": <error_object> | null
}
```

**成功回應範例**:
```json
{
  "data": {
    "id": "uuid",
    "nickname": "CardMaster"
  },
  "meta": null,
  "error": null
}
```

**分頁回應範例**:
```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "error": null
}
```

**錯誤回應範例**:
```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "404_NOT_FOUND",
    "message": "Resource not found",
    "details": {}
  }
}
```

**詳細說明**: 請參閱 [API Overview](docs/api/README.md) 與 [Response Format Specification](../../specs/001-kcardswap-complete-spec/response-format.md)

### API 模組

所有 45 個端點已標準化：

- **Identity Module** (9 endpoints): 認證、個人檔案、訂閱
- **Social Module - Cards** (5 endpoints): 小卡上傳與管理
- **Social Module - Nearby** (2 endpoints): 附近搜尋
- **Social Module - Friends** (5 endpoints): 好友系統
- **Social Module - Chat** (3 endpoints): 聊天室
- **Social Module - Trade** (6 endpoints): 交換系統
- **Social Module - Rating** (3 endpoints): 評分系統
- **Social Module - Report** (2 endpoints): 檢舉系統
- **Posts Module** (8 endpoints): 城市看板貼文
- **Locations Module** (1 endpoint): 城市列表

完整端點列表請參閱 [API Overview](docs/api/README.md)

## 架構原則

### DDD (Domain-Driven Design)
- 模組化的 DDD 架構
- 清楚分離 Domain, Application, Infrastructure, Presentation 層

### 依賴注入
- 使用 IoC 容器管理依賴
- 透過介面定義服務

### 資料庫遷移
- Alembic 管理 schema 變更
- 初始化資料透過獨立 scripts

詳見 [IoC 容器實作](docs/architecture/ioc-implementation.md) 和 [初始化資料設計](docs/setup/init-data-design.md)。

## 相關資源

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [Poetry 官方文件](https://python-poetry.org/docs/)
- [Alembic 官方文件](https://alembic.sqlalchemy.org/)

## 變更紀錄

### 2026-01-02 - API Response Standardization (Phase 8.6)

- ✅ 實作統一 envelope 回應格式 (`{data, meta, error}`)
- ✅ 標準化所有 12 個 routers、45 個 API 端點
- ✅ 更新錯誤處理機制，統一錯誤碼格式
- ✅ 新增分頁支援 (meta 包含 total, page, page_size, total_pages)
- ✅ 更新 OpenAPI 3.0 規格檔案
- ⚠️ **Breaking Change**: 前端需要更新以解析新的回應格式

詳細資訊請參閱:
- [Phase 8.6 Backend Complete Report](/PHASE86_BACKEND_COMPLETE.md)
- [Response Format Specification](../../specs/001-kcardswap-complete-spec/response-format.md)

---

**最後更新**: 2026-01-02  
**維護者**: KCardSwap Team
