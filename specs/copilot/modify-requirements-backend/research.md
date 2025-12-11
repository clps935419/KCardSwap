# Phase 0 Research: Poetry 遷移技術研究

**日期**: 2025-12-11  
**研究範圍**: Poetry 依賴管理工具、Docker 整合、CI/CD 最佳實踐

---

## Section 1: Poetry 核心功能與最佳實踐

### 1.1 Poetry 依賴解析演算法

**研究發現**：
- Poetry 使用 **PubGrub** 演算法進行依賴解析，這是一個先進的版本求解器
- 自動處理傳遞依賴（transitive dependencies）的版本衝突
- 支援語義化版本（SemVer）範圍表達式：`^`（相容更新）、`~`（修補更新）、`>=`、`<` 等

**決策影響**：
- 無需手動管理版本衝突，Poetry 會自動找到最佳解
- 使用 `^` 符號定義依賴，允許次版本更新（例如 `^1.2.3` 允許 `>=1.2.3,<2.0.0`）

**範例**：
```toml
[tool.poetry.dependencies]
fastapi = "^0.109.1"  # 允許 0.109.x 和 0.x 系列的相容更新
pydantic = "^2.5.3"   # 允許 2.x 系列，但不包括 3.x
```

### 1.2 pyproject.toml 配置結構

**核心區段**：

1. **[tool.poetry]** - 專案元資料
   ```toml
   [tool.poetry]
   name = "kcardswap-backend"
   version = "0.1.0"
   description = "後端 API 服務"
   authors = ["Team <team@example.com>"]
   readme = "README.md"
   packages = [{include = "app"}]  # 指定打包目錄
   ```

2. **[tool.poetry.dependencies]** - 生產依賴
   ```toml
   [tool.poetry.dependencies]
   python = "^3.11"      # Python 版本約束
   fastapi = "^0.109.1"
   ```

3. **[tool.poetry.group.dev.dependencies]** - 開發依賴
   ```toml
   [tool.poetry.group.dev.dependencies]
   pytest = "^7.4.3"
   ruff = "^0.1.0"
   ```

4. **[build-system]** - 構建系統（PEP 517）
   ```toml
   [build-system]
   requires = ["poetry-core"]
   build-backend = "poetry.core.masonry.api"
   ```

**最佳實踐**：
- 將所有工具配置（pytest, ruff）整合於同一檔案
- 使用 dependency groups 明確分離不同用途的依賴
- packages 指定實際程式碼目錄，避免打包測試代碼

### 1.3 poetry.lock 鎖定機制

**運作原理**：
- `poetry lock` 命令解析所有依賴並生成確定性的 poetry.lock
- poetry.lock 記錄每個套件的精確版本、哈希值、來源
- 在 CI/CD 和團隊成員間，`poetry install` 會使用 lock 檔案確保一致性

**版本控制策略**：
```bash
# 應該納入版本控制
git add poetry.lock

# 鎖定檔案更新時機
poetry lock              # 僅更新 lock，不安裝
poetry lock --no-update  # 不解析新版本，僅重新鎖定現有依賴
poetry update package    # 更新特定套件
```

**決策**：
- ✅ poetry.lock 必須納入版本控制
- ✅ 每次依賴變更後執行 `poetry lock`
- ✅ CI 中驗證 lock 檔案是最新的：`poetry check --lock`

### 1.4 私有套件倉庫支援

**當前需求**：KCardSwap 專案目前僅使用 PyPI 公開套件，無私有倉庫需求。

**未來擴展**（若需要）：
```toml
[[tool.poetry.source]]
name = "private-pypi"
url = "https://pypi.example.com/simple"
priority = "supplemental"  # 或 "primary" / "default"
```

**決策**：此階段無需配置，保持預設 PyPI 來源。

---

## Section 2: Docker 多階段構建最佳化

### 2.1 Poetry 在 Docker 中的安裝方式

**方案比較**：

| 方法 | 優點 | 缺點 | 決策 |
|------|------|------|------|
| 官方安裝腳本 | 官方推薦，完整功能 | 映像稍大（~50MB） | ✅ 用於構建階段 |
| pip install poetry | 簡單快速 | 可能版本不一致 | ❌ 不推薦 |
| 預構建映像 | 最快 | 需額外維護 | ❌ 過度複雜 |

**最佳實踐**：
```dockerfile
# 構建階段：使用官方安裝腳本
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"
```

### 2.2 多階段構建策略

**設計目標**：
1. 構建階段：完整開發工具鏈（Poetry, compiler）
2. 執行階段：最小化依賴，僅運行時必需

