# OpenAPI Snapshot

本目錄用來保存 **後端 OpenAPI 規格的 repo 內快照**，提供給：

- Mobile（或其他前端）在本機/CI/雲端 agent 進行 codegen
- 避免 codegen 依賴 `localhost` 或內網可達性

---

## ⚠️ 重要：開發工作流程

### 當您修改後端 API 時，請務必遵循以下順序：

```bash
# 步驟 1：修改後端程式碼（例如新增或修改 API 端點）
# 在 apps/backend/app/modules/... 修改您的 router

# 步驟 2：生成新的 OpenAPI 規格
make generate-openapi

# 步驟 3：重新生成前端 SDK（在修改前端前必須執行）
cd apps/mobile
npm run sdk:clean
npm run sdk:generate

# 步驟 4：驗證型別
npm run type-check

# 步驟 5：現在可以開始修改前端程式碼，使用新的 SDK

# 步驟 6：提交變更
git add ../../openapi/openapi.json  # 只 commit openapi.json
# generated/ 目錄不要 commit（已在 .gitignore）
git commit -m "feat: Add new API endpoint and regenerate SDK"
```

### 為什麼這個順序很重要？

1. **型別安全**：前端 TypeScript 會自動知道新的 API 端點和型別
2. **避免錯誤**：在修改前端前生成 SDK，避免使用過期的 API 定義
3. **開發效率**：IDE 會提供自動完成和型別檢查

---

## 快照檔案約定

請在本目錄維護一份快照檔（檔名可依團隊偏好統一）：

- 建議：`openapi.json` 或 `backend.openapi.json`

## 更新快照的方法

### 方法 1：使用 Python 腳本從程式碼生成（推薦）✅

**無需啟動後端服務**，直接從 FastAPI 程式碼提取 OpenAPI 規格：

#### 選項 A：使用 Poetry（推薦，自動處理依賴）

```bash
# 在 repo 根目錄（需要先安裝 Poetry）
make generate-openapi

# 或者進入 backend 目錄
cd apps/backend
poetry install  # 首次執行需要安裝依賴
poetry run python scripts/generate_openapi.py
```

**優點**：
- ✅ 不需要啟動 database
- ✅ 不需要啟動 Kong gateway
- ✅ 不需要解決環境變數或網路問題
- ✅ 直接從程式碼提取，保證與實作一致
- ✅ 可在 CI/CD pipeline 中自動化

## 完整工作流程

### 當後端 API 有變更時：

#### 使用 Poetry 方法（本機開發）

```bash
# 1. 更新 OpenAPI snapshot
make generate-openapi
# 或: cd apps/backend && poetry run python scripts/generate_openapi.py

# 2. 重新生成 Mobile SDK
cd apps/mobile
npm run sdk:clean
npm run sdk:generate

# 3. 驗證 TypeScript 型別
npm run type-check

# 4. 提交變更（只提交 openapi.json，不提交 generated/）
git add ../../openapi/openapi.json
git commit -m "chore: Update OpenAPI spec"
```

## 注意：baseURL 規則（避免 /api/v1/api/v1）

後端 OpenAPI 的 endpoint paths 已包含 `/api/v1`（例如 `/api/v1/cards/me`），因此：

- 生成 client 的 `baseUrl` 應使用 **host-only**（例如 `http://localhost:8080`）
- 不要把 `/api/v1` 再放進 `baseUrl`

## 故障排除

### 錯誤：`ModuleNotFoundError: No module named 'fastapi'`

**原因**：Python 環境中沒有安裝 FastAPI 相關依賴

**解決方案（依優先順序）**：

1. **使用 Poetry**：
   ```bash
   cd apps/backend
   poetry install
   poetry run python scripts/generate_openapi.py
   ```

### 在 Windows 上執行

Windows 用戶建議使用 **Docker 方法**，因為：
- 不需要安裝 Poetry 或 Python 虛擬環境
- Docker Desktop 提供完整的環境
- 避免 Windows 路徑和權限問題

## 雲端 agent / CI 的最小驗證清單

1. 確認本目錄的 OpenAPI snapshot 檔案存在且為有效 JSON
2. Mobile 安裝 hey-api（Axios client）與 TanStack Query plugin 相關依賴
3. 以本快照作為 codegen input 產生 SDK（生成輸出不 commit；每次 generate）
4. 執行 `apps/mobile` 的型別檢查與測試

## 自動化（CI/CD）

在 GitHub Actions 或其他 CI 中：

```yaml
# .github/workflows/update-openapi.yml
- name: Generate OpenAPI spec
  run: make generate-openapi

- name: Regenerate Mobile SDK
  run: |
    cd apps/mobile
    npm run sdk:generate
    npm run type-check
```
