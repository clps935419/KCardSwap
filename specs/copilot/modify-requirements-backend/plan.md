# Implementation Plan: 後端依賴管理遷移 (pip → Poetry)

**Branch**: `copilot/modify-requirements-backend` | **Date**: 2025-12-11 | **Spec**: [specs/001-kcardswap-complete-spec/spec.md](../001-kcardswap-complete-spec/spec.md)
**Input**: Development Environment Requirements (DR-001 至 DR-005)

## Summary

本計畫實作後端依賴管理工具從傳統 pip/requirements.txt 遷移至 Poetry，以提升依賴管理的可靠性、可重現性與開發體驗。此變更影響開發環境設置、Docker 構建流程與 CI/CD 管道。

**核心變更**：
1. 採用 Poetry 作為唯一依賴管理工具
2. 在 pyproject.toml 中統一定義專案元資料、依賴與工具配置
3. 使用 poetry.lock 確保跨環境的版本一致性
4. 明確分離開發依賴與生產依賴
5. 更新 Docker 與 CI/CD 以支援 Poetry 工作流程

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: 
- FastAPI (Web 框架)
- SQLAlchemy (ORM)
- Pydantic (資料驗證)
- Poetry (依賴管理工具，本次遷移重點)

**Current Dependency Management**: pip + requirements.txt + requirements-dev.txt  
**Target Dependency Management**: Poetry + pyproject.toml + poetry.lock

**Storage**: PostgreSQL (via SQLAlchemy)  
**Testing**: pytest + pytest-asyncio + pytest-cov  
**Target Platform**: Linux server (Docker 容器，Cloud Run/GKE)  
**Project Type**: Web API (Mobile + API 架構的後端部分)  
**Performance Goals**: 1000 req/s (POC 階段 100-200 MAU)  
**Constraints**: 
- 依賴版本必須可重現（跨開發/測試/生產環境）
- Docker 映像構建時間應保持合理（< 5 分鐘）
- CI/CD 管道執行時間不應顯著增加

**Scale/Scope**: 
- 單一後端專案 (apps/backend)
- 約 10-15 個主要 Python 依賴套件
- 5-8 個開發專用依賴套件

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase -1 Gates 檢查結果

#### 1. Simplicity Gate ✅ **PASS**
**規則**：避免不必要的抽象層；優先選擇簡單直接的解決方案。

**評估**：
- Poetry 是業界標準的現代化工具，非自創抽象
- 取代多檔案依賴管理（requirements.txt + requirements-dev.txt）為單一 pyproject.toml
- 內建功能取代手動虛擬環境管理
- 減少複雜度：不需額外的 pip-tools、virtualenv 等工具

**結論**：符合簡化原則，實際上降低了工具鏈複雜度。

#### 2. Anti-Abstraction Gate ✅ **PASS**
**規則**：不建立過度抽象；每個抽象層必須有明確的實際需求。

**評估**：
- Poetry 不引入新的抽象層，而是標準化工具
- pyproject.toml 是 Python 生態系統的 PEP 518 標準
- 沒有創建自定義包裝器或中間層
- 直接使用工具的原生介面

**結論**：無過度抽象問題。

#### 3. Integration-First Gate ✅ **PASS**
**規則**：優先選擇與現有工具和流程整合良好的方案。

**評估**：
- Poetry 與 pytest、ruff、Docker、GitHub Actions 完全相容
- 支援標準 Python 打包格式（wheel, sdist）
- 可匯出 requirements.txt 作為向下相容方案
- GCP Cloud Run/GKE 支援 Poetry 構建的容器

**結論**：與整個技術堆疊整合良好。

### Constitution 相容性總結

此變更完全符合 KCardSwap 專案憲法的核心原則：

1. **測試優先開發**：Poetry 不影響測試策略，pytest 完全支援
2. **程式碼品質標準**：Ruff 可透過 Poetry 管理與執行
3. **CI/CD 管道**：GitHub Actions 有官方 Poetry 支援
4. **開發工作流程**：簡化依賴安裝與環境設置流程