**策略選擇**：

**選項 A：執行階段保留 Poetry**
```dockerfile
FROM python:3.11-slim
# 安裝 Poetry 並使用
COPY --from=builder /opt/poetry /opt/poetry
CMD ["poetry", "run", "uvicorn", "..."]
```
- ❌ 映像增大 ~50MB
- ❌ Poetry 僅用於啟動，浪費資源

**選項 B：導出 requirements.txt（推薦）** ✅
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
# 安裝 Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- ✅ 執行階段輕量（僅 pip + 依賴）
- ✅ 啟動速度快
- ✅ 安全性更好（減少攻擊面）

**決策**：採用選項 B

### 2.3 映像大小最佳化

**優化技巧**：

1. **使用 slim 基礎映像**
   ```dockerfile
   FROM python:3.11-slim  # ~150MB vs. python:3.11 ~900MB
   ```

2. **移除構建依賴**
   ```dockerfile
   RUN apt-get update && apt-get install -y --no-install-recommends \
       gcc \
       && pip install ... \
       && apt-get purge -y gcc \
       && apt-get autoremove -y \
       && rm -rf /var/lib/apt/lists/*
   ```

3. **避免快取目錄**
   ```dockerfile
   RUN pip install --no-cache-dir -r requirements.txt
   ```

4. **使用 .dockerignore**
   ```
   __pycache__
   *.pyc
   .pytest_cache
   .coverage
   poetry.lock  # 執行階段不需要
   ```

**預期結果**：
- 構建映像：~500MB（含 Poetry 和構建工具）
- 執行映像：~200MB（僅運行時依賴）

### 2.4 Docker Compose 整合

**本地開發配置**：
```yaml
version: '3.8'
services:
  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
    volumes:
      - ./apps/backend:/app  # 熱重載
    environment:
      - DATABASE_URL=postgresql://...
    command: poetry run uvicorn app.main:app --host 0.0.0.0 --reload
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    # ...
```

**決策**：
- 本地開發使用 volume mount + Poetry 直接執行（支援熱重載）
- 生產構建使用多階段優化映像

---

## Section 3: CI/CD 整合模式

### 3.1 GitHub Actions Poetry 快取策略

**官方 Action：snok/install-poetry**

**完整配置**：
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install Poetry
  uses: snok/install-poetry@v1
  with:
    version: 1.7.1
    virtualenvs-create: true
    virtualenvs-in-project: true  # .venv 在專案目錄內

- name: Load cached venv
  id: cached-poetry-dependencies
  uses: actions/cache@v3
  with:
    path: apps/backend/.venv
    key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

- name: Install dependencies
  if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
  run: poetry install --no-interaction --no-root
```

**快取效益**：
- 首次執行：~60 秒（安裝所有依賴）
- 快取命中：~5 秒（僅檢查 lock 檔案）

### 3.2 Lock 檔案驗證

**防止 lock 檔案過期**：
```yaml
- name: Check poetry.lock is up-to-date
  run: poetry check --lock
```

**效果**：
- 若 pyproject.toml 變更但未執行 `poetry lock`，CI 會失敗
- 強制開發者在 PR 前更新 lock 檔案

### 3.3 平行測試執行

**矩陣策略**（可選）：
```yaml
strategy:
  matrix:
    python-version: ['3.11']  # 目前僅 3.11，未來可擴展
    os: [ubuntu-latest]

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
  # ... Poetry 安裝與快取
```

**決策**：POC 階段僅測試 Python 3.11 + ubuntu-latest，簡化 CI。

### 3.4 GCP Cloud Build 支援

**Cloud Build 配置範例**：
```yaml
steps:
  # Step 1: 安裝 Poetry
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="/root/.local/bin:$PATH"
        cd apps/backend
        poetry install --no-dev
        poetry run pytest

  # Step 2: 構建 Docker 映像
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/backend', './apps/backend']
```

**決策**：優先使用 GitHub Actions，Cloud Build 作為備選方案。

---

## Section 4: 遷移策略與向下相容性

### 4.1 平滑遷移步驟

**Phase 1: 準備（不影響現有流程）**
1. 在 apps/backend/ 執行 `poetry init` 生成初始 pyproject.toml
2. 使用 `poetry add` 逐一添加現有依賴（從 requirements.txt 讀取）
3. 執行 `poetry lock` 生成 poetry.lock
4. 本地驗證：`poetry install && poetry run pytest`

**Phase 2: 更新工具鏈**
1. 更新 Dockerfile（保留多階段構建）
2. 更新 GitHub Actions 工作流程
3. 更新 README.md 與開發文件

**Phase 3: 切換（可回滾點）**
1. 合併 PR 至主分支
2. 團隊成員拉取變更並執行 `poetry install`
3. 監控 CI/CD 管道穩定性

**Phase 4: 清理（可選）**
1. 若穩定運行 2 週以上，可移除 requirements.txt
2. 簡化 Dockerfile（完全使用 Poetry）

### 4.2 向下相容性保障

**保留 requirements.txt 的方式**：

**方法 1：手動導出**
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev
```

