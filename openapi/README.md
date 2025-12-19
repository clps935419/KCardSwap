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

#### 選項 A：使用 Poetry（推薦，自動處理依賴）

```bash
# 在 repo 根目錄（需要先安裝 Poetry）
make generate-openapi

# 或者進入 backend 目錄
cd apps/backend
poetry install  # 首次執行需要安裝依賴
poetry run python scripts/generate_openapi.py
```

#### 選項 B：使用 Docker（最簡單，無需本機安裝任何工具）

```bash
# 在 repo 根目錄
# 1. 確保後端容器正在運行
docker compose up -d backend

# 2. 在容器內執行生成腳本
make generate-openapi-docker
```

#### 選項 C：直接使用 Python（需要手動安裝依賴）

```bash
# 進入 backend 目錄
cd apps/backend

# 安裝依賴（使用 pip）
pip install fastapi pydantic sqlalchemy psycopg2-binary python-dotenv dependency-injector

# 執行腳本
python scripts/generate_openapi.py
```

**推薦順序**：
1. **Docker 方法**（最簡單）- 如果您已經在使用 Docker
2. **Poetry 方法**（最佳實踐）- 如果您在本機開發
3. **直接 Python**（最後選擇）- 只在無法使用上述方法時

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

#### 使用 Docker 方法（推薦給 Windows 用戶）

```bash
# 1. 確保後端容器正在運行
docker compose up -d backend

# 2. 生成 OpenAPI snapshot
make generate-openapi-docker

# 3. 重新生成 Mobile SDK
cd apps/mobile
npm run sdk:clean
npm run sdk:generate

# 4. 驗證 TypeScript 型別
npm run type-check

# 5. 提交變更（只提交 openapi.json，不提交 generated/）
git add ../../openapi/openapi.json
git commit -m "chore: Update OpenAPI spec"
```

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

1. **使用 Docker 方法（推薦）**：
   ```bash
   docker compose up -d backend
   make generate-openapi-docker
   ```

2. **使用 Poetry**：
   ```bash
   cd apps/backend
   poetry install
   poetry run python scripts/generate_openapi.py
   ```

3. **使用 pip 手動安裝**：
   ```bash
   cd apps/backend
   pip install fastapi pydantic sqlalchemy psycopg2-binary python-dotenv dependency-injector
   python scripts/generate_openapi.py
   ```

### 錯誤：`docker compose exec backend: container not running`

**解決方案**：先啟動後端容器
```bash
docker compose up -d backend
# 等待幾秒讓容器啟動
docker compose ps  # 確認 backend 容器狀態為 "Up"
make generate-openapi-docker
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
