# 本機開發環境設定

## 後端開發設定

本專案使用 **Poetry** 進行依賴管理。

### 1) 安裝 Poetry

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

### 2) 進入後端目錄並安裝依賴

```bash
cd apps/backend
poetry install
```

### 3) 啟動開發伺服器

```bash
# 方式 1: 使用 poetry run
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2: 先啟動虛擬環境 shell
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) 執行合約測試

```bash
cd apps/backend
poetry run pytest ../specs/001-kcardswap-complete-spec/tests/contract_tests -q
```

說明：合約測試設計為 Test-First（Red），在後端實作並更新合約 JSON 的 `implemented: true` 後，測試才會通過（Green）。

## 常用 Poetry 命令

| 操作 | 命令 |
|------|------|
| 安裝所有依賴 | `poetry install` |
| 新增生產依賴 | `poetry add package-name` |
| 新增開發依賴 | `poetry add --group dev package-name` |
| 移除依賴 | `poetry remove package-name` |
| 更新依賴 | `poetry update` |
| 查看已安裝套件 | `poetry show` |
| 執行測試 | `poetry run pytest` |
| 執行 linting | `poetry run ruff check .` |

詳細說明請參考：`apps/backend/README.md`
