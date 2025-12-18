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

### 📋 Phase 完成報告
- [Phase 0 完成報告](docs/phases/phase-0-complete.md) - 專案初始化
- [Phase 1 完成報告](docs/phases/phase-1-complete.md) - 認證與個人檔案
- [Phase 2.5 完成報告](docs/phases/phase-2.5-complete.md) - 管理員系統
- [Phase 3 & 3.1 總結](docs/phases/phase-3-and-3.1-summary.md) - Google OAuth PKCE
- [Phase 3.1 完成報告](docs/phases/phase-3.1-complete.md) - OAuth 整合

### 📝 實作報告
- [Phase 1 實作報告](docs/phases/phase-1-implementation-report.md)
- [Phase 2.5 管理員腳本說明](docs/phases/phase-2.5-admin-scripts-clarification.md)
- [Phase 2.5 驗證指南](docs/phases/phase-2.5-verification-guide.md)
- [Phase 2.5 最終總結](docs/phases/phase-2.5-final-summary.md)
- [Phase 3 執行報告](docs/phases/phase-3-execution-report.md)
- [Phase 3.1 測試指南](docs/phases/phase-3.1-testing-guide.md)

### 🎉 里程碑
- [完成報告](docs/completion-report.md) - 專案完成總覽
- [Poetry 遷移報告](docs/poetry-migration-report.md) - 依賴管理工具遷移

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

# 管理員初始化
INIT_DEFAULT_ADMIN=true
DEFAULT_ADMIN_EMAIL=admin@kcardswap.local
DEFAULT_ADMIN_PASSWORD=your-password
```

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

## API 文件

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
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