**方法 2：Pre-commit hook 自動化**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: poetry-export
        name: Export requirements.txt
        entry: poetry export -f requirements.txt -o requirements.txt --without-hashes
        language: system
        pass_filenames: false
```

**方法 3：GitHub Actions 自動提交**
```yaml
- name: Export requirements.txt
  run: poetry export -f requirements.txt --output requirements.txt --without-hashes

- name: Commit if changed
  uses: stefanzweifel/git-auto-commit-action@v4
  with:
    commit_message: "chore: update requirements.txt from poetry"
    file_pattern: requirements.txt
```

**決策**：
- ✅ Phase 1-3 使用方法 1（手動導出）保持簡單
- ✅ Phase 4 評估是否需要自動化或完全移除

### 4.3 團隊學習曲線

**培訓計畫**：

**階段 1：基礎認知（30 分鐘）**
- Poetry 是什麼？與 pip 的差異
- 為何遷移？五大優勢說明
- 安裝 Poetry：`curl -sSL https://install.python-poetry.org | python3 -`

**階段 2：常用命令（30 分鐘）**
| pip 命令 | Poetry 等價命令 | 說明 |
|----------|------------------|------|
| `pip install package` | `poetry add package` | 新增依賴 |
| `pip install -r requirements.txt` | `poetry install` | 安裝所有依賴 |
| `pip uninstall package` | `poetry remove package` | 移除依賴 |
| `pip freeze > requirements.txt` | `poetry export ...` | 導出依賴列表 |
| `python -m venv .venv` | `poetry shell` | 啟動虛擬環境 |

**階段 3：實戰演練（30 分鐘）**
- Clone 專案並執行 `poetry install`
- 新增一個測試依賴：`poetry add --group dev faker`
- 執行測試：`poetry run pytest`
- 檢視依賴樹：`poetry show --tree`

**文件資源**：
- 內部 Wiki：Poetry 快速入門
- Cheat Sheet：pip vs Poetry 命令對照表
- 錄影教學：10 分鐘上手 Poetry

### 4.4 回滾計畫

**觸發條件**：
- CI/CD 管道持續失敗超過 24 小時
- Docker 構建問題無法在 2 個工作日內解決
- 團隊超過 50% 成員遇到嚴重阻礙

**回滾步驟**：

**Step 1: Git Revert**
```bash
git revert <commit-hash>  # 遷移 PR 的 commit
git push origin main
```

**Step 2: 恢復舊版文件**
```bash
# Dockerfile 改回使用 pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# GitHub Actions 改回使用 pip
- run: pip install -r requirements.txt
- run: pytest
```

**Step 3: 通知團隊**
- 發送通知：暫時恢復 pip 工作流程
- 重新評估遷移時機

**資料保存**：
- 保留 poetry.lock 作為參考（不刪除）
- 記錄遭遇的問題與解決嘗試

---

## 研究總結

### 關鍵決策摘要

| 決策點 | 選擇 | 理由 |
|--------|------|------|
| 依賴管理工具 | Poetry | 現代化、自動解析、鎖定機制 |
| Docker 策略 | 多階段 + 導出 requirements.txt | 最小化執行映像 |
| CI 快取策略 | 快取 .venv 目錄 | 大幅加速 CI |
| 向下相容 | 保留 requirements.txt（暫時）| 降低風險 |
| 團隊培訓 | 3 階段培訓計畫 | 平滑過渡 |

### 實作準備度

- ✅ 技術方案已驗證可行
- ✅ Docker 構建策略已設計
- ✅ CI/CD 整合方案已確認
- ✅ 回滾計畫已準備
- ✅ 團隊培訓計畫已規劃

### 下一步行動

1. 建立 PR：實作 pyproject.toml 與 poetry.lock
2. 更新 Dockerfile 與 GitHub Actions
3. 執行團隊培訓 session
4. 合併 PR 並監控 2 週
5. 評估是否移除 requirements.txt（Phase 4）

---

**研究完成日期**: 2025-12-11  
**研究者**: KCardSwap Technical Team  
**審查狀態**: 待技術負責人審查
