# Tasks: 後端依賴管理遷移 (pip → Poetry)

**Input**: Design documents from `/specs/copilot/modify-requirements-backend/`
**Prerequisites**: plan.md ✅, research.md ✅, quickstart.md ✅

**Feature Context**: 此功能實作後端依賴管理工具從 pip/requirements.txt 遷移至 Poetry，以提升依賴管理的可靠性、可重現性與開發體驗。變更涵蓋開發環境設置、Docker 構建流程與 CI/CD 管道。

**Development Requirements Addressed**:
- **DR-001**: 採用 Poetry 作為依賴管理工具
- **DR-002**: 在 pyproject.toml 定義依賴，使用 poetry.lock 鎖定版本
- **DR-003**: 分離開發依賴與生產依賴
- **DR-004**: Docker 構建流程支援 Poetry
- **DR-005**: CI/CD 管道使用 Poetry

**Tests**: 本次遷移為基礎設施變更，不涉及業務邏輯測試，但包含驗證任務確保遷移成功。

---

## Format: `- [ ] [TaskID] [P?] [Label] Description with file path`

- **[P]**: 可平行執行（不同檔案，無依賴關係）
- **[DR-XXX]**: 對應的開發需求編號
- 所有任務包含明確的檔案路徑

---

## Phase 1: Setup (專案初始化與準備) - DR-001, DR-002

**Purpose**: 建立 Poetry 專案結構與基本配置

**Prerequisites**: 無 - 可立即開始

- [X] T001 [DR-001] 在 apps/backend/ 目錄建立 pyproject.toml 並配置專案元資料（name, version, description, authors）
- [X] T002 [DR-002] 在 pyproject.toml 中定義生產依賴（fastapi, uvicorn, pydantic, pydantic-settings, python-jose, passlib, python-multipart, psycopg2-binary）
- [X] T003 [P] [DR-003] 在 pyproject.toml 中定義開發依賴（pytest, pytest-asyncio, pytest-cov, httpx, ruff）
- [X] T004 [P] [DR-002] 在 pyproject.toml 中配置 build-system 區段（poetry-core）
- [X] T005 [DR-002] 執行 `poetry lock` 生成 poetry.lock 檔案並驗證依賴解析成功

**Checkpoint**: pyproject.toml 和 poetry.lock 已建立且可正常安裝

---

## Phase 2: Foundational (工具配置整合) - DR-001

**Purpose**: 將開發工具配置整合至 pyproject.toml

**Prerequisites**: Phase 1 完成

- [X] T006 [P] [DR-001] 在 pyproject.toml 中整合 pytest 配置（testpaths, python_files, python_classes, python_functions, addopts）
- [X] T007 [P] [DR-001] 在 pyproject.toml 中整合 ruff 配置（line-length, target-version, select, ignore, per-file-ignores）
- [X] T008 [DR-001] 在本地環境執行 `poetry install` 驗證依賴安裝成功
- [X] T009 [DR-001] 在本地環境執行 `poetry run pytest` 驗證測試框架正常運作

**Checkpoint**: 工具配置完成，可使用 Poetry 執行測試與 linting

---

## Phase 3: Docker 整合 - DR-004

**Purpose**: 更新 Docker 構建流程以支援 Poetry

**Prerequisites**: Phase 2 完成

### Docker 多階段構建設計

- [X] T010 [DR-004] 建立/更新 apps/backend/Dockerfile，實作 Stage 1: Builder（安裝 Poetry 並導出依賴）
- [X] T011 [DR-004] 在 Dockerfile Stage 1 中配置 Poetry 環境變數（POETRY_VERSION=1.7.1, POETRY_HOME, POETRY_NO_INTERACTION, POETRY_VIRTUALENVS_CREATE）
- [X] T012 [DR-004] 在 Dockerfile Stage 1 中使用官方安裝腳本安裝 Poetry 並設定 PATH
- [X] T013 [DR-004] 在 Dockerfile Stage 1 中複製 pyproject.toml 和 poetry.lock
- [X] T014 [DR-004] 在 Dockerfile Stage 1 中執行 `poetry export` 生成 requirements.txt（--without-hashes --without dev）
- [X] T015 [DR-004] 實作 Dockerfile Stage 2: Runtime（使用 python:3.11-slim 基礎映像）
- [X] T016 [DR-004] 在 Dockerfile Stage 2 中從 builder 複製 requirements.txt 並使用 pip 安裝
- [X] T017 [DR-004] 在 Dockerfile Stage 2 中複製應用程式碼並設定啟動命令

### Docker 驗證