**憲章條款對應**：
- 後端架構 → 技術堆疊更新（增加 Poetry）
- DevOps → CI/CD 管道需更新使用 Poetry 命令
- 本地開發環境 → 開發者需安裝 Poetry

## Project Structure

### Documentation (this feature)

```text
specs/copilot/modify-requirements-backend/
├── plan.md              # 本文件（實作計畫）
├── research.md          # Phase 0: Poetry 工具研究與最佳實踐
├── data-model.md        # N/A（本次無資料模型變更）
├── quickstart.md        # Phase 1: Poetry 快速入門指南
└── contracts/           # N/A（本次無 API 變更）
```

### Source Code (repository root)

```text
apps/backend/                    # Python FastAPI 後端
├── app/                         # 應用程式碼
│   ├── models/                  # SQLAlchemy 模型
│   ├── services/                # 業務邏輯層
│   ├── api/                     # API 路由
│   └── core/                    # 核心配置與工具
├── tests/                       # 測試套件
│   ├── unit/                    # 單元測試
│   └── integration/             # 整合測試
├── pyproject.toml               # [更新] Poetry 專案配置 + 工具設定
├── poetry.lock                  # [新增] 鎖定依賴版本
├── requirements.txt             # [保留暫時] 向下相容（可由 Poetry 匯出）
├── requirements-dev.txt         # [移除] 整合至 pyproject.toml
└── README.md                    # [更新] 新增 Poetry 設置說明

gateway/kong/                    # Kong API Gateway（無變更）
infra/                           # 基礎設施配置
├── docker/                      # [更新] Dockerfile 支援 Poetry
└── ci/                          # [更新] GitHub Actions 工作流程

.github/workflows/               # CI/CD 管道
├── backend-ci.yml               # [更新] 使用 Poetry 命令
└── deploy.yml                   # [更新] 部署流程調整
```

**Structure Decision**: 
採用 Web application 架構（Option 2），前端（未來 React Native）與後端（FastAPI）分離。本次變更僅影響 `apps/backend/` 目錄及相關基礎設施配置。保持既有目錄結構，僅變更依賴管理方式。

## Complexity Tracking

> 本次變更無需填寫 - 未違反任何 Constitution Gates

此遷移實際上**降低**了複雜度：
- 工具數量：多工具（pip + virtualenv + pip-tools）→ 單一工具（Poetry）
- 配置檔案：2 個（requirements.txt + requirements-dev.txt）→ 1 個（pyproject.toml）
- 依賴解析：手動管理版本衝突 → Poetry 自動解析
- 環境管理：手動建立虛擬環境 → Poetry 自動處理

## Phase 0: Research & Technical Decisions

### 研究主題

#### 1. Poetry 核心功能與最佳實踐
**研究問題**：
- Poetry 的依賴解析演算法如何運作？
- 如何正確配置 pyproject.toml 的各個區段？
- poetry.lock 的鎖定機制與版本控制策略？
- 如何處理私有套件倉庫（若需要）？

**輸出位置**：`research.md` - Section 1

#### 2. Docker 多階段構建最佳化
**研究問題**：
- 如何在 Docker 中高效安裝 Poetry？
- 多階段構建策略：構建階段 vs 執行階段
- 如何最小化最終映像大小？
- 是否在生產映像中保留 Poetry 或僅使用導出的 requirements.txt？

**輸出位置**：`research.md` - Section 2

#### 3. CI/CD 整合模式
**研究問題**：
- GitHub Actions 中 Poetry 快取策略？
- 如何在 CI 中驗證 poetry.lock 是最新的？
- 平行測試執行與 Poetry 環境隔離？
- GCP Cloud Build 是否支援 Poetry？

**輸出位置**：`research.md` - Section 3

#### 4. 遷移策略與向下相容性
**研究問題**：
- 如何平滑遷移現有依賴？
- 是否保留 requirements.txt 作為備援？
- 團隊成員學習曲線與文件需求？
- 回滾計畫（若遷移失敗）？

**輸出位置**：`research.md` - Section 4

### 技術決策記錄

#### Decision 1: 採用 Poetry 完全取代 pip
**選擇**：Poetry 作為唯一依賴管理工具

