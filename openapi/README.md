# OpenAPI Snapshot

本目錄用來保存 **後端 OpenAPI 規格的 repo 內快照**，提供給：

- Mobile / Web（或其他前端）在本機/CI/雲端 agent 進行 codegen
- 避免 codegen 依賴 `localhost` 或內網可達性

⚠️ 注意：`openapi/openapi.json` 是由程式碼生成的開發後產物，可能落後於程式碼（例如你先更新文件/任務，但尚未實作 API、或實作後尚未 regenerate+commit）。
- 文件/需求/任務討論：以 spec/plan/tasks 為準
- SDK/Swagger/測試對齊：以「更新後的 snapshot」為準（未更新時先 regenerate）

---

## ⚠️ 重要：開發工作流程

### 當您修改後端 API 時，請務必遵循以下順序：

```bash
# 步驟 1：修改後端程式碼（例如新增或修改 API 端點）
# 在 apps/backend/app/modules/... 修改您的 router

# 步驟 2：生成新的 OpenAPI 規格
make generate-openapi

# 步驟 3：重新生成前端 SDK（在修改前端前必須執行）

## Mobile
cd apps/mobile
npm run sdk:clean
npm run sdk:generate

## Web
cd ../web
npm run sdk:clean
npm run sdk:generate

# 步驟 4：驗證型別
npm run type-check

# 步驟 5：現在可以開始修改前端程式碼，使用新的 SDK

# 步驟 6：提交變更
git add ../../openapi/openapi.json  # 只 commit openapi.json
# generated/ 目錄不要 commit（應在各 app 的 .gitignore 中排除）
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

# 3. 重新生成 Web SDK
cd ../web
npm run sdk:clean
npm run sdk:generate

# 4. 驗證 TypeScript 型別
npm run type-check

# 5. 提交變更（只提交 openapi.json，不提交 generated/）
git add ../../openapi/openapi.json
git commit -m "chore: Update OpenAPI spec"
```

## 注意：baseURL 規則（避免 /api/v1/api/v1）

後端 OpenAPI 的 endpoint paths 已包含 `/api/v1`（例如 `/api/v1/cards/me`），因此：

- 生成 client 的 `baseUrl` 應使用 **host-only**（例如 `http://localhost:8080`）
- 不要把 `/api/v1` 再放進 `baseUrl`

---

## 驗證方式：httpOnly Cookie（Web + Backend）

本專案的 Web POC 會採用 **httpOnly cookie** 作為主要登入狀態承載方式（不使用 LocalStorage token，也不以 `Authorization: Bearer` 作為主要驗證方式）。

本 POC 採用 cookie-JWT 典型配置：

- `access_token`：短效 JWT（用於一般 API 請求）
- `refresh_token`：長效 JWT（用於換發新的 access）
- `POST /auth/refresh`：讀取 refresh cookie，換發新的 access cookie（常見做法會順便 rotate refresh）

這會影響前端 SDK 的呼叫方式：

- 產生的 SDK client 必須能 **隨請求攜帶 cookie**（同源或跨域 credentials）。
- 若你使用 Axios client（例如 `@hey-api/client-axios`），請確認 client instance 有開啟 `withCredentials: true`（讓瀏覽器會送出 cookie）。

### POC 建議（同機同源）

你目前的部署計畫是 Web 與 API 在同一台機器上，建議以同源/gateway 方式提供 API：

- POC 預設 cookie：`SameSite=Lax`
- 盡量避免跨 origin，以減少 CORS + `SameSite=None` 帶來的複雜度

### 前端請求的 refresh 行為（建議）

典型行為是：

1. API 回覆 `401`（access token 過期）
2. 前端呼叫 `POST /auth/refresh`
3. 後端回新的 `Set-Cookie`（更新 access，必要時也更新 refresh）
4. 前端 retry 原本的 API 請求

### 同源 / 跨域注意事項

若 Web 與 API 位於不同 origin：

- 後端必須允許 credentials（CORS `Access-Control-Allow-Credentials: true`）
- cookie 的 `SameSite`/`Secure` 需要符合瀏覽器規則（常見為 `SameSite=None; Secure`，但本機開發可能需要以 gateway/同源方式運行以降低摩擦）

建議的 POC 做法是讓 Web 透過 gateway 或同源代理呼叫 API，以降低跨域 cookie 的複雜度。

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
2. Mobile/Web 安裝 hey-api（Axios client）與 TanStack Query plugin 相關依賴
3. 以本快照作為 codegen input 產生 SDK（生成輸出不 commit；每次 generate）
4. 執行 `apps/mobile` / `apps/web` 的型別檢查與測試

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

- name: Regenerate Web SDK
  run: |
    cd apps/web
    npm run sdk:generate
    npm run type-check
```