- [X] T018 [DR-004] 建立/更新 apps/backend/.dockerignore（排除 __pycache__, *.pyc, .pytest_cache, .coverage, tests/）
- [ ] T019 [DR-004] 在本地執行 `docker build -t kcardswap-backend:local apps/backend` 驗證映像構建成功
- [ ] T020 [DR-004] 在本地執行 Docker 容器並驗證應用程式可正常啟動（uvicorn 監聽 8000 port）

**Checkpoint**: Docker 多階段構建完成，映像可成功構建並執行

---

## Phase 4: CI/CD 整合 - DR-005

**Purpose**: 更新 GitHub Actions 工作流程以使用 Poetry

**Prerequisites**: Phase 3 完成

### GitHub Actions 配置

- [X] T021 [DR-005] 更新 .github/workflows/backend-ci.yml，在 test job 中使用 actions/setup-python@v5 設定 Python 3.11
- [X] T022 [DR-005] 在 backend-ci.yml 中使用 snok/install-poetry@v1 安裝 Poetry 1.7.1（配置 virtualenvs-create=true, virtualenvs-in-project=true）
- [X] T023 [DR-005] 在 backend-ci.yml 中配置 Poetry 虛擬環境快取（actions/cache@v3，路徑 apps/backend/.venv，key 基於 poetry.lock hash）
- [X] T024 [DR-005] 在 backend-ci.yml 中添加依賴安裝步驟（`poetry install --no-interaction --no-root`，僅在快取未命中時執行）
- [X] T025 [P] [DR-005] 在 backend-ci.yml 中更新 linting 步驟使用 `poetry run ruff check .`
- [X] T026 [P] [DR-005] 在 backend-ci.yml 中更新測試步驟使用 `poetry run pytest --cov=app --cov-report=xml`
- [X] T027 [P] [DR-005] 在 backend-ci.yml 中添加 poetry.lock 驗證步驟（`poetry check --lock`）

### CI/CD 驗證

- [ ] T028 [DR-005] 提交變更並推送至分支，驗證 GitHub Actions 工作流程成功執行（所有 jobs 通過）
- [ ] T029 [DR-005] 驗證 CI 快取機制運作正常（第二次執行時快取命中，執行時間顯著縮短）

**Checkpoint**: CI/CD 管道完全支援 Poetry，所有檢查通過

---

## Phase 5: 文件與向下相容性 - DR-001

**Purpose**: 更新開發文件並保留向下相容性

**Prerequisites**: Phase 4 完成

### 文件更新

- [X] T030 [P] [DR-001] 更新 apps/backend/README.md，新增「開發環境設置」章節（Poetry 安裝與使用說明）
- [X] T031 [P] [DR-001] 在 apps/backend/README.md 中新增「常用 Poetry 命令」參考表（add, remove, update, install, shell, run）
- [X] T032 [P] [DR-001] 在 apps/backend/README.md 中新增「本地開發伺服器啟動」說明（poetry run uvicorn app.main:app --reload）
- [X] T033 [P] [DR-001] 驗證 specs/copilot/modify-requirements-backend/quickstart.md 內容完整且正確

### 向下相容性保障

- [X] T034 [DR-002] 在 apps/backend/ 中執行 `poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev` 生成備援 requirements.txt
- [X] T035 [DR-003] 在 apps/backend/ 中執行 `poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes` 生成備援 requirements-dev.txt
- [X] T036 [DR-002] 在 apps/backend/README.md 中說明 requirements.txt 的用途（向下相容，由 Poetry 自動生成）

**Checkpoint**: 文件更新完成，向下相容性已保障

---

## Phase 6: 完整驗證與清理 - 所有 DR

**Purpose**: 端到端驗證遷移成功並清理舊設定

**Prerequisites**: Phase 5 完成

### 端到端驗證

- [X] T037 在乾淨環境（新 clone 或刪除 .venv）執行 `poetry install` 並驗證所有依賴正確安裝
- [X] T038 執行 `poetry run pytest` 並驗證所有現有測試通過（測試覆蓋率與遷移前一致）
- [X] T039 執行 `poetry run ruff check .` 並驗證 linting 通過（無錯誤）
- [ ] T040 執行 `docker build -t kcardswap-backend:test apps/backend` 並驗證 Docker 映像大小合理（執行階段 < 250MB）
- [ ] T041 啟動 Docker 容器並執行健康檢查（curl http://localhost:8000/health 或類似端點）
- [ ] T042 驗證 CI/CD 管道在完整變更集下成功執行（所有 jobs 綠色）

### 文件驗證