**理由**：
1. **依賴解析**：自動解決版本衝突，避免手動 pin 版本
2. **鎖定機制**：poetry.lock 確保所有環境完全一致
3. **開發體驗**：`poetry add/remove` 比 `pip install` + 手動編輯更直觀
4. **標準化**：pyproject.toml 是 PEP 518/517 標準，未來趨勢
5. **整合工具配置**：pytest、ruff、black 配置可整合於同一檔案

**捨棄方案**：
- pip-tools：需額外工具，Poetry 功能更完整
- pipenv：社群活躍度較低，Poetry 更現代化
- 保持 pip：無法解決版本鎖定與依賴衝突問題

#### Decision 2: Docker 構建策略
**選擇**：多階段構建 + Poetry 導出 requirements.txt

**理由**：
1. 構建階段使用完整 Poetry 環境
2. 執行階段使用輕量 pip 安裝（從導出的 requirements.txt）
3. 最終映像不包含 Poetry，減少大小約 50MB
4. 保持啟動速度與安全性

**捨棄方案**：
- 在生產映像保留 Poetry：增加映像大小，無必要
- 完全不使用 Poetry 構建：失去依賴鎖定優勢

#### Decision 3: 保留 requirements.txt（暫時）
**選擇**：使用 `poetry export` 自動生成 requirements.txt

**理由**：
1. 向下相容某些工具或流程（如果存在）
2. 作為備援方案，降低風險
3. 可透過 CI 自動化生成，無維護負擔
4. 未來可完全移除（待穩定後）

**時程**：Phase 2 穩定後評估移除

## Phase 1: Design & Implementation

### 1. pyproject.toml 設計

#### 專案元資料區段
```toml
[tool.poetry]
name = "kcardswap-backend"
version = "0.1.0"
description = "KCardSwap Backend API - 韓國偶像小卡交換平台後端服務"
authors = ["KCardSwap Team"]
readme = "README.md"
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.1"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
psycopg2-binary = "^2.9.9"
pydantic = "^2.5.3"
pydantic-settings = "^2.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.18"
sqlalchemy = "^2.0.0"      # 未來新增
alembic = "^1.13.0"        # 未來新增

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
httpx = "^0.26.0"
pytest-cov = "^4.1.0"
ruff = "^0.1.0"            # 取代 black + isort

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### 工具配置整合
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --disable-warnings --cov=app --cov-report=term-missing"

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
```

### 2. Docker 多階段構建

#### Dockerfile 設計
```dockerfile
# Stage 1: Builder - 安裝 Poetry 並導出依賴
FROM python:3.11-slim as builder

# 安裝 Poetry
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# 複製依賴定義
COPY pyproject.toml poetry.lock ./

# 導出 requirements.txt（用於生產階段）
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev

# Stage 2: Runtime - 輕量執行環境
FROM python:3.11-slim

WORKDIR /app

# 從 builder 複製 requirements.txt
COPY --from=builder /app/requirements.txt .

# 使用 pip 安裝（快速且最小化）
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY ./app ./app

# 執行
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. CI/CD 工作流程更新

#### GitHub Actions 配置
```yaml
name: Backend CI

on:
  pull_request:
    paths:
      - 'apps/backend/**'
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: 1.7.1
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v3
        with:
          path: apps/backend/.venv
          key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        working-directory: apps/backend
        run: poetry install --no-interaction --no-root
      
      - name: Run Ruff
        working-directory: apps/backend
        run: poetry run ruff check .
      
      - name: Run tests
        working-directory: apps/backend
        run: poetry run pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./apps/backend/coverage.xml
```

### 4. 開發環境設置指南

#### quickstart.md 內容大綱
```markdown
# KCardSwap Backend - Poetry 快速入門

