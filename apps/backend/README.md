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
- [Identity Module API](docs/api/identity-module.md) - 身份驗證與個人檔案 API

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
TEST_DATABASE_URL=postgresql+asyncpg://kcardswap:kcardswap@localhost:5432/kcardswap_test

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
# 執行所有測試
poetry run pytest

# 執行測試並顯示覆蓋率
poetry run pytest --cov=app

# 使用 Makefile 執行測試
make test

# 在 Docker 容器中執行測試
make test-docker
```

#### 測試資料庫設置

本專案使用獨立的測試資料庫 `kcardswap_test`，提供以下優勢：

- **資料隔離**：測試資料與開發資料完全分離
- **自動回滾**：每個測試在獨立事務中執行，測試完成後自動回滾
- **快速清理**：無需手動清理測試資料，事務回滾自動處理
- **並行安全**：多個測試可以安全地並行執行

測試資料庫在 Docker 啟動時會自動建立並執行 migrations。如需手動初始化：

```bash
# 初始化測試資料庫 schema
make init-test-db

# 或直接使用 alembic
DATABASE_URL=postgresql://kcardswap:kcardswap@localhost:5432/kcardswap_test alembic upgrade head
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

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json
- **Kong Gateway**: http://localhost:8080/api/v1

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

---

**最後更新**: 2025-12-18  
**維護者**: KCardSwap Team