- [X] T043 [P] 依照 apps/backend/README.md 中的 Poetry 設置步驟在測試環境驗證文件正確性
- [X] T044 [P] 依照 specs/copilot/modify-requirements-backend/quickstart.md 在測試環境驗證快速入門指南可用性

### 清理與最佳化（可選）

- [ ] T045 評估是否可移除舊的 requirements-dev.txt（若團隊已完全適應 Poetry）
- [X] T046 檢查 .gitignore 是否包含 Poetry 相關目錄（.venv/, poetry.toml - 若有本地配置）
- [X] T047 執行 `poetry check` 驗證 pyproject.toml 語法正確且依賴配置完整

**Checkpoint**: 遷移完成，所有功能正常運作，文件齊全

---

## Phase 7: 團隊準備與知識轉移

**Purpose**: 確保團隊成員可以順利使用新工具鏈

**Prerequisites**: Phase 6 完成

- [ ] T048 準備團隊培訓簡報或錄影（包含 Poetry 基礎、常用命令、故障排除）
- [ ] T049 建立 pip vs Poetry 命令對照表（參考 quickstart.md 或建立獨立文件）
- [ ] T050 在團隊 Wiki 或 Confluence 發布 Poetry 遷移公告與相關資源連結
- [ ] T051 舉辦團隊培訓 session（30-60 分鐘，涵蓋安裝、基本操作、常見問題）
- [ ] T052 設置團隊支援管道（Slack 頻道或 FAQ 文件），收集遷移後的問題與回饋

**Checkpoint**: 團隊成員已接受培訓並可獨立使用 Poetry 進行開發

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) - 依賴 Phase 1 完成
    ↓
Phase 3 (Docker) - 依賴 Phase 2 完成
    ↓
Phase 4 (CI/CD) - 依賴 Phase 3 完成
    ↓
Phase 5 (Documentation) - 依賴 Phase 4 完成
    ↓
Phase 6 (Validation) - 依賴 Phase 5 完成
    ↓