## 安裝 Poetry
\`\`\`bash
curl -sSL https://install.python-poetry.org | python3 -
\`\`\`

## 設置專案
\`\`\`bash
cd apps/backend
poetry install              # 安裝所有依賴（含開發依賴）
poetry shell                # 啟動虛擬環境
\`\`\`

## 常用命令
\`\`\`bash
poetry add fastapi          # 新增生產依賴
poetry add --group dev pytest  # 新增開發依賴
poetry remove package-name  # 移除依賴
poetry update               # 更新依賴至最新相容版本
poetry show                 # 列出所有已安裝套件
poetry export -f requirements.txt --output requirements.txt  # 導出 requirements.txt
\`\`\`

## 執行測試
\`\`\`bash
poetry run pytest           # 執行所有測試
poetry run pytest --cov=app # 執行測試並計算覆蓋率
poetry run ruff check .     # 執行 linting
\`\`\`

## 本地開發伺服器
\`\`\`bash
poetry run uvicorn app.main:app --reload
\`\`\`
```

## Phase 2: Migration Tasks (Not in this plan)

**注意**：Phase 2 任務分解將由 `/speckit.tasks` 命令生成，不在本 plan.md 範圍內。

預期任務類型：
- 更新 pyproject.toml 並執行 `poetry lock`
- 更新 Dockerfile
- 更新 GitHub Actions 工作流程
- 更新 README.md 與開發文件
- 驗證 Docker 構建
- 驗證 CI/CD 管道
- 團隊培訓與知識轉移

## Risk Assessment & Mitigation

### 風險 1: 團隊學習曲線
**影響**: 中  
**機率**: 高  
**緩解措施**:
- 提供詳細的 quickstart.md
- 舉辦團隊培訓 session
- 在 README 中增加常見問題 FAQ
- Poetry 命令與 pip 命令對照表

### 風險 2: Docker 構建時間增加
**影響**: 低  
**機率**: 中  
**緩解措施**:
- 使用多階段構建最佳化
- CI/CD 快取 Poetry 虛擬環境
- 僅在依賴變更時重建

### 風險 3: 與現有工具相容性問題
**影響**: 中  
**機率**: 低  
**緩解措施**:
- 保留 requirements.txt 作為備援（自動導出）
- 充分測試 CI/CD 管道
- 逐步遷移，保持向下相容

### 風險 4: poetry.lock 合併衝突
**影響**: 低  
**機率**: 中  
**緩解措施**:
- 在 PR 中明確溝通依賴變更
- 使用 `poetry lock --no-update` 最小化變更
- 建立依賴更新流程指南

## Success Criteria

### 技術驗證
- [ ] `poetry install` 在乾淨環境中成功執行
- [ ] 所有現有測試通過（使用 `poetry run pytest`）
- [ ] Docker 映像成功構建並可在本地執行
- [ ] CI/CD 管道通過所有檢查
- [ ] Ruff linting 通過

### 文件完整性
- [ ] README.md 包含 Poetry 安裝與使用說明
- [ ] quickstart.md 提供完整開發環境設置指南
- [ ] CONTRIBUTING.md 更新依賴管理流程（如存在）

### 團隊準備度
- [ ] 至少一位團隊成員完成 Poetry 培訓
- [ ] 團隊成員可在本地環境成功設置專案
- [ ] 常見問題 FAQ 文件準備就緒

## Rollback Plan

若遷移過程中遇到無法解決的問題，可執行以下回滾步驟：

1. **保留 requirements.txt**：本次遷移保留自動生成的 requirements.txt，可立即切回
2. **Git revert**：所有變更均在單一 PR 中，可整體 revert
3. **Docker fallback**：Dockerfile 可快速改回使用 pip + requirements.txt
4. **CI/CD rollback**：恢復舊版 GitHub Actions 工作流程

**回滾決策點**：若在 Phase 2 執行過程中發現嚴重阻礙（如 CI 持續失敗、Docker 構建問題無法解決），團隊可決定暫緩遷移。

## References

- [Poetry 官方文件](https://python-poetry.org/docs/)
- [PEP 518 - Specifying Minimum Build System Requirements](https://peps.python.org/pep-0518/)
- [Poetry Docker 最佳實踐](https://github.com/python-poetry/poetry/discussions/1879)
- [GitHub Actions Poetry 整合範例](https://github.com/snok/install-poetry)

---

**計畫狀態**: Phase 0-1 完成，待執行 Phase 2 任務分解與實作
**最後更新**: 2025-12-11
**審查者**: [待指派]
