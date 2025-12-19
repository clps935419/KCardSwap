# OpenAPI Snapshot（策略 B）

本目錄用來保存 **後端 OpenAPI 規格的 repo 內快照**，提供給：

- Mobile（或其他前端）在本機/CI/雲端 agent 進行 codegen
- 避免 codegen 依賴 `localhost` 或內網可達性

## 快照檔案約定

請在本目錄維護一份快照檔（檔名可依團隊偏好統一）：

- 建議：`openapi.json` 或 `backend.openapi.json`

## 更新快照的方法

### 方法 1：使用 Python 腳本從程式碼生成（推薦）✅

**無需啟動後端服務**，直接從 FastAPI 程式碼提取 OpenAPI 規格：

```bash
# 在 repo 根目錄
make generate-openapi

# 或者進入 backend 目錄
cd apps/backend
python scripts/generate_openapi.py

# 使用 Docker（如果本機沒有 Python 環境）
make generate-openapi-docker
```

**優點**：
- ✅ 不需要啟動 database
- ✅ 不需要啟動 Kong gateway
- ✅ 不需要解決環境變數或網路問題
- ✅ 直接從程式碼提取，保證與實作一致
- ✅ 可在 CI/CD pipeline 中自動化

### 方法 2：從運行中的後端取得

如果後端已經在運行，可以直接從端點取得：

#### 來源端點
- Backend（直連）: http://localhost:8000/api/v1/openapi.json
- Kong Proxy（與 App 路徑一致）: http://localhost:8080/api/v1/openapi.json

> 建議以 Kong Proxy 取得，以更貼近 App 實際走的 gateway 路徑。

#### macOS / Linux

```bash
curl -s http://localhost:8080/api/v1/openapi.json > openapi/openapi.json
```

#### Windows PowerShell

```powershell
Invoke-WebRequest http://localhost:8080/api/v1/openapi.json -OutFile openapi/openapi.json
```

## 完整工作流程

### 當後端 API 有變更時：

```bash
# 1. 更新 OpenAPI snapshot（使用方法 1）
make generate-openapi

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
