# KCardSwap Backend - Poetry 快速入門指南

**版本**: 1.0  
**更新日期**: 2025-12-11  
**適用對象**: 後端開發者、DevOps 工程師

---

## 📋 目錄

1. [安裝 Poetry](#安裝-poetry)
2. [首次設置專案](#首次設置專案)
3. [常用命令](#常用命令)
4. [開發工作流程](#開發工作流程)
5. [故障排除](#故障排除)
6. [pip vs Poetry 命令對照](#pip-vs-poetry-命令對照)

---

## 安裝 Poetry

### macOS / Linux

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 驗證安裝

```bash
poetry --version
# 預期輸出: Poetry (version 1.7.1)
```

### 配置 PATH

如果 `poetry` 命令找不到，請將以下路徑加入 PATH：

- **macOS/Linux**: `$HOME/.local/bin`
- **Windows**: `%APPDATA%\Python\Scripts`

**macOS/Linux 範例**：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## 首次設置專案

### 1. Clone 專案

```bash
git clone https://github.com/your-org/kcardswap.git
cd kcardswap/apps/backend
```

### 2. 安裝依賴

```bash
# 安裝所有依賴（生產 + 開發）
poetry install

# 僅安裝生產依賴（適用於生產環境）
poetry install --only main
```

### 3. 啟動虛擬環境

**方法 1：進入 Poetry Shell（推薦）**
```bash
poetry shell
# 現在你在虛擬環境中，可直接執行命令
uvicorn app.main:app --reload
pytest
```

**方法 2：使用 `poetry run` 前綴**
```bash
# 無需進入 shell，每次加上 poetry run
poetry run uvicorn app.main:app --reload
poetry run pytest
```

### 4. 驗證設置

```bash
# 檢查 Python 版本
poetry run python --version
# 預期: Python 3.11.x

# 執行測試
poetry run pytest
# 預期: 所有測試通過

# 執行 linting
poetry run ruff check .
# 預期: 無錯誤
```

---

## 常用命令

### 依賴管理

#### 新增依賴

```bash
# 新增生產依賴
poetry add fastapi
poetry add "sqlalchemy>=2.0.0"

# 新增開發依賴
poetry add --group dev pytest
poetry add --group dev ruff

# 新增特定版本
poetry add "pydantic==2.5.3"

# 新增帶 extras 的套件
poetry add "uvicorn[standard]"
```

#### 移除依賴

```bash
poetry remove package-name
poetry remove --group dev pytest-cov
```

#### 更新依賴

```bash
# 更新所有依賴至最新相容版本
poetry update

# 更新特定套件
poetry update fastapi pydantic

# 僅重新鎖定（不更新版本）
poetry lock --no-update
```

#### 查看依賴

```bash
# 列出所有已安裝套件
poetry show

# 查看特定套件詳情
poetry show fastapi

# 查看依賴樹
poetry show --tree

# 僅顯示過期套件
poetry show --outdated
```

### 虛擬環境管理

```bash
# 啟動 shell（進入虛擬環境）
poetry shell

# 查看虛擬環境路徑
poetry env info --path

# 列出所有虛擬環境
poetry env list

# 移除虛擬環境
poetry env remove python3.11
```

### 執行命令

```bash
# 在虛擬環境中執行任意命令
poetry run python script.py
poetry run uvicorn app.main:app --reload
poetry run pytest
poetry run ruff check .
```

### 導出與檢查

```bash
# 導出 requirements.txt（向下相容）
poetry export -f requirements.txt --output requirements.txt --without-hashes

# 導出開發依賴
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# 檢查 pyproject.toml 語法
poetry check

# 檢查 poetry.lock 是否最新
poetry check --lock
```

---

## 開發工作流程

### 日常開發循環

```bash
# 1. 拉取最新代碼
git pull origin main

# 2. 同步依賴（若 poetry.lock 有變更）
poetry install

# 3. 啟動開發伺服器
poetry run uvicorn app.main:app --reload

# 4. 執行測試（另一個終端）
poetry run pytest --cov=app

# 5. Linting 與格式化
poetry run ruff check .
poetry run ruff check --fix .  # 自動修正
```

### 新增功能流程

```bash
# 1. 建立功能分支
git checkout -b feature/new-endpoint

# 2. 如需新增依賴
poetry add httpx

# 3. 開發並測試
poetry run pytest tests/test_new_endpoint.py

# 4. 提交變更（包含 pyproject.toml 和 poetry.lock）
git add pyproject.toml poetry.lock
git commit -m "feat: add new endpoint"

# 5. 推送並建立 PR
git push origin feature/new-endpoint
```

### 本地測試 Docker 構建

```bash
# 從 backend 目錄構建
docker build -t kcardswap-backend:local .

# 執行容器
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  kcardswap-backend:local
```

---

## 故障排除

### 問題 1: `poetry: command not found`

**原因**: Poetry 未加入 PATH

**解決方案**:
```bash
# macOS/Linux
export PATH="$HOME/.local/bin:$PATH"

# 或重新安裝
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | python3 -
```

### 問題 2: `poetry install` 速度很慢

**原因**: 依賴解析或下載緩慢

**解決方案**:
```bash
# 使用國內鏡像（中國地區）
poetry config repositories.tsinghua https://pypi.tuna.tsinghua.edu.cn/simple
poetry config repositories.aliyun https://mirrors.aliyun.com/pypi/simple/

# 或清除快取後重試
poetry cache clear pypi --all
poetry install
```

### 問題 3: `SolverProblemError` 依賴衝突

**原因**: 依賴版本不相容

**解決方案**:
```bash
# 查看詳細錯誤訊息
poetry add package-name -vvv

# 放寬版本約束
# 在 pyproject.toml 中將 ^2.5.3 改為 >=2.5.3,<3.0.0

# 更新 lock 檔案
poetry lock --no-update
poetry install
```

### 問題 4: `poetry.lock` 過期警告

**警告訊息**: `Warning: poetry.lock is not consistent with pyproject.toml`

**解決方案**:
```bash
# 重新生成 lock 檔案
poetry lock --no-update

# 若需要更新依賴版本
poetry update
```

### 問題 5: 虛擬環境找不到套件

**原因**: 套件未正確安裝或虛擬環境損壞

**解決方案**:
```bash
# 重新建立虛擬環境
poetry env remove python3.11
poetry install

# 驗證安裝
poetry run python -c "import fastapi; print(fastapi.__version__)"
```

### 問題 6: CI/CD 中 Poetry 安裝失敗

**原因**: 網路問題或版本不符

**解決方案** (GitHub Actions):
```yaml
- name: Install Poetry
  uses: snok/install-poetry@v1
  with:
    version: 1.7.1
    virtualenvs-create: true
    virtualenvs-in-project: true
```

---

## pip vs Poetry 命令對照

| 操作 | pip | Poetry |
|------|-----|--------|
| 安裝依賴 | `pip install package` | `poetry add package` |
| 安裝開發依賴 | `pip install -r requirements-dev.txt` | `poetry add --group dev package` |
| 移除依賴 | `pip uninstall package` | `poetry remove package` |
| 列出套件 | `pip list` | `poetry show` |
| 匯出依賴 | `pip freeze > requirements.txt` | `poetry export -f requirements.txt -o requirements.txt` |
| 更新套件 | `pip install --upgrade package` | `poetry update package` |
| 建立虛擬環境 | `python -m venv .venv` | `poetry shell` (自動建立) |
| 啟動虛擬環境 | `source .venv/bin/activate` | `poetry shell` |
| 執行命令 | `python script.py` | `poetry run python script.py` |
| 檢查依賴 | `pip check` | `poetry check` |

---

## 進階配置

### 配置 Poetry 行為

```bash
# 在專案目錄內建立虛擬環境（推薦）
poetry config virtualenvs.in-project true

# 查看所有配置
poetry config --list

# 禁用虛擬環境（若使用 Docker）
poetry config virtualenvs.create false
```

### pyproject.toml 常用區段

```toml
[tool.poetry]
name = "kcardswap-backend"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.1"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=app"

[tool.ruff]
line-length = 88
```

### 使用 Scripts（類似 npm scripts）

在 `pyproject.toml` 中定義快捷命令：

```toml
[tool.poetry.scripts]
dev = "uvicorn app.main:app --reload"
test = "pytest"
lint = "ruff check ."
```

執行：
```bash
poetry run dev
poetry run test
poetry run lint
```

---

## 常見問題 FAQ

**Q: Poetry 和 pip 可以混用嗎？**  
A: 不建議。混用可能導致依賴衝突。統一使用 Poetry 管理依賴。

**Q: 如何在 Docker 中使用 Poetry？**  
A: 參考專案的 Dockerfile，使用多階段構建並導出 requirements.txt。

**Q: poetry.lock 需要提交到 Git 嗎？**  
A: 是的！這確保團隊成員使用相同的依賴版本。

**Q: 如何指定 Python 版本？**  
A: 在 `pyproject.toml` 中設定 `python = "^3.11"`，Poetry 會使用符合的 Python。

**Q: Poetry 安裝很慢，如何加速？**  
A: 使用 `--no-root` 選項：`poetry install --no-root`（若不需安裝專案本身）。

**Q: 如何升級 Poetry 本身？**  
A: `poetry self update` 或重新執行安裝腳本。

---

## 參考資源

- **官方文件**: https://python-poetry.org/docs/
- **命令參考**: https://python-poetry.org/docs/cli/
- **依賴規範**: https://python-poetry.org/docs/dependency-specification/
- **內部 Wiki**: [連結待補充]
- **團隊 Slack 頻道**: #backend-dev

---

## 變更日誌

| 版本 | 日期 | 變更內容 |
|------|------|----------|
| 1.0 | 2025-12-11 | 初始版本，遷移至 Poetry |

---

**需要協助？**  
請在 Slack #backend-dev 頻道提問，或聯繫技術負責人。
