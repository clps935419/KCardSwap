# KCardSwap Web POC

Posts-first POC 的 Web 客戶端，使用 Next.js App Router 實作。

## 技術棧

- **框架**: Next.js 16+ (App Router)
- **UI 元件**: shadcn/ui
- **表單**: react-hook-form
- **資料抓取**: TanStack Query
- **API SDK**: hey-api (從 `openapi/openapi.json` 生成)
- **驗證**: NextAuth + httpOnly cookie
- **代碼品質**: Biome (linting & formatting)

## 快速開始

### 前置需求

- Node.js 18+
- 後端服務已啟動 (apps/backend)

### 安裝依賴

```bash
cd apps/web
npm install --legacy-peer-deps  # 需要使用 legacy-peer-deps 解決 peer dependency 衝突
```

### 環境變數設定

複製 `.env.example` 到 `.env.local` 並填入必要的環境變數：

```bash
cp .env.example .env.local
```

必要的環境變數：
- `NEXT_PUBLIC_API_URL`: 後端 API 的 URL (例如: `http://localhost:8000`)
- `NEXTAUTH_SECRET`: NextAuth 的密鑰 (可用 `openssl rand -base64 32` 生成)
- `NEXTAUTH_URL`: 前端的 URL (例如: `http://localhost:3000`)
- `GOOGLE_CLIENT_ID`: Google OAuth 客戶端 ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth 客戶端密鑰

### 開發模式

```bash
npm run dev
```

預設會在 http://localhost:3000 啟動。

### 生產建置

```bash
npm run build
npm run start
```

## 專案結構

```
apps/web/
├── src/
│   ├── app/              # Next.js App Router 路由
│   │   ├── (auth)/       # 登入相關頁面
│   │   ├── (app)/        # 已登入的應用頁面
│   │   ├── layout.tsx    # 根 layout
│   │   └── providers.tsx # React providers
│   ├── components/       # 共用元件
│   │   └── ui/          # shadcn/ui 元件
│   ├── features/        # 功能模組
│   │   ├── posts/       # 貼文功能
│   │   ├── gallery/     # 相簿功能
│   │   └── inbox/       # 訊息功能
│   ├── lib/             # 工具函式
│   │   ├── api/         # API 客戶端
│   │   └── query-client.ts # TanStack Query 設定
│   └── shared/          # 共用型別與常數
│       └── api/         # 生成的 API SDK
│           └── generated/
├── public/              # 靜態資源
├── .env.example         # 環境變數範例
└── package.json
```

## API SDK 生成

本專案使用 hey-api 從後端的 OpenAPI 規格生成型別安全的 API SDK。

### 生成 SDK

```bash
npm run sdk:generate
```

這個指令會：
1. 讀取 repo root 的 `openapi/openapi.json`
2. 生成 TypeScript SDK 到 `src/shared/api/generated/`
3. 使用 axios client
4. 包含完整的型別定義

### 何時需要重新生成

當後端 API 有變更時：
1. 後端執行 `python3 scripts/generate_openapi.py` 更新 `openapi/openapi.json`
2. 前端執行 `npm run sdk:generate` 重新生成 SDK

## 開發環境管理員登入

在開發環境下，登入頁面會顯示管理員帳密登入表單。

### 前置條件

1. 創建管理員帳號（在後端執行）：
```bash
cd apps/backend
poetry run python scripts/init_admin.py --email admin@example.com --password SecurePass123
```

2. 確保 `NODE_ENV` 設定為 `development`（預設就是）

### 使用方式

1. 啟動開發伺服器：`npm run dev`
2. 訪問登入頁面：http://localhost:3000/login
3. 會看到琥珀色的「開發模式：管理員登入」區塊
4. 輸入管理員 email 和密碼
5. 點擊「管理員登入」
6. 成功後會儲存 tokens 並重定向到首頁

**注意**：此功能只在開發環境顯示（`NODE_ENV === 'development'`），生產環境不會出現。

## Cookie 與驗證

本專案使用 httpOnly cookie 進行驗證：

- **Access Token**: 短效 (15 分鐘)，存於 httpOnly cookie
- **Refresh Token**: 長效 (7 天)，存於 httpOnly cookie
- **Token 續期**: 前端自動處理 (401 → refresh → retry)

### 同源部署

Web 與 API 需同機同源部署，以確保 cookie 能正確傳遞。

開發時可用反向代理 (如 nginx) 或確保兩個服務在同一網域下。

## 開發注意事項

### 必須遵守的規則

1. **UI 元件**: 使用 shadcn/ui 元件，從 `@/components/ui` 導入
2. **路徑別名**: 使用 `@/` 而非相對路徑
3. **API 呼叫**: 使用生成的 TanStack Query hooks，不手寫 API 呼叫
4. **表單**: 使用 react-hook-form
5. **驗證**: 所有頁面都需要登入 (除了登入頁)

### 代碼檢查與格式化

```bash
# 檢查並修復代碼問題 (lint + format)
npm run check

# 僅檢查 linting
npm run lint

# 僅格式化代碼
npm run format
```

## 測試

(待補充)

## 部署

(待補充)
