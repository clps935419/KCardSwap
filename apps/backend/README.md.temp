# KCardSwap Backend (FastAPI)

## 環境變數
- `DATABASE_URL`: 例如 `postgresql+asyncpg://kcardswap:kcardswap@db:5432/kcardswap`（使用 asyncpg 驅動）
- `GCS_BUCKET`: 例如 `kcardswap-dev`
- `JWT_SECRET`: 用於簽發 JWT 的密鑰（開發可暫用）

## 開發環境設置

### 安裝 Poetry

Poetry 是本專案的依賴管理工具。請依據您的作業系統安裝：

**macOS / Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

驗證安裝：
```bash
poetry --version
```

### 首次設置專案

```bash
# 1. Clone 專案並進入 backend 目錄
cd apps/backend

# 2. 安裝所有依賴（生產 + 開發）
poetry install

# 3. 啟動虛擬環境 shell
poetry shell

# 4. 啟動開發伺服器（支援熱重載）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或者不進入 shell，直接使用 `poetry run`：
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 常用 Poetry 命令

| 操作 | 命令 |
|------|------|
| 安裝所有依賴 | `poetry install` |
| 新增生產依賴 | `poetry add package-name` |
| 新增開發依賴 | `poetry add --group dev package-name` |
| 移除依賴 | `poetry remove package-name` |
| 更新依賴 | `poetry update` |
| 查看已安裝套件 | `poetry show` |
| 查看依賴樹 | `poetry show --tree` |
| 啟動虛擬環境 | `poetry shell` |
| 執行命令 | `poetry run <command>` |

## 本地開發伺服器啟動

**使用 Poetry（推薦）:**
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**使用 Docker Compose:**
```bash
# 從專案根目錄啟動整套環境
docker compose up -d
```

## 結構建議
```
apps/backend/
  app/
    main.py
    routers/
      auth.py
      profile.py
      cards.py
      nearby.py
      social.py
      chat.py
      trade.py
      biz.py
    services/
    models/
    db/
  tests/
  pyproject.toml      # Poetry 配置檔案
  poetry.lock         # Poetry 鎖定檔案（必須納入版本控制）
```

## 測試

**使用 Poetry 執行測試:**
```bash
# 執行所有測試
poetry run pytest

# 執行測試並顯示覆蓋率
poetry run pytest --cov=app --cov-report=term-missing

# 執行特定測試檔案
poetry run pytest tests/test_main.py -v
```

## Linting 與格式化

```bash
# 執行 Ruff linting
poetry run ruff check .

# 自動修正可修正的問題
poetry run ruff check --fix .
```

## 依賴管理說明

本專案使用 **Poetry** 進行依賴管理，提供以下優勢：
- 自動解決依賴衝突
- 精確的版本鎖定（poetry.lock）
- 開發/生產依賴分離
- 簡化的依賴操作

所有依賴變更應透過 `poetry add/remove` 命令進行。

## 注意事項
- 與 Kong 連接路徑統一為 `/api/v1/*`
- 錯誤回應格式 `{ data: null, error: { code, message } }`
- 超限錯誤碼：`422_LIMIT_EXCEEDED`；未授權：`401_UNAUTHORIZED`
- `poetry.lock` 必須納入版本控制，確保團隊環境一致性

## 故障排除

### Poetry 找不到
確保 Poetry 已加入 PATH。通常在：
- macOS/Linux: `$HOME/.local/bin`
- Windows: `%APPDATA%\Python\Scripts`

### 依賴衝突
```bash
# 清除快取並重新安裝
poetry cache clear pypi --all
poetry install
```

### 更多協助
詳見 `/specs/copilot/modify-requirements-backend/quickstart.md`
