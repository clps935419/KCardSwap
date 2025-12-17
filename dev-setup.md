# 本機開發環境設定

## 後端開發設定

本專案使用 **Poetry** 進行依賴管理。

### 1) 安裝 Poetry

**macOS / Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

驗證安裝：
```bash
poetry --version
```

### 2) 進入後端目錄並安裝依賴

```bash
cd apps/backend
poetry install
```

### 3) 啟動開發伺服器

```bash
# 方式 1: 使用 poetry run
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2: 先啟動虛擬環境 shell
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) 執行合約測試

```bash
cd apps/backend
poetry run pytest ../specs/001-kcardswap-complete-spec/tests/contract_tests -q
```

說明：合約測試設計為 Test-First（Red），在後端實作並更新合約 JSON 的 `implemented: true` 後，測試才會通過（Green）。

## 常用 Poetry 命令

| 操作 | 命令 |
|------|------|
| 安裝所有依賴 | `poetry install` |
| 新增生產依賴 | `poetry add package-name` |
| 新增開發依賴 | `poetry add --group dev package-name` |
| 移除依賴 | `poetry remove package-name` |
| 更新依賴 | `poetry update` |
| 查看已安裝套件 | `poetry show` |
| 執行測試 | `poetry run pytest` |
| 執行 linting | `poetry run ruff check .` |

詳細說明請參考：`apps/backend/README.md`

---

## 前端 Mobile 開發設定 (Expo)

本專案的 Mobile App 使用 **Expo SDK 54** 與 TypeScript 開發。

### 1) 環境需求

- **Node.js**: 20.x 或更新版本
- **npm**: 10.x 或更新版本
- **Expo CLI**: 透過 npx 自動安裝
- **iOS 開發** (選用): macOS + Xcode
- **Android 開發** (選用): Android Studio + 模擬器或實體裝置

### 2) 安裝依賴

```bash
cd apps/mobile
npm install --legacy-peer-deps
```

註：使用 `--legacy-peer-deps` 以解決 React 19 的 peer dependency 衝突。

### 3) 環境變數設定

複製環境變數範本並修改：

```bash
cp .env.example .env
```

編輯 `.env` 檔案，設定後端 API 位址：

```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8080/api/v1
EXPO_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### 4) 啟動開發伺服器

```bash
cd apps/mobile

# 啟動 Expo 開發伺服器
npm start

# 或直接在 Android 模擬器執行
npm run android

# 或在 iOS 模擬器執行 (僅限 macOS)
npm run ios

# 或在瀏覽器執行
npm run web
```

### 5) 執行測試

```bash
cd apps/mobile

# 執行所有測試
npm test

# 測試 watch 模式
npm run test:watch

# 產生測試覆蓋率報告
npm run test:coverage
```

### 6) 程式碼品質檢查

```bash
cd apps/mobile

# TypeScript 型別檢查
npm run type-check

# ESLint 檢查
npm run lint

# 自動修正 ESLint 問題
npm run lint:fix

# Prettier 格式化
npm run format
```

## 常用 Mobile 開發命令

| 操作 | 命令 |
|------|------|
| 啟動開發伺服器 | `npm start` |
| Android 開發 | `npm run android` |
| iOS 開發 | `npm run ios` |
| Web 開發 | `npm run web` |
| 執行測試 | `npm test` |
| Lint 檢查 | `npm run lint` |
| 型別檢查 | `npm run type-check` |
| 清除快取 | `npx expo start --clear` |

詳細說明請參考：`apps/mobile/README.md`

---

## 開發流程建議

### 後端 + 前端同步開發

1. **終端機 1**: 啟動後端服務
   ```bash
   cd apps/backend
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **終端機 2**: 啟動 Mobile App
   ```bash
   cd apps/mobile
   npm start
   ```

3. **終端機 3**: 啟動資料庫與 Gateway (使用 Docker Compose)
   ```bash
   docker compose up -d
   ```

### 疑難排解

#### Mobile App 問題

- **Module not found**: 執行 `npm install --legacy-peer-deps`
- **Metro bundler cache**: 執行 `npx expo start -c`
- **TypeScript 錯誤**: 執行 `npm run type-check`
- **iOS 編譯問題**: 在 Xcode 中清除 Derived Data

#### 後端問題

- **依賴問題**: 執行 `poetry install`
- **資料庫連線**: 確認 Docker Compose 服務運行中
- **Migration 問題**: 執行 `alembic upgrade head`