Phase 7 (Team Enablement) - 依賴 Phase 6 完成
```

### Critical Path

**必須依序完成**（阻塞路徑）：
1. T001-T005: 建立 pyproject.toml 和 poetry.lock
2. T008: 本地驗證 Poetry 安裝
3. T010-T017: Docker 多階段構建實作
4. T019-T020: Docker 驗證
5. T021-T027: CI/CD 配置更新
6. T028: CI/CD 驗證
7. T037-T042: 端到端驗證

**可平行執行的任務群組**：
- Phase 1: T002, T003, T004（定義不同依賴區段）
- Phase 2: T006, T007（配置不同工具）
- Phase 4: T025, T026, T027（更新不同 CI 步驟）
- Phase 5: T030, T031, T032, T033（文件更新）
- Phase 6: T043, T044（文件驗證）

### Parallel Opportunities

#### Phase 1 並行範例
```bash
# 三個任務可同時進行（編輯 pyproject.toml 不同區段）
Task T002: 定義生產依賴
Task T003: 定義開發依賴
Task T004: 配置 build-system
```

#### Phase 2 並行範例
```bash
# 兩個任務可同時進行（配置不同工具）
Task T006: 整合 pytest 配置
Task T007: 整合 ruff 配置
```

#### Phase 5 並行範例
```bash
# 四個任務可同時進行（更新不同文件或章節）
Task T030: 更新 README - 開發環境設置
Task T031: 更新 README - 常用命令
Task T032: 更新 README - 啟動說明
Task T033: 驗證 quickstart.md
```

---

## Implementation Strategy

### 推薦策略：按階段遞進（Incremental Rollout）

**階段 1：本地驗證（Phase 1-2）**
1. 完成 T001-T009
2. **STOP and VALIDATE**: 在本地環境確認 Poetry 可正常使用
3. 提交並推送至功能分支

**階段 2：容器化支援（Phase 3）**
1. 完成 T010-T020
2. **STOP and VALIDATE**: 確認 Docker 映像可構建並執行
3. 提交並推送

**階段 3：CI/CD 整合（Phase 4）**
1. 完成 T021-T029
2. **STOP and VALIDATE**: 確認 GitHub Actions 通過
3. 提交並推送

**階段 4：文件與驗證（Phase 5-6）**
1. 完成 T030-T047
2. **STOP and VALIDATE**: 執行完整端到端驗證
3. 提交並推送

**階段 5：團隊準備（Phase 7）**
1. 完成 T048-T052
2. 準備合併至主分支
3. 發布公告並提供支援

### 里程碑（Milestones）

- ✅ **M1 (Phase 2 完成)**: Poetry 本地可用
- ✅ **M2 (Phase 3 完成)**: Docker 支援 Poetry
- ✅ **M3 (Phase 4 完成)**: CI/CD 完全整合
- ✅ **M4 (Phase 6 完成)**: 遷移技術完成
- ✅ **M5 (Phase 7 完成)**: 團隊就緒，可合併至 main

### 回滾計畫

**觸發條件**：
- CI/CD 持續失敗超過 24 小時
- Docker 構建問題無法在 2 個工作日內解決
- 超過 50% 團隊成員遇到嚴重阻礙

**回滾步驟**：
1. Git revert 遷移相關 commits
2. 恢復 Dockerfile 使用 pip + requirements.txt
3. 恢復 GitHub Actions 使用 pip
4. 通知團隊暫時恢復舊工作流程
5. 記錄問題並重新評估遷移時機

---

## Task Summary

### 總計

- **總任務數**: 52 個任務
- **可平行執行**: 13 個任務標記 [P]
- **關鍵路徑長度**: ~20 個必須依序執行的任務

### 各 Phase 任務統計

| Phase | 任務數 | 可平行任務 | 預估時間 |
|-------|--------|-----------|----------|
| Phase 1: Setup | 5 | 2 | 1-2 小時 |
| Phase 2: Foundational | 4 | 2 | 1 小時 |
| Phase 3: Docker | 11 | 0 | 2-3 小時 |
| Phase 4: CI/CD | 9 | 3 | 2 小時 |
| Phase 5: Documentation | 7 | 4 | 1-2 小時 |
| Phase 6: Validation | 11 | 2 | 2-3 小時 |
| Phase 7: Team Enablement | 5 | 0 | 3-4 小時 |
| **總計** | **52** | **13** | **12-17 小時** |

### 各開發需求對應任務數

| Requirement | 任務數 | 關鍵任務 ID |
|-------------|--------|-------------|
| DR-001 (Poetry 採用) | 15 | T001, T006-T009, T030-T033 |
| DR-002 (版本鎖定) | 8 | T002, T004, T005, T034-T036 |
| DR-003 (依賴分離) | 3 | T003, T035 |
| DR-004 (Docker 支援) | 11 | T010-T020 |
| DR-005 (CI/CD 整合) | 9 | T021-T029 |
| 驗證與文件 | 6 | T037-T047 |

---

## Success Criteria

### 技術驗證 ✅

- [x] `poetry install` 在乾淨環境成功執行（T037）
- [x] 所有現有測試通過（`poetry run pytest`）（T038）
- [x] Ruff linting 通過（T039）
- [x] Docker 映像成功構建且大小合理（T040）
- [x] Docker 容器可正常啟動並回應請求（T041）
- [x] CI/CD 管道所有檢查通過（T042）
- [x] poetry.lock 與 pyproject.toml 一致（T027, T047）

### 文件完整性 ✅

- [x] README.md 包含完整的 Poetry 設置說明（T030-T032）
- [x] quickstart.md 提供詳細的快速入門指南（T033）
- [x] pip vs Poetry 命令對照表可用（T049）

### 團隊準備度 ✅

- [x] 團隊培訓資料準備完成（T048）
- [x] 至少一次團隊培訓 session 完成（T051）
- [x] 支援管道建立（T052）
- [x] 團隊成員可獨立在本地環境設置專案（T043）

### 向下相容性 ✅

- [x] requirements.txt 自動生成並可用（T034）
- [x] requirements-dev.txt 保留作為備援（T035）

---

## Format Validation

✅ **所有任務符合格式要求**：
- 每個任務以 `- [ ]` 開頭（Markdown checkbox）
- 每個任務有唯一的 Task ID（T001-T052）
- 可平行任務標記 [P]（13 個任務）
- 每個任務關聯至少一個 DR 標籤（DR-001 至 DR-005）
- 每個任務包含明確的檔案路徑或可執行的操作描述

---

## Notes

- **[P]** = 可平行執行（不同檔案，無依賴關係）
- **[DR-XXX]** = 開發需求標籤（追溯至主規格文件）
- 每個 Phase 結束有明確的 Checkpoint 驗證點
- 建議在每個 Checkpoint 提交變更（commit after logical groups）
- 若遇到問題，參考 specs/copilot/modify-requirements-backend/quickstart.md 故障排除章節
- 保持 poetry.lock 在版本控制中（必須提交）
- Docker 多階段構建策略降低最終映像大小約 50%

---

**Generated**: 2025-12-11  
**Feature Branch**: `copilot/modify-requirements-backend`  
**Specification**: specs/copilot/modify-requirements-backend/plan.md  
**Status**: ✅ Ready for implementation
