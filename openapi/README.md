# OpenAPI Snapshot（策略 B）

本目錄用來保存 **後端 OpenAPI 規格的 repo 內快照**，提供給：

- Mobile（或其他前端）在本機/CI/雲端 agent 進行 codegen
- 避免 codegen 依賴 `localhost` 或內網可達性

## 來源端點（參考）

後端啟動後可從以下端點取得 OpenAPI：

- Backend（直連）: http://localhost:8000/api/v1/openapi.json
- Kong Proxy（與 App 路徑一致）: http://localhost:8080/api/v1/openapi.json

> 建議以 Kong Proxy 取得，以更貼近 App 實際走的 gateway 路徑。

## 快照檔案約定

請在本目錄維護一份快照檔（檔名可依團隊偏好統一）：

- 建議：`openapi.json` 或 `backend.openapi.json`

## 更新快照（手動）

### macOS / Linux

```bash
curl -s http://localhost:8080/api/v1/openapi.json > openapi/openapi.json
```

### Windows PowerShell

```powershell
Invoke-WebRequest http://localhost:8080/api/v1/openapi.json -OutFile openapi/openapi.json
```

## 注意：baseURL 規則（避免 /api/v1/api/v1）

後端 OpenAPI 的 endpoint paths 已包含 `/api/v1`（例如 `/api/v1/cards/me`），因此：

- 生成 client 的 `baseUrl` 應使用 **host-only**（例如 `http://localhost:8080`）
- 不要把 `/api/v1` 再放進 `baseUrl`

## 雲端 agent / CI 的最小驗證清單（文件版）

1. 確認本目錄的 OpenAPI snapshot 檔案存在且為有效 JSON
2. Mobile 安裝 hey-api（Axios client）與 TanStack Query plugin 相關依賴
3. 以本快照作為 codegen input 產生 SDK（生成輸出不 commit；每次 generate）
4. 執行 `apps/mobile` 的型別檢查與測試
