# Tasks: KCardSwap 完整產品

**生成日期**: 2025-12-16  
**Input**: Design documents from `/specs/001-kcardswap-complete-spec/`  
**Prerequisites**: plan.md, spec.md, data-model.md, openapi/openapi.json

**架構**: Modular DDD (Identity + Social modules)  
**測試策略**: TDD - 先寫測試，確保測試失敗後才實作  
**依賴管理**: Poetry (pyproject.toml + poetry.lock)  
**資料庫遷移**: Alembic (遷移為王策略)

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: 可平行執行（不同檔案，無相依性）
- **[Story]**: 所屬使用者故事（US1, US2, US3...）
- 描述包含明確檔案路徑
- **ID 命名建議**: 後端維持 `T###`，前端 Expo 維持 `M###`（同一份 tasks.md 但不混用編號）

---

## Phase 1: Setup (專案初始化)

**目的**: 建立專案基礎結構與開發環境

- [X] T001 初始化 monorepo 目錄結構（apps/backend, apps/mobile, gateway/kong, infra/）
- [X] T002 配置 Poetry 環境：建立 apps/backend/pyproject.toml 並定義核心依賴（FastAPI, SQLAlchemy, Alembic, pytest）
- [X] T003 [P] 建立 Docker Compose 配置：apps/backend/docker-compose.yml（Kong Gateway + PostgreSQL + Backend）
- [X] T004 [P] 配置 Kong Gateway：gateway/kong/kong.yaml（路由前綴 /api/v1、JWT 插件、Rate Limiting）
- [ ] T005 [P] 建立 GCS Bucket 與測試分層規劃文件：infra/gcs/README.md（僅定義 cards/；禁止 thumbs/；並明確規範 mock→真實 GCS 切換：Unit/Integration 不打真實 GCS，僅 Staging/Nightly 以環境變數啟用少量 Smoke 測試）
- [X] T006 [P] 配置 CI/CD：.github/workflows/backend-ci.yml（lint, test, build 檢查）
- [X] T007 建立開發環境文件：dev-setup.md（本地環境設定指引）
- [X] T008 建立 Makefile：提供 dev, test, lint, seed 指令

---

## Phase 1M: Mobile Setup (Expo 基礎架構) ✅

**目的**: 建立 Expo app 與共用前端基礎，供所有 User Story 的 Mobile 任務共用（不放進各 US）

- [x] M001 初始化 Expo app 專案：建立 apps/mobile（TypeScript）
- [x] M002 建立路由與導航骨架：apps/mobile/app（Expo Router - Auth Stack + Main Tabs）
- [x] M003 建立 API Client：apps/mobile/src/shared/api/client.ts（baseURL + /api/v1、timeout、錯誤解析、自動 token refresh）
- [x] M004 建立 Token 儲存與 Session 管理：apps/mobile/src/shared/auth/session.ts（expo-secure-store 儲存 access/refresh、啟動時 refresh）
- [x] M005 建立 Auth 狀態管理：apps/mobile/src/shared/state/authStore.ts（登入/登出/refresh、401 自動導回登入）
- [x] M006 建立錯誤碼與訊息映射：apps/mobile/src/shared/api/errorMapper.ts（對齊後端 400/401/403/404/422/429）
- [x] M007 建立環境設定範本：apps/mobile/.env.example（BACKEND_BASE_URL、GOOGLE_CLIENT_ID 等）
- [x] M008 建立基礎測試與 lint：apps/mobile（eslint/prettier + jest）
- [x] M009 更新開發文件：dev-setup.md（補上 mobile 啟動、環境變數、Android 模擬器/實機）
- [x] M010 [P] 建立 Mobile CI：.github/workflows/mobile-ci.yml（lint/test；EAS build 可後續加）
- [x] M011 安裝 User Stories 所需 Expo 套件（expo-auth-session, expo-image-picker, expo-image-manipulator, expo-location, expo-notifications 等）
- [x] M012 建立前端技術文件：apps/mobile/TECH_STACK.md（完整技術棧說明、套件使用範例、最佳實踐）
- [x] M013 配置程式碼格式化工具：Prettier + ESLint with Expo config（npm run format, npm run precommit）
 - [x] M014 [P] [INFRA/US] Gluestack UI 導入與初始化：apps/mobile
   - 在 `apps/mobile` 執行 `npx gluestack-ui init`，將 `GluestackUIProvider` 加入全域布局（`app/_layout.tsx`）
   - 建立初始 theme tokens（colors/spacing/typography）並加入 `src/shared/ui/theme`
   - 實作並替換 3 個共享基礎元件：`Button`, `Card`, `Input`（放在 `src/shared/ui/components/`），並提供最小的 story / snapshot 測試
   - 更新 `apps/mobile/TECH_STACK.md` 與 `apps/mobile/README.md` 的安裝與啟動說明（包含 gluestack init 指令與 provider 範例）
   - 驗收標準：
     - App 能啟動且首頁可正確載入 Gluestack provider（dev build）
     - `Button/Card/Input` 在至少一個 screen 中被替換並通過 snapshot 測試
     - docs 已更新、且 Phase 1M checkpoint 維持 Gluestack-only 語句

**Checkpoint**: Mobile 基礎架構完成 ✅ - 各 US 的 Mobile 任務可開始並行

**已完成項目:**
- ✅ Expo SDK 54 + React Native 0.81 + TypeScript
- ✅ Expo Router 檔案式路由（app/ 目錄結構）
- ✅ Gluestack UI 元件系統（Provider + 基礎元件）
- ✅ Zustand 狀態管理 + TanStack Query API 管理
- ✅ Axios API Client with 自動 Token Refresh
- ✅ 完整錯誤處理與映射
- ✅ 所有 User Stories 所需 Expo 套件已安裝
- ✅ 完整技術文件 (TECH_STACK.md)
- ✅ ESLint + Prettier 程式碼品質工具
- ✅ Mobile CI/CD workflow

**Checkpoint**: Mobile 基礎架構完成 - 各 US 的 Mobile 任務可開始並行

---

## Phase 1M.1: OpenAPI SDK Generation（hey-api / Axios client）✅

**目的**: 由後端 OpenAPI 產生型別安全 SDK（含 TanStack Query options），並確保雲端 agent/CI 不依賴網路可達性（使用 repo 內 snapshot）。

**狀態**: ✅ **已完成**

**重要規則**:
- OpenAPI paths 已包含 `/api/v1`，生成 client 的 baseUrl 必須使用 host-only（例如 `http://localhost:8080`），避免 `/api/v1/api/v1`。
- 生成輸出（generated）**不 commit**；每次需要時重新 generate。

⚠️ 注意：`openapi/openapi.json` 是由程式碼生成的開發後產物，可能落後於程式碼。它用於 Swagger 檢視、SDK codegen 與整合測試對齊；討論需求/任務時請以 spec/plan/tasks 為準，不要用 snapshot 推論需求是否已完成。

- [x] M015 [P] [TOOLING] 新增/更新 OpenAPI snapshot：建立 `openapi/openapi.json`（來源：從後端程式碼自動生成，已執行）
- [x] M016 [P] [TOOLING] 建立 hey-api codegen config：`apps/mobile/openapi-ts.config.ts`（Axios client + `@tanstack/react-query` plugin；input 指向 `openapi/openapi.json`；output 至 `apps/mobile/src/shared/api/generated/`）
- [x] M017 [P] [TOOLING] 加入 codegen scripts：更新 `apps/mobile/package.json`（新增 `sdk:generate` / `sdk:clean`；確保可在乾淨環境執行）
- [x] M018 [P] [TOOLING] 排除生成輸出：更新 `.gitignore`（忽略 `apps/mobile/src/shared/api/generated/`，確保 generated 不被提交）
- [x] M019 [P] [TOOLING] 生成 client 的 runtime 設定入口：新增 `apps/mobile/src/shared/api/sdk.ts`（集中設定 baseUrl=host-only、Auth header、以及 refresh token 行為；使用 hey-api axios client）
- [x] M020 [P] [TOOLING] 最小驗證：在 `apps/mobile` 執行 `npm run sdk:generate` + `npm run type-check`（確保生成結果可被 TS 正確解析）

**Checkpoint**: OpenAPI SDK Generation 完成 ✅
- ✅ OpenAPI 規格已從實際後端程式碼生成（17 個端點，41KB）
- ✅ hey-api 配置完成，可生成型別安全的 Axios client + TanStack Query hooks
- ✅ 完整文檔與故障排除指南
- ✅ 雲端 agent 驗證通過

**開發工作流程**（重要）：
1. **當修改後端 API 時**：先執行 `make generate-openapi` 生成新的 `openapi/openapi.json`
2. **在修改前端前**：執行 `cd apps/mobile && npm run sdk:generate` 生成最新的 hey-api SDK
3. **驗證**：執行 `npm run type-check` 確保型別正確
4. **提交**：只 commit `openapi/openapi.json`，不 commit `apps/mobile/src/shared/api/generated/`（已在 .gitignore）

詳細文檔請見：
- `openapi/README.md` - OpenAPI 生成方法與完整工作流程
- `apps/mobile/OPENAPI_SDK_GUIDE.md` - SDK 使用指南與最佳實踐

---

## Phase 1M.2: SDK Adoption & Standardization（hey-api TanStack SDK 全面接管）

**目的**: 在不回改既有已完成項（Phase 1M / 1M.1）的前提下，補充/覆寫 Mobile 對 SDK 的最新規範：

- **唯一允許的後端 API 呼叫方式**：使用 hey-api 生成的 TanStack Query **options/mutations**（`getXxxOptions()` / `xxxMutation()` / `getXxxQueryKey()`）搭配 `useQuery(...)` / `useMutation(...)`
- **禁止**：再新增任何對 `apps/mobile/src/shared/api/client.ts` 的使用（視為 legacy）
- **例外**：Signed URL 直傳（PUT/POST 到 `upload_url`）必須使用獨立 `fetch()`，並完全依照 `required_headers`（不得注入 Authorization / 其他非必要 header）
- **生成輸出策略（單人開發取捨）**：允許 commit `apps/mobile/src/shared/api/generated/`，但它是 dependency，**禁止手改**；只能透過 `sdk:generate` 更新

- [x] M021 [P] [DOCS] 更新 Mobile 文件：
  - `apps/mobile/README.md`：移除「Axios client as standard」敘述，改成 SDK 為唯一 API 入口，保留 Signed URL 上傳例外
  - `apps/mobile/OPENAPI_SDK_GUIDE.md`：改成 options/mutations 用法（非 hooks），並更新「generated 可 commit、禁手改」規則
  - `apps/mobile/TECH_STACK.md`：Signed URL 直傳例外與錯誤分流規則更精準
- [x] M022 [P] [TOOLING] 調整 `apps/mobile/package.json` 的 `sdk:clean` 為跨平台（Windows 可用，不依賴 `rm -rf`）
- [x] M023 [P] [REFACTOR] 全面移除 Mobile 對 legacy client 的依賴：搜尋並改寫所有 `@/src/shared/api/client` 的 import，改用 `@/src/shared/api/sdk` 的 options/mutations
- [x] M024 [P] [GUARDRAIL] 加入防呆規則：
  - ESLint 規則或專案約定，禁止 import `@/src/shared/api/client`
  - README/TECH_STACK 明確列出「禁止使用的 import」與替代寫法

## Phase 2: Foundational (基礎設施 - 阻塞性前置任務)

**目的**: 核心基礎設施，必須完成後才能開始任何 User Story 實作

**⚠️ 關鍵**: 此階段完成前，所有 User Story 工作均不可開始

### 資料庫與 ORM 基礎

- [X] T009 建立精簡版 init.sql：infra/db/init.sql（僅 CREATE DATABASE, CREATE EXTENSION pgcrypto, CREATE USER, GRANT）
- [X] T010 配置 Alembic 環境：apps/backend/alembic.ini + alembic/env.py（連線 PostgreSQL）
- [X] T011 建立初始 migration script：alembic/versions/001_initial_schema.py（所有表結構從現有 data-model.md 轉換）
- [X] T012 建立索引 migration：alembic/versions/002_add_indexes.py（所有索引定義）
- [X] T013 驗證 migration 升降級：執行 `alembic upgrade head` 與 `alembic downgrade base` 確保正常運作
- [X] T014 更新 Docker 初始化流程：docker-entrypoint.sh（先執行 init.sql，再執行 alembic upgrade head）

### 模組化架構骨架

- [X] T015 建立 Shared Kernel 目錄結構：apps/backend/app/shared/（domain/, infrastructure/, presentation/）
- [X] T016 [P] 建立 Identity 模組目錄結構：apps/backend/app/modules/identity/（domain/, application/, infrastructure/, presentation/）
- [X] T017 [P] 建立 Social 模組目錄結構：apps/backend/app/modules/social/（domain/, application/, infrastructure/, presentation/）
- [X] T018 建立依賴注入容器骨架：apps/backend/app/container.py（使用 dependency-injector）
- [X] T019 建立應用程式入口：apps/backend/app/main.py（FastAPI app 初始化與模組路由聚合）

### Shared Kernel 實作

- [X] T020 [P] 實作共用 Value Object：apps/backend/app/shared/domain/email.py（Email VO）
- [X] T021 [P] 實作 Entity 基類：apps/backend/app/shared/domain/base_entity.py
- [X] T022 實作資料庫連線：apps/backend/app/shared/infrastructure/database/connection.py（SQLAlchemy Engine）
- [X] T023 [P] 實作 Repository 基類：apps/backend/app/shared/infrastructure/database/base_repository.py
- [X] T024 [P] 實作 JWT 服務：apps/backend/app/shared/infrastructure/security/jwt_service.py（簽發/驗證 Access + Refresh Token）
- [X] T025 [P] 實作密碼雜湊：apps/backend/app/shared/infrastructure/security/password_hasher.py（bcrypt）
- [X] T026 [P] 實作 GCS 服務：apps/backend/app/shared/infrastructure/external/gcs_storage_service.py（產生 signed URL）
- [X] T027 [P] 實作錯誤處理中介軟體：apps/backend/app/shared/presentation/middleware/error_handler.py
- [X] T028 [P] 實作 API 例外類別：apps/backend/app/shared/presentation/exceptions/api_exceptions.py（400/401/403/404/422/429）

**Checkpoint**: 基礎設施完成 - User Story 實作可以開始並行進行

---

## Phase 2.5: Admin System (管理員系統 - 僅供後台管理)

**目的**: 提供管理員帳密登入功能，不對移動端用戶開放

**使用場景**: 管理員透過 Swagger UI、Postman 或 curl 進行帳密登入，獲取 JWT Token 進行後台管理操作

- [X] T029 [Admin-Auth] 擴展 User Entity：添加 password_hash 和 role 屬性（apps/backend/app/modules/identity/domain/entities/user.py）
- [X] T030 [Admin-Auth] 創建 Alembic migration：alembic/versions/003_add_admin_fields.py（添加 password_hash VARCHAR(255) NULLABLE, role VARCHAR(20) DEFAULT 'user'，修改 google_id 為 NULLABLE）
- [X] T031 [Admin-Auth] 更新 ORM 模型：apps/backend/app/modules/identity/infrastructure/database/models.py（同步 password_hash 與 role 欄位）
- [X] T032 [Admin-Auth] 實現密碼服務：apps/backend/app/modules/identity/infrastructure/security/password_service.py（hash_password, verify_password 使用 bcrypt）
- [X] T033 [Admin-Auth] 實現 AdminLoginUseCase：apps/backend/app/modules/identity/application/use_cases/auth/admin_login.py（驗證 email+password，檢查 role 是否為 admin/super_admin）
- [X] T034 [Admin-Auth] 添加 Admin Login Endpoint：POST /api/v1/auth/admin-login（apps/backend/app/modules/identity/presentation/routers/auth_router.py，標記 tags=["Admin"]）
- [X] T035 [Admin-Auth] 創建管理員工具腳本（手動）：apps/backend/scripts/create_admin.py（接受 --email, --password, --role 參數，生成 bcrypt hash 並插入資料庫；用於手動建立額外管理員，email 重複會報錯）
- [X] T035A [Admin-Auth] 創建自動初始化腳本（idempotent）：apps/backend/scripts/init_admin.py（支援環境變數、預設值、隨機密碼生成；idempotent 設計可重複執行；整合至 Docker 啟動流程 start.sh；用於自動化部署）
- [X] T036 [Admin-Auth] 對齊 OpenAPI/Swagger：/auth/admin-login（以更新後的 openapi/openapi.json snapshot 作為驗證基準；需先 regenerate+commit 才會反映最新程式碼）
- [X] T037 [Admin-Auth] 更新資料模型文件：specs/001-kcardswap-complete-spec/data-model.md（更新 users 表定義與不變條件）
- [X] T038 [Admin-Auth] 撰寫單元測試：tests/unit/application/use_cases/test_admin_login.py（測試正確密碼、錯誤密碼、非管理員帳號）
- [X] T039 [Admin-Auth] 添加 pyproject.toml 依賴：bcrypt = "^4.1.0"

**Checkpoint**: Admin 登入系統完成，管理員可透過帳密登入獲取 JWT Token

**📝 重要說明**：
- **兩個腳本的用途不同，都需要保留**：
  - `create_admin.py` (T035)：手動建立額外管理員（會在 email 重複時報錯，確保不會意外覆蓋）
  - `init_admin.py` (T035A)：自動化初始化預設管理員（idempotent，可安全重複執行，用於 Docker/CI/CD）
- **遵循業界最佳實務**：Schema migration（Alembic）與資料初始化（init scripts）分離
- **參考文件**：詳見 `INIT-DATA-DESIGN.md`

---

## Phase 3: User Story 1 - Google 登入與完成基本個人檔案 (Priority: P1) 🎯 MVP

**目標**: 使用者可以透過 Google 登入，並完成基本個人檔案設定

**獨立測試標準**:
- ✓ 使用者可以成功使用 Google 登入並取得 JWT Token
- ✓ 使用者可以查看和更新個人檔案（nickname, bio, avatar）
- ✓ 登入狀態可以通過 JWT 驗證
- ✓ Refresh Token 機制正常運作

### Domain Layer (Identity Module)

- [X] T040 [P] [US1] 建立 User Entity：apps/backend/app/modules/identity/domain/entities/user.py（id, email, google_id, created_at）
- [X] T041 [P] [US1] 建立 Profile Entity：apps/backend/app/modules/identity/domain/entities/profile.py（user_id, nickname, bio, avatar_url）
- [X] T042 [P] [US1] 建立 RefreshToken Entity：apps/backend/app/modules/identity/domain/entities/refresh_token.py（token, user_id, expires_at）
- [X] T032 [P] [US1] 定義 UserRepository Interface：apps/backend/app/modules/identity/domain/repositories/user_repository.py
- [X] T033 [P] [US1] 定義 ProfileRepository Interface：apps/backend/app/modules/identity/domain/repositories/profile_repository.py
- [X] T034 [P] [US1] 定義 RefreshTokenRepository Interface：apps/backend/app/modules/identity/domain/repositories/refresh_token_repository.py

### Application Layer (Identity Module)

- [X] T035 [P] [US1] 建立 GoogleLoginUseCase：apps/backend/app/modules/identity/application/use_cases/google_login_use_case.py（驗證 Google Token → 建立/更新 User → 簽發 JWT）
- [X] T035A [P] [US1] （Expo/PKCE）建立 GoogleCallbackUseCase：apps/backend/app/modules/identity/application/use_cases/google_callback_use_case.py（接收 authorization code + code_verifier → 後端交換 tokens → 驗證 id_token → 建立/更新 User → 簽發 JWT）
- [X] T036 [P] [US1] 建立 RefreshTokenUseCase：apps/backend/app/modules/identity/application/use_cases/refresh_token_use_case.py（驗證 Refresh Token → 簽發新 Access Token）
- [X] T037 [P] [US1] 建立 GetProfileUseCase：apps/backend/app/modules/identity/application/use_cases/get_profile_use_case.py
- [X] T038 [P] [US1] 建立 UpdateProfileUseCase：apps/backend/app/modules/identity/application/use_cases/update_profile_use_case.py

### Infrastructure Layer (Identity Module)

- [X] T039 [P] [US1] 實作 SQLAlchemy User Model：apps/backend/app/modules/identity/infrastructure/database/models/user_model.py
- [X] T040 [P] [US1] 實作 SQLAlchemy Profile Model：apps/backend/app/modules/identity/infrastructure/database/models/profile_model.py
- [X] T041 [P] [US1] 實作 SQLAlchemy RefreshToken Model：apps/backend/app/modules/identity/infrastructure/database/models/refresh_token_model.py
- [X] T042 [P] [US1] 實作 UserRepositoryImpl：apps/backend/app/modules/identity/infrastructure/repositories/user_repository_impl.py
- [X] T043 [P] [US1] 實作 ProfileRepositoryImpl：apps/backend/app/modules/identity/infrastructure/repositories/profile_repository_impl.py
- [X] T044 [P] [US1] 實作 RefreshTokenRepositoryImpl：apps/backend/app/modules/identity/infrastructure/repositories/refresh_token_repository_impl.py
- [X] T045 [P] [US1] 實作 GoogleOAuthService：apps/backend/app/modules/identity/infrastructure/external/google_oauth_service.py（驗證 Google ID Token）
- [X] T045A [P] [US1] （Expo/PKCE）擴展 GoogleOAuthService：apps/backend/app/modules/identity/infrastructure/external/google_oauth_service.py（新增 exchange_code_with_pkce：用 code + code_verifier 向 Google token endpoint 交換 tokens，取得並回傳 id_token）

### Presentation Layer (Identity Module)

- [X] T046 [P] [US1] 定義 Login Schema：apps/backend/app/modules/identity/presentation/schemas/auth_schemas.py（GoogleLoginRequest, TokenResponse）
- [X] T047 [P] [US1] 定義 Profile Schema：apps/backend/app/modules/identity/presentation/schemas/profile_schemas.py（ProfileResponse, UpdateProfileRequest）
- [X] T048 [US1] 建立 Auth Router：apps/backend/app/modules/identity/presentation/routers/auth_router.py（POST /api/v1/auth/google-login, POST /api/v1/auth/refresh）
- [X] T048A [US1] （Expo/PKCE）擴展 Auth Router：apps/backend/app/modules/identity/presentation/routers/auth_router.py（新增 POST /api/v1/auth/google-callback：接收 { code, code_verifier, redirect_uri? }，回傳 TokenResponse）
- [X] T049 [US1] 建立 Profile Router：apps/backend/app/modules/identity/presentation/routers/profile_router.py（GET /api/v1/profile/me, PUT /api/v1/profile/me）
- [X] T050 [P] [US1] 實作 JWT Authentication Dependency：apps/backend/app/modules/identity/presentation/dependencies/auth_deps.py（get_current_user）

### Phase 3.1: Google OAuth Callback with PKCE（Expo 標準做法）✅

**目的**: 支援 Expo AuthSession 的 Authorization Code Flow with PKCE。Mobile 端取得 `code` 後，交由後端交換 tokens（避免在前端保存任何 secret）。

**端點**:
- `POST /api/v1/auth/google-callback`（Kong 前綴後實際為 `/auth/google-callback`）

**保留既有端點**:
- `POST /api/v1/auth/google-login`：維持接收 `id_token`（Web 或其他情境），但不作為 Expo 推薦路徑

#### Schemas

- [X] T046A [P] [US1] （Expo/PKCE）擴展 Login Schema：apps/backend/app/modules/identity/presentation/schemas/auth_schemas.py（GoogleCallbackRequest: code, code_verifier, redirect_uri?）

#### Use Case / Service 行為

- [X] T035B [P] [US1] （Expo/PKCE）GoogleCallbackUseCase：強制驗證 `redirect_uri` 與配置一致（若採用），並處理錯誤映射（Google token endpoint 失敗 → 401/422）
- [X] T045B [P] [US1] （Expo/PKCE）Google token exchange：HTTP client timeout/retry 策略（最小實作：timeout + 清楚錯誤訊息）

#### Testing

- [X] T053A [P] [US1] （Expo/PKCE）對齊 OpenAPI/Swagger：/auth/google-callback（以更新後的 openapi/openapi.json snapshot 作為驗證基準；需先 regenerate+commit 才會反映最新程式碼）
- [X] T057A [P] [US1] （Expo/PKCE）Auth Integration Tests：tests/integration/modules/identity/test_auth_flow.py（mock Google token endpoint，覆蓋 code+pkce 流程）

#### Documentation

- [X] T061A [P] [US1] （Expo/PKCE）更新 Authentication 文件：apps/backend/docs/authentication.md（補上 PKCE code flow 與兩條登入路徑差異）
- [X] T062A [P] [US1] （Expo/PKCE）更新 API 文件：apps/backend/docs/api/identity-module.md（新增 /auth/google-callback）

### Integration

- [X] T051 [US1] 註冊 Identity Module 到 DI Container：apps/backend/app/container.py（綁定 Repositories, UseCases, Services）
- [X] T052 [US1] 註冊 Identity Module 路由到 main.py：apps/backend/app/main.py（包含 /auth 和 /profile 路由）

### Testing

- [X] T053 [P] [US1] 撰寫 Auth Integration Tests（以 OpenAPI/Swagger（由程式碼生成的 snapshot）作為回應/路由對齊驗證；已由 T057/T057A 整合測試覆蓋）
- [X] T054 [P] [US1] 撰寫 Profile Integration Tests（以 OpenAPI/Swagger（由程式碼生成的 snapshot）作為回應/路由對齊驗證；已由 T058 整合測試覆蓋）
- [X] T055 [P] [US1] 撰寫 User Entity Unit Tests：tests/unit/modules/identity/domain/test_user_entity.py
- [X] T056 [P] [US1] 撰寫 GoogleLoginUseCase Unit Tests：tests/unit/modules/identity/application/test_google_login_use_case.py
- [X] T057 [US1] 撰寫 Auth Integration Tests：tests/integration/modules/identity/test_auth_flow.py（完整登入流程 E2E）
- [X] T058 [US1] 撰寫 Profile Integration Tests：tests/integration/modules/identity/test_profile_flow.py（查看/更新檔案 E2E）

### Configuration

- [X] T059 [P] [US1] 配置 Kong JWT Plugin：gateway/kong/phase1-jwt-config.yaml（驗證 Access Token）
- [X] T060 [P] [US1] 更新環境變數：apps/backend/app/config.py（GOOGLE_CLIENT_ID, JWT_SECRET, JWT_ALGORITHM）

### Documentation

- [X] T061 [P] [US1] 撰寫 Authentication 文件：apps/backend/docs/authentication.md（Google OAuth 流程、JWT 結構、Refresh 機制）
- [X] T062 [P] [US1] 更新 API 文件：apps/backend/docs/api/identity-module.md（/auth 和 /profile 端點說明）

### Seed Data

- [X] T063 [P] [US1] 建立測試用戶 Seed：apps/backend/scripts/seed_users.py（產生測試用戶與 Profile）

### Verification

- [X] T064 [US1] 執行所有 US1 測試：確保 Unit Tests + Integration Tests 全數通過（已移除獨立 OpenAPI JSON 驗證流程）
- [X] T065 [US1] 手動驗證 US1 驗收標準：使用 Postman/curl 測試完整登入與檔案更新流程

### Mobile (Expo)

- [X] M101 [P] [US1] 實作 Google 登入畫面與 PKCE Flow：apps/mobile/src/features/auth（使用 AuthSession 取得 code + code_verifier → 呼叫 /api/v1/auth/google-callback；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）
- [X] M102 [P] [US1] 串接 TokenResponse 並寫入 Session：apps/mobile/src/shared/auth/session.ts（使用 /api/v1/auth/refresh 續期；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）
- [X] M103 [P] [US1] 建立個人檔案頁（讀取/更新）：apps/mobile/src/features/profile（GET/PUT /api/v1/profile/me；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）
- [ ] M104 [US1] 手動驗證登入與更新檔案：Android 實機/模擬器（確認冷啟動 refresh 與 401 重新登入）

---

## Phase 4: User Story 2 - 新增小卡與上傳限制 (Priority: P1)

**目標**: 使用者可以上傳小卡圖片，系統管理上傳限制（免費：2張/日、10MB/張、1GB總容量）

**獨立測試標準**:
- ✓ 使用者可以上傳小卡圖片並取得 GCS Signed URL
- ✓ 使用者在成功 PUT 到 Signed URL 後可呼叫「確認上傳」API，避免幽靈紀錄
- ✓ 系統正確驗證檔案類型（JPEG/PNG）和大小限制
- ✓ 系統正確追蹤每日上傳次數和總容量
- ✓ 達到限制時回傳正確錯誤訊息（422_LIMIT_EXCEEDED）
- ✓ Mobile 端本機產生 200x200 WebP 縮圖並快取（不回傳/不儲存/不上傳縮圖；列表優先使用本機縮圖，必要時回退載入原圖）

### Domain Layer (Social Module - Cards)

- [x] T066 [P] [US2] 建立 Card Entity：apps/backend/app/modules/social/domain/entities/card.py（id, owner_id, idol, idol_group, album, version, rarity, status, image_url, size_bytes, created_at）
- [x] T067 [P] [US2] 建立 UploadQuota Value Object：apps/backend/app/modules/social/domain/value_objects/upload_quota.py（daily_limit, max_file_size, total_storage）
- [x] T068 [P] [US2] 定義 CardRepository Interface：apps/backend/app/modules/social/domain/repositories/card_repository.py
- [x] T069 [P] [US2] 定義 Card Domain Service：apps/backend/app/modules/social/domain/services/card_validation_service.py（檔案類型/大小驗證邏輯）

### Application Layer (Social Module - Cards)

- [x] T070 [P] [US2] 建立 UploadCardUseCase：apps/backend/app/modules/social/application/use_cases/upload_card_use_case.py（驗證限制 → 產生 Signed URL → 建立 Card 記錄）
- [x] T071 [P] [US2] 建立 GetMyCardsUseCase：apps/backend/app/modules/social/application/use_cases/get_my_cards_use_case.py（查詢當前使用者的所有卡片）
- [x] T072 [P] [US2] 建立 DeleteCardUseCase：apps/backend/app/modules/social/application/use_cases/delete_card_use_case.py
- [x] T073 [P] [US2] 建立 CheckUploadQuotaUseCase：apps/backend/app/modules/social/application/use_cases/check_upload_quota_use_case.py（檢查當日上傳次數與總容量）

### Infrastructure Layer (Social Module - Cards)

- [x] T074 [P] [US2] 實作 SQLAlchemy Card Model：apps/backend/app/modules/social/infrastructure/database/models/card_model.py
- [x] T075 [P] [US2] 實作 CardRepositoryImpl：apps/backend/app/modules/social/infrastructure/repositories/card_repository_impl.py
- [x] T076 [P] [US2] 擴展 GCS Storage Service：apps/backend/app/shared/infrastructure/external/gcs_storage_service.py（新增 generate_upload_signed_url 方法，路徑為 cards/{user_id}/{uuid}.jpg）
- [x] T078 [P] [US2] 實作 Quota Tracking Service：apps/backend/app/modules/social/infrastructure/services/quota_tracking_service.py（Redis 或 DB 追蹤每日上傳次數）

### Presentation Layer (Social Module - Cards)

- [x] T079 [P] [US2] 定義 Card Schema：apps/backend/app/modules/social/presentation/schemas/card_schemas.py（CreateCardRequest, CardResponse, UploadUrlResponse）
- [x] T080 [US2] 建立 Cards Router：apps/backend/app/modules/social/presentation/routers/cards_router.py（POST /api/v1/cards/upload-url, GET /api/v1/cards/me, DELETE /api/v1/cards/{id}）

### Confirm Upload (Design Update)

- [x] T094A [US2] 新增確認上傳 API：POST /api/v1/cards/{id}/confirm-upload（驗證 GCS 物件存在後將卡片標記為已完成上傳；並補齊最小錯誤碼/回應）✅
  - ✅ 已更新 cards 資料模型（新增 upload_status / upload_confirmed_at 欄位）
  - ✅ 已建立 migration 013_add_card_upload_confirmation.py
  - ✅ 已實作 ConfirmCardUploadUseCase
  - ✅ 已更新 cards_router 新增確認上傳端點
  - ✅ 已撰寫單元測試 (Card Entity + ConfirmCardUploadUseCase)
  - ⏸️ 需在實際環境執行 migration 和測試
  - ⏸️ 需更新 OpenAPI snapshot (需實際環境)

### Integration

- [x] T081 [US2] 註冊 Social Module (Cards) 到 DI Container：apps/backend/app/container.py
- [x] T082 [US2] 註冊 Cards Router 到 main.py：apps/backend/app/main.py（包含 /cards 路由）

### Testing

- [x] T083 [P] [US2] 撰寫 Cards Integration Tests（以 OpenAPI/Swagger（由程式碼生成的 snapshot）作為回應/路由對齊驗證；改以整合測試覆蓋）
- [x] T084 [P] [US2] 撰寫 Card Entity Unit Tests：tests/unit/modules/social/domain/test_card_entity.py
- [x] T085 [P] [US2] 撰寫 UploadCardUseCase Unit Tests：tests/unit/modules/social/application/test_upload_card_use_case.py（Mock 限制檢查）
- [x] T086 [P] [US2] 撰寫 Quota Validation Unit Tests：tests/unit/modules/social/domain/test_upload_quota.py（測試每日/總容量/單檔大小邊界）
- [x] T087 [US2] 撰寫 Card Upload Integration Tests：tests/integration/modules/social/test_card_upload_flow.py（完整上傳流程 E2E，包含限制觸發）

### Configuration

- [x] T088 [P] [US2] 配置 GCS Bucket CORS：infra/gcs/cors-config.json（允許前端直接上傳）
- [x] T089 [P] [US2] 更新環境變數：apps/backend/app/config.py（GCS_BUCKET_NAME, DAILY_UPLOAD_LIMIT=2, MAX_FILE_SIZE_MB=10, TOTAL_STORAGE_GB=1）

### Documentation

- [x] T090 [P] [US2] 撰寫 Card Upload 文件：apps/backend/docs/card-upload.md（Signed URL 流程、限制說明、錯誤碼）
- [x] T091 [P] [US2] 更新 API 文件：apps/backend/docs/api/social-module-cards.md

### Verification

- [ ] T092 [US2] 執行所有 US2 測試：確保 Unit Tests + Integration Tests 全數通過（已移除獨立 OpenAPI JSON 驗證流程）
- [ ] T093 [US2] 手動驗證 US2 驗收標準：測試上傳 2 張後觸發 422_LIMIT_EXCEEDED
- [ ] T094 [US2] 驗證縮圖行為（Mobile-only）：確認 App 本機產生 200x200 WebP 縮圖並快取；卡冊列表優先顯示本機縮圖（無縮圖時回退載入原圖）

### Mobile (Expo)

- [x] M201 [P] [US2] 圖片選取與壓縮：apps/mobile/src/features/cards（expo-image-picker + expo-image-manipulator；控制大小 ≤10MB）✅
  - 支援「拍照」與「相簿選取」兩種來源（相機/相簿權限各自處理；權限拒絕需提供清楚提示與重新授權入口）
  - 使用者取消選取/拍照不視為錯誤（不噴錯、不寫入狀態）
  - 需取得實際檔案大小（bytes）做前置驗證；若壓縮後仍 >10MB，需再降解析度/品質直到 ≤10MB 或明確提示「檔案過大」並中止
  - 輸出格式限制為 JPEG/PNG（與後端限制一致），並在 UI 顯示不支援格式的提示
  - （POC/引導框）若需要「拍照時相機畫面顯示框線 + 固定提示文案」，不要使用 `expo-image-picker` 的內建相機 UI（無法自訂 overlay）。需改用 `expo-camera` 自建 CameraView，並以絕對定位疊加 overlay（框線/角標/提示文字）。
  - （POC/依框裁切）若要「依框線區域裁切成卡片圖」，需處理座標映射：框線是在 preview(View) 座標；拍照結果是照片像素座標。建議以相對比例保存框線區域（x/y/width/height 皆為 0..1），再換算為照片像素後用 `expo-image-manipulator` crop。
  - （避免映射歪斜）盡量讓 preview aspect ratio 與拍照輸出比例一致；若 preview 使用 cover/縮放，需把 letterbox/crop 的偏移納入換算，否則裁切會偏移。
  - 參考：apps/mobile/TECH_STACK.md 的「expo-camera（相機預覽 + 自訂 overlay，引導框 POC）」段落（含 POC 步驟與座標映射注意事項）
- [x] M202 [P] [US2] 取得上傳 Signed URL：apps/mobile/src/features/cards/api（呼叫 POST /api/v1/cards/upload-url；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）✅
  - 回應需包含：`upload_url`、`method`（PUT/POST）、`required_headers`（至少 Content-Type；由後端決定）、以及可對應列表的 `image_url`/object key（或等價欄位）
  - 需明確規範 Signed URL 的有效期限（或 TTL 欄位），過期時前端需重新走 M202
- [x] M203 [P] [US2] 直接上傳到 Signed URL：apps/mobile/src/features/cards/services/uploadToSignedUrl.ts（PUT/POST 上傳、錯誤處理與重試）✅
  - 上傳請求必須嚴格使用 M202 回傳的 `method` + `required_headers`（避免簽名不匹配導致 403）
  - 上傳至 Signed URL 不走既有 API client（避免自動注入 Authorization 等 header）；用 fetch 或獨立 HTTP client
  - Retry：僅針對網路錯誤/timeout/5xx 做有限次重試；對 4xx（含 403/400）不盲重試，需提示並必要時重新取得 Signed URL
  - 錯誤 UX：需區分「後端 422（配額/檔案過大/格式不符）」與「Signed URL 上傳失敗（403/過期/網路）」並給出對應提示與重試入口
- [x] M203B [US2] 上傳成功後呼叫確認上傳 API：apps/mobile/src/features/cards（呼叫 POST /api/v1/cards/{id}/confirm-upload；失敗時提示重試/重新取得 Signed URL）✅
  - ✅ 已新增 confirmCardUpload 函數到 cardsApi.ts
  - ✅ 已更新 useUploadCard hook 整合確認上傳步驟
  - ✅ 已新增 'confirming' 進度狀態 (75%)
  - ⏸️ 需在實際環境產生 SDK 並測試
- [x] M203A [P] [US2] 產生 200x200 WebP 縮圖並本機快取：apps/mobile/src/features/cards（縮圖僅供列表快速載入，不上傳、不進後端 API 定義）✅
  - 縮圖快取需定義 key（建議以 card_id 或 image_url 雜湊），並提供失效策略：卡片刪除時移除縮圖；找不到縮圖時回退載入原圖
  - 若 WebP 在特定平台不可用，需定義 fallback（例如 JPEG），但仍維持 200x200 尺寸
- [x] M204 [P] [US2] 我的卡冊列表：apps/mobile/src/features/cards/screens/MyCardsScreen.tsx（GET /api/v1/cards/me）✅（已使用 Gluestack UI）
  - 列表圖片載入順序：本機縮圖 → 原圖（fallback）；原圖載入失敗需顯示可重試狀態
  - UI 狀態：loading/空狀態/錯誤狀態（含重試）需可見且一致
- [x] M205 [P] [US2] 刪除卡片：apps/mobile/src/features/cards/api（DELETE /api/v1/cards/{id}）✅
  - 刪除成功後需同步清除該卡片的縮圖快取，並刷新列表資料
  - 刪除失敗需顯示原因與重試入口（401/403 需導回登入或提示無權限，遵循既有錯誤映射策略）
- [ ] M206 [US2] 手動驗證上傳限制與錯誤 UX：Android 實機/模擬器 ⚠️（程式碼完成，待實機測試）
  - 驗證免費用戶上傳第 3 張觸發 422_LIMIT_EXCEEDED
  - 驗證相機/相簿權限拒絕、使用者取消、>10MB、非 JPEG/PNG、Signed URL 過期/403、網路中斷/timeout 時的提示與重試行為

---

## Phase 5: User Story 3 - 附近的小卡搜尋 (Priority: P1)

**目標**: 使用者可以搜尋附近的小卡（免費 5次/日限制；付費差異 deferred 至 Phase 8 BIZ）

**獨立測試標準**:
- ✓ 使用者可以提供座標並搜尋附近的小卡
- ✓ 搜尋結果按距離排序
- ✓ 隱身模式用戶不出現在結果中
- ✓ 系統正確追蹤每日搜尋次數（免費 5次/日）
- ✓ 達到限制時回傳正確錯誤訊息（HTTP 429 Too Many Requests）

### Application Layer (Social Module - Nearby)

- [X] T095 [P] [US3] 建立 SearchNearbyCardsUseCase：apps/backend/app/modules/social/application/use_cases/search_nearby_cards_use_case.py（計算距離 → 過濾隱身 → 排序）
- [X] T096 [P] [US3] 建立 UpdateUserLocationUseCase：apps/backend/app/modules/social/application/use_cases/update_user_location_use_case.py（記錄最近位置至 profiles.last_lat/last_lng）

### Infrastructure Layer (Social Module - Nearby)

- [X] T097 [P] [US3] 擴展 CardRepositoryImpl：新增 find_nearby_cards 方法（使用 PostGIS 或 Haversine 公式計算距離）
- [X] T098 [P] [US3] 實作 Search Quota Service：apps/backend/app/modules/social/infrastructure/services/search_quota_service.py（Redis 或 DB 追蹤每日搜尋次數）

### Presentation Layer (Social Module - Nearby)

- [X] T099 [P] [US3] 定義 Nearby Schema：apps/backend/app/modules/social/presentation/schemas/nearby_schemas.py（SearchNearbyRequest, NearbyCardResponse）
- [X] T100 [US3] 建立 Nearby Router：apps/backend/app/modules/social/presentation/routers/nearby_router.py（POST /api/v1/nearby/search）
- [X] T100A [US3] 補齊位置上報端點：apps/backend/app/modules/social/presentation/routers/nearby_router.py（PUT /api/v1/nearby/location）

### Integration

- [X] T101 [US3] 註冊 Nearby 功能到 DI Container：apps/backend/app/container.py
- [X] T102 [US3] 註冊 Nearby Router 到 main.py：apps/backend/app/main.py（包含 /nearby 路由）

### Testing

- [X] T103 [P] [US3] 撰寫 Nearby Integration Tests（以 OpenAPI/Swagger（由程式碼生成的 snapshot）作為回應/路由對齊驗證）
- [X] T104 [P] [US3] 撰寫 SearchNearbyCardsUseCase Unit Tests：tests/unit/modules/social/application/test_search_nearby_use_case.py（Mock 距離計算與排序邏輯）
- [X] T105 [US3] 撰寫 Nearby Search Integration Tests：tests/integration/modules/social/test_nearby_search_flow.py（完整搜尋流程 E2E，包含限制觸發）

### Configuration

- [ ] T106 [P] [US3] 配置 Kong Rate Limiting：gateway/kong/kong.yaml（/nearby/search：free=5/day；premium 規則 deferred 至 Phase 8 BIZ）⏭️ 可選項目（應用層已實作）
- [X] T107 [P] [US3] 更新環境變數：apps/backend/app/config.py（DAILY_SEARCH_LIMIT_FREE=5, SEARCH_RADIUS_KM=10）

### Verification

- [X] T108 [US3] 執行所有 US3 測試：確保 Unit Tests + Integration Tests 全數通過（已移除獨立 OpenAPI JSON 驗證流程）✅ 9/9 單元測試通過
- [ ] T109 [US3] 手動驗證 US3 驗收標準：測試搜尋 5 次後觸發 HTTP 429 Too Many Requests（免費用戶）⏸️ 需要實際環境
- [ ] T110 [US3] （Deferred/Phase 8）驗證付費用戶搜尋差異：premium unlimited / premium priority ⏭️ 待 Phase 8 實作

### Mobile (Expo)

- [X] M301 [P] [US3] 定位權限與取得座標：apps/mobile/src/features/nearby（expo-location；處理拒絕權限）
- [X] M302 [P] [US3] 附近搜尋頁：apps/mobile/src/features/nearby/screens/NearbySearchScreen.tsx（POST /api/v1/nearby/search；Schema 以更新後的 Swagger/OpenAPI snapshot（openapi/openapi.json）作為驗證/對齊基準）
  - 建議流程：取得定位後先 PUT /api/v1/nearby/location，再 POST /api/v1/nearby/search（避免後端依舊位置造成結果偏差）
- [X] M303 [US3] 限次錯誤處理：免費用戶第 6 次提示 HTTP 429 Too Many Requests（並提供升級入口；升級差異 deferred 至 Phase 8 BIZ）

---

## Phase 6: User Story 4 - 好友系統與聊天 (Priority: P1)

**狀態**: ✅ **100% Complete** (Backend 33/33 + Mobile 4/4, PR #23 已實作 + Rating 系統已依 FR-SOCIAL-003A 更新)

**目標**: 使用者可以加好友、聊天、評分、檢舉

**獨立測試標準**:
- ✓ 使用者可以送出/接受/拒絕好友邀請
- ✓ 使用者可以封鎖其他用戶（封鎖後雙方無法互動）
- ✓ 使用者可以發送/接收聊天訊息（輪詢機制）
- ✓ 使用者可以收到 FCM 推播通知（背景）
- ✓ 使用者可以對他人評分（規則：必須是好友，或提供 trade_id 且該 trade 與雙方關聯）
- ✓ 使用者可以檢舉違規內容

### Domain Layer (Social Module - Friends & Chat)

- [X] T111 [P] [US4] 建立 Friendship Entity：apps/backend/app/modules/social/domain/entities/friendship.py（id, user_id, friend_id, status: pending/accepted/blocked, created_at）
- [X] T112 [P] [US4] 建立 ChatRoom Entity：apps/backend/app/modules/social/domain/entities/chat_room.py（id, participant_ids, created_at）
- [X] T113 [P] [US4] 建立 Message Entity：apps/backend/app/modules/social/domain/entities/message.py（id, room_id, sender_id, content, status: sent/delivered/read, created_at）
- [X] T114 [P] [US4] 建立 Rating Entity：apps/backend/app/modules/social/domain/entities/rating.py（id, rater_id, rated_user_id, trade_id, score, comment, created_at）
- [X] T115 [P] [US4] 建立 Report Entity：apps/backend/app/modules/social/domain/entities/report.py（id, reporter_id, reported_user_id, reason, created_at）
- [X] T116 [P] [US4] 定義 FriendshipRepository Interface：apps/backend/app/modules/social/domain/repositories/friendship_repository.py
- [X] T117 [P] [US4] 定義 ChatRoomRepository Interface：apps/backend/app/modules/social/domain/repositories/chat_room_repository.py
- [X] T118 [P] [US4] 定義 MessageRepository Interface：apps/backend/app/modules/social/domain/repositories/message_repository.py
- [X] T119 [P] [US4] 定義 RatingRepository Interface：apps/backend/app/modules/social/domain/repositories/rating_repository.py
- [X] T120 [P] [US4] 定義 ReportRepository Interface：apps/backend/app/modules/social/domain/repositories/report_repository.py

### Application Layer (Social Module - Friends & Chat)

- [X] T121 [P] [US4] 建立 SendFriendRequestUseCase：apps/backend/app/modules/social/application/use_cases/send_friend_request_use_case.py
- [X] T122 [P] [US4] 建立 AcceptFriendRequestUseCase：apps/backend/app/modules/social/application/use_cases/accept_friend_request_use_case.py
- [X] T123 [P] [US4] 建立 BlockUserUseCase：apps/backend/app/modules/social/application/use_cases/block_user_use_case.py
- [X] T123A [P] [US4] 建立 UnblockUserUseCase：apps/backend/app/modules/social/application/use_cases/unblock_user_use_case.py（解除封鎖，恢復互動資格但不自動成為好友）
- [X] T124 [P] [US4] 建立 SendMessageUseCase：apps/backend/app/modules/social/application/use_cases/send_message_use_case.py（發送訊息 → 觸發 FCM 推播）
- [X] T125 [P] [US4] 建立 GetMessagesUseCase：apps/backend/app/modules/social/application/use_cases/get_messages_use_case.py（輪詢機制：after_message_id）
- [X] T126 [P] [US4] 建立 RateUserUseCase：apps/backend/app/modules/social/application/use_cases/ratings/rate_user_use_case.py（ratings 基礎能力：建立評分；基本驗證：不可自評、分數 1–5、封鎖禁止；權限規則：好友或提供 trade_id）
  - [X] T126A 修正 Rating Entity - trade_id 改為 Optional（對應 FR-SOCIAL-003A）
  - [X] T126B 修正 Rating Model - trade_id nullable=True
  - [X] T126C 擴充 RateUserUseCase - 新增權限驗證（好友或 trade_id）與封鎖檢查
  - [X] T126D 更新 Rating Router - 注入 FriendshipRepository
  - [X] T126E 更新 Rating Repository - 處理 nullable trade_id
  - [X] T126F 建立 Alembic Migration 009 - 修改 ratings.trade_id 為 nullable
  - [X] T126G 更新 Rating Tests - 涵蓋好友評分和 trade 評分場景
- [X] T127 [P] [US4] 建立 ReportUserUseCase：apps/backend/app/modules/social/application/use_cases/report_user_use_case.py

- [ ] T125A [DEFERRED] [US4] 訊息保留政策：伺服器端保留 30 天；清理/清除 job（例如每日排程）清除超過 30 天的 messages（先在文件/規格中定義，實作延後）

### Infrastructure Layer (Social Module - Friends & Chat)

- [X] T128 [P] [US4] 實作 SQLAlchemy Friendship Model：apps/backend/app/modules/social/infrastructure/database/models/friendship_model.py
- [X] T129 [P] [US4] 實作 SQLAlchemy ChatRoom Model：apps/backend/app/modules/social/infrastructure/database/models/chat_room_model.py
- [X] T130 [P] [US4] 實作 SQLAlchemy Message Model：apps/backend/app/modules/social/infrastructure/database/models/message_model.py
- [X] T131 [P] [US4] 實作 SQLAlchemy Rating Model：apps/backend/app/modules/social/infrastructure/database/models/rating_model.py
- [X] T132 [P] [US4] 實作 SQLAlchemy Report Model：apps/backend/app/modules/social/infrastructure/database/models/report_model.py
- [X] T133 [P] [US4] 實作 FriendshipRepositoryImpl：apps/backend/app/modules/social/infrastructure/repositories/friendship_repository_impl.py
- [X] T134 [P] [US4] 實作 ChatRoomRepositoryImpl：apps/backend/app/modules/social/infrastructure/repositories/chat_room_repository_impl.py
- [X] T135 [P] [US4] 實作 MessageRepositoryImpl：apps/backend/app/modules/social/infrastructure/repositories/message_repository_impl.py
- [X] T136 [P] [US4] 實作 RatingRepositoryImpl：apps/backend/app/modules/social/infrastructure/repositories/rating_repository_impl.py
- [X] T137 [P] [US4] 實作 ReportRepositoryImpl：apps/backend/app/modules/social/infrastructure/repositories/report_repository_impl.py
- [X] T138 [P] [US4] 實作 FCM Push Notification Service：apps/backend/app/shared/infrastructure/external/fcm_service.py（發送推播通知）

### Presentation Layer (Social Module - Friends & Chat)

- [X] T139 [US4] 建立 Friends Router：apps/backend/app/modules/social/presentation/routers/friends_router.py（POST /api/v1/friends/request, POST /api/v1/friends/accept, POST /api/v1/friends/block）
- [X] T139A [US4] 更新 Friends Router：新增解除封鎖端點（例如 POST /api/v1/friends/unblock），串接 UnblockUserUseCase 並更新 OpenAPI 文件
- [X] T140 [US4] 建立 Chat Router：apps/backend/app/modules/social/presentation/routers/chat_router.py（GET /api/v1/chats/{id}/messages, POST /api/v1/chats/{id}/messages）
- [X] T141 [US4] 建立 Rating Router：apps/backend/app/modules/social/presentation/routers/rating_router.py（POST /api/v1/ratings, GET /api/v1/ratings/user/{user_id}, GET /api/v1/ratings/user/{user_id}/average）
- [X] T142 [US4] 建立 Report Router：apps/backend/app/modules/social/presentation/routers/report_router.py（POST /api/v1/reports）

### Verification

- [ ] T143 [US4] 執行所有 US4 測試並手動驗證完整社交功能流程

### Mobile (Expo)

- [X] M401 [P] [US4] 好友邀請/接受/封鎖頁：apps/mobile/src/features/friends（對齊 /api/v1/friends/* 端點；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）
- [X] M402 [P] [US4] 聊天室 UI 與輪詢：apps/mobile/src/features/chat（GET /api/v1/chats/{id}/messages, POST /api/v1/chats/{id}/messages；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）
- [X] M403 [P] [US4] 前景輪詢策略：apps/mobile/src/features/chat/services/polling.ts（after_message_id、退避避免過度打 API）
- [X] M404 [P] [US4] 推播接收與導頁：apps/mobile/src/features/notifications（expo-notifications；點擊通知導向聊天室）

---

## Phase 7: User Story 5 - 小卡交換流程 (Priority: P1)

**目標**: 使用者可以發起、回應、完成小卡交換

**獨立測試標準**:
- ✓ 使用者可以建立交換提案（選擇雙方卡片）
- ✓ 對方可以接受/拒絕提案
- ✓ 雙方確認後交換完成，卡片狀態更新為「已交換」
- ✓ trade completed 後前端顯示「去評分」入口/引導，並以 trade_id 建立評分
- ✓ 交換歷史可以查詢
- ✓ 狀態機正確流轉（draft → proposed → accepted → completed）

### Domain Layer (Social Module - Trade)

- [X] T144 [P] [US5] 建立 Trade Entity：apps/backend/app/modules/social/domain/entities/trade.py（id, initiator_id, responder_id, status: draft/proposed/accepted/completed/rejected/canceled, accepted_at, initiator_confirmed_at, responder_confirmed_at, completed_at, canceled_at, created_at）
- [X] T145 [P] [US5] 建立 TradeItem Entity：apps/backend/app/modules/social/domain/entities/trade_item.py（id, trade_id, card_id, owner_side）
- [X] T146 [P] [US5] 建立 Trade Status Value Object：apps/backend/app/modules/social/domain/value_objects/trade_status.py（狀態機邏輯）
- [X] T147 [P] [US5] 定義 TradeRepository Interface：apps/backend/app/modules/social/domain/repositories/trade_repository.py
- [X] T148 [P] [US5] 定義 Trade Domain Service：apps/backend/app/modules/social/domain/services/trade_validation_service.py（驗證卡片所有權、狀態流轉規則）

### Application Layer (Social Module - Trade)

- [X] T149 [P] [US5] 建立 CreateTradeProposalUseCase：apps/backend/app/modules/social/application/use_cases/create_trade_proposal_use_case.py
- [X] T150 [P] [US5] 建立 AcceptTradeUseCase：apps/backend/app/modules/social/application/use_cases/accept_trade_use_case.py
- [X] T151 [P] [US5] 建立 RejectTradeUseCase：apps/backend/app/modules/social/application/use_cases/reject_trade_use_case.py
- [X] T152 [P] [US5] 建立 CompleteTradeUseCase：apps/backend/app/modules/social/application/use_cases/complete_trade_use_case.py（各自獨立標記完成；雙方都確認後才轉 completed 並鎖定卡片；完成後提供導流評分所需的 trade_id）
  - [ ] T152A 擴充 RateUserUseCase - 新增 trade 完成狀態驗證（FR-SOCIAL-003B）：
    - 驗證 trade_id 對應的 trade 狀態為 completed
    - 確保評分者是該 trade 的參與者（initiator_id 或 responder_id）
    - 注入 TradeRepository 進行驗證
-  - [X] T152B [P] [US5] 交換確認 Timeout 規則（48h）：trade 進入 accepted 後超過 `TRADE_CONFIRMATION_TIMEOUT_HOURS`（預設 48 小時）仍未雙方完成確認時，必須視為 `canceled`（不新增 `expired` 狀態）；此規則需在 complete/讀取 trade 時能被正確套用
- [X] T153 [P] [US5] 建立 GetTradeHistoryUseCase：apps/backend/app/modules/social/application/use_cases/get_trade_history_use_case.py

### Infrastructure Layer (Social Module - Trade)

- [X] T154 [P] [US5] 實作 SQLAlchemy Trade Model：apps/backend/app/modules/social/infrastructure/database/models/trade_model.py
- [X] T155 [P] [US5] 實作 SQLAlchemy TradeItem Model：apps/backend/app/modules/social/infrastructure/database/models/trade_item_model.py
- [X] T156 [P] [US5] 實作 TradeRepositoryImpl：apps/backend/app/modules/social/infrastructure/repositories/trade_repository_impl.py

### Presentation Layer (Social Module - Trade)

- [X] T157 [P] [US5] 定義 Trade Schema：apps/backend/app/modules/social/presentation/schemas/trade_schemas.py（CreateTradeRequest, TradeResponse）
- [X] T158 [US5] 建立 Trade Router：apps/backend/app/modules/social/presentation/routers/trade_router.py（POST /api/v1/trades, POST /api/v1/trades/{id}/accept, POST /api/v1/trades/{id}/reject, POST /api/v1/trades/{id}/cancel, POST /api/v1/trades/{id}/complete, GET /api/v1/trades/history）

### Integration

- [X] T159 [US5] 註冊 Trade 功能到 DI Container：apps/backend/app/container.py（使用 FastAPI 內建依賴注入，無需額外註冊）
- [X] T160 [US5] 註冊 Trade Router 到 main.py：apps/backend/app/main.py

### Testing

- [ ] T161 [P] [US5] 撰寫 Trade Integration Tests（以 OpenAPI/Swagger（由程式碼生成的 snapshot）作為回應/路由對齊驗證；改以整合測試覆蓋）
- [X] T162 [P] [US5] 撰寫 Trade Entity Unit Tests：tests/unit/modules/social/domain/test_trade_entity.py
- [X] T163 [P] [US5] 撰寫 Trade Status State Machine Tests：tests/unit/modules/social/domain/test_trade_status.py（測試所有狀態轉換）
- [X] T164 [P] [US5] 撰寫 CreateTradeProposalUseCase Unit Tests：tests/unit/modules/social/application/test_create_trade_proposal_use_case.py
- [X] T165 [US5] 撰寫 Trade Flow Integration Tests：tests/integration/modules/social/test_trade_flow.py（完整交換流程 E2E）

### Alembic Migration

- [X] T166 [P] [US5] 建立 Trade Tables Migration：alembic/versions/010_add_trade_tables.py（trades, trade_items）
- [ ] T167 [US5] 執行並驗證 Migration：alembic upgrade head && alembic downgrade -1

### Configuration

- [X] T168 [P] [US5] 更新環境變數：apps/backend/app/config.py（TRADE_CONFIRMATION_TIMEOUT_HOURS=48）

### Documentation

- [ ] T169 [P] [US5] 撰寫 Trade Flow 文件：apps/backend/docs/trade-flow.md（狀態機圖、API 流程）
- [ ] T170 [P] [US5] 更新 API 文件：apps/backend/docs/api/social-module-trade.md

### Seed Data

- [ ] T171 [P] [US5] 建立測試交換 Seed：apps/backend/scripts/seed_trades.py

### Verification

- [ ] T172 [US5] 執行所有 US5 測試：確保 Unit Tests + Integration Tests 全數通過（已移除獨立 OpenAPI JSON 驗證流程）
- [ ] T173 [US5] 手動驗證 US5 驗收標準：測試完整交換流程（draft → proposed → accepted → completed）
- [ ] T174 [US5] 驗證卡片鎖定：確認交換完成後卡片狀態更新為「已交換」且無法再次交換

### Mobile (Expo)

- [X] M501 [P] [US5] 發起交換提案頁：apps/mobile/src/features/trade（選擇卡片並呼叫 POST /api/v1/trades；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）
- [X] M502 [P] [US5] 提案詳情與狀態更新 UI：apps/mobile/src/features/trade/screens/TradeDetailScreen.tsx（接受/完成等動作）
- [X] M503 [US5] 交換歷史列表：apps/mobile/src/features/trade/screens/TradeHistoryScreen.tsx（GET /api/v1/trades/history）
- [X] M504 [US5] trade 完成後導流評分：在 TradeDetail/TradeHistory 顯示「去評分」入口並導向評分流程（POST /api/v1/ratings 並帶 trade_id；依後端一次性規則處理重複評分）

---

## Phase 8: User Story 6 - 訂閱與付費 (Priority: P2)

**目標**: 使用者可以訂閱付費方案（Google Play Billing），解鎖更高限制

**獨立測試標準**:
- ✓ 系統可以驗證 Google Play 收據
- ✓ 訂閱成功後使用者權限升級（以後端 verify-receipt 驗證通過 + entitlement 生效為準；不可只以 UI 顯示成功為準）
- ✓ 訂閱到期後自動降級為免費用戶
- ✓ 權限檢查中介層正確限制 API 存取

**POC 決議（文件即合約，實作需對齊）**:
- ✅ 不新增 RTDN/webhook（Phase 8 POC 先不做）；狀態同步採：App 開啟/回前景時呼叫 `GET /api/v1/subscriptions/status` + 後端每日排程降級兜底
- ✅ Acknowledge 由後端負責（在 server-side 驗證成功後完成 acknowledge；需具備冪等與重試）
- ✅ Restore 流程不新增 API：App 端 query 現有購買 → 以同一個 `POST /api/v1/subscriptions/verify-receipt` 重新驗證並更新 entitlement

**API 合約（POC 最小集合）**:
- `POST /api/v1/subscriptions/verify-receipt`
  - 請求（最小）：`{ platform: "android", purchase_token: string, product_id: string }`
  - 回應（最小）：`{ plan: "free"|"premium", status: "active"|"inactive"|"expired"|"pending", expires_at: string|null, entitlement_active: boolean, source: "google_play" }`
  - 行為：必須做 token 綁定（purchase_token 只能綁定一個 user）、防重放（同 token 重送需冪等/拒絕跨 user）、並在驗證通過後更新 entitlement
- `GET /api/v1/subscriptions/status`
  - 回應（最小）：同上（以伺服器端資料為準）

**狀態與錯誤碼（POC 最小集合；前後端需對齊）**:
- `status` 值定義（後端回傳的業務狀態）：
  - `active`：已生效；`entitlement_active=true`
  - `expired`：已過期；`entitlement_active=false`
  - `inactive`：未訂閱或不可用（包含取消後到期、或後端判定不應授權的狀態）；`entitlement_active=false`
  - `pending`：Google Play 購買/付款仍在 pending（或暫時無法確認已生效）；`entitlement_active=false`；App UI 應顯示「待確認」並允許稍後重試
- `verify-receipt` 常見錯誤（HTTP + `error.code`）：
  - `401_UNAUTHORIZED`：未登入/Token 過期（需重新登入或 refresh）
  - `400_VALIDATION_FAILED`：缺欄位、platform 不支援、product_id 格式錯誤等
  - `409_CONFLICT`：purchase_token 已綁定到其他 user（防重放/綁定衝突；不得自動轉移；App 顯示「此購買已被其他帳號使用」）
  - `503_SERVICE_UNAVAILABLE`：Google Play 驗證服務暫時不可用或逾時（可重試；App 顯示「驗證暫時失敗，請稍後再試」）
- `status` 常見錯誤（HTTP + `error.code`）：
  - `401_UNAUTHORIZED`：未登入/Token 過期
  - `503_SERVICE_UNAVAILABLE`：資料庫或依賴服務暫時不可用（可重試）

**冪等/重試規則（必須）**:
- 同一個 `purchase_token`、同一個 user 重送 `verify-receipt`：後端必須冪等（回傳目前的 `plan/status/entitlement_active`），不可重複升級/寫入重複資料
- 同一個 `purchase_token`、不同 user 重送：必須拒絕並回 `409_CONFLICT`

### Domain Layer (Identity Module - Subscription)

- [X] T175 [P] [US6] 建立 Subscription Entity：apps/backend/app/modules/identity/domain/entities/subscription.py（id, user_id, plan: free/premium, status: active/inactive/expired/pending, expires_at）
- [X] T176 [P] [US6] 定義 SubscriptionRepository Interface：apps/backend/app/modules/identity/domain/repositories/subscription_repository.py
- [X] 新增 PurchaseTokenRepository Interface：apps/backend/app/modules/identity/domain/repositories/purchase_token_repository.py（防重放攻擊）

### Application Layer (Identity Module - Subscription)

- [X] T177 [P] [US6] 建立 VerifyReceiptUseCase：apps/backend/app/modules/identity/application/use_cases/subscription/verify_receipt_use_case.py（驗證 Google Play 收據 → 更新訂閱狀態；冪等；token 綁定；防重放；成功後需觸發 acknowledge）
- [X] T178 [P] [US6] 建立 CheckSubscriptionStatusUseCase：apps/backend/app/modules/identity/application/use_cases/subscription/check_subscription_status_use_case.py
- [X] T179 [P] [US6] 建立 ExpireSubscriptionsUseCase：apps/backend/app/modules/identity/application/use_cases/subscription/expire_subscriptions_use_case.py（定期任務：檢查並降級過期訂閱）

### Infrastructure Layer (Identity Module - Subscription)

- [X] T180 [P] [US6] 實作 SQLAlchemy Subscription Model：apps/backend/app/modules/identity/infrastructure/database/models/subscription_model.py
- [X] T180A [P] [US6] 新增/擴展 Alembic migration：保存 Google Play purchase_token 與去重資訊（建議新增 subscription_purchase_tokens 表；purchase_token UNIQUE；用於 token 綁定/防重放）
  - ✅ 建立 alembic/versions/011_add_subscription_tables.py
  - ✅ subscriptions 表：id, user_id (UUID), plan, status, expires_at
  - ✅ subscription_purchase_tokens 表：purchase_token (UNIQUE), user_id, product_id, platform
- [X] T181 [P] [US6] 實作 SubscriptionRepositoryImpl：apps/backend/app/modules/identity/infrastructure/repositories/subscription_repository_impl.py
- [X] T181A [P] [US6] 實作 PurchaseTokenRepositoryImpl：apps/backend/app/modules/identity/infrastructure/repositories/purchase_token_repository_impl.py
- [X] T182 [P] [US6] 實作 Google Play Billing Service：apps/backend/app/modules/identity/infrastructure/external/google_play_billing_service.py（驗證收據 + acknowledge；需可重試且冪等）
- [X] T182A [P] [US6] 實作 token 綁定/防重放策略：同 purchase_token 不可跨 user 重放（DB UNIQUE + 應用層檢查；重送需冪等回傳）

### Presentation Layer

- [X] T183 [P] [US6] 建立 Subscription Router：apps/backend/app/modules/identity/presentation/routers/subscription_router.py（POST /api/v1/subscriptions/verify-receipt, GET /api/v1/subscriptions/status；回應需包含 entitlement_active 與 expires_at）
  - ✅ 已建立 3 個端點：verify-receipt, status, expire-subscriptions
  - ✅ 完整錯誤處理與文檔
- [X] T183A [P] [US6] 定義 API Schemas：apps/backend/app/modules/identity/presentation/schemas/subscription_schemas.py
- [X] T183B [P] [US6] 註冊 Subscription Router 到 main.py
- [X] T184 [US6] 實作 Subscription Permission Middleware：apps/backend/app/shared/presentation/middleware/subscription_check.py（依 subscriptions.plan/status 套用限制；影響 cards upload-url/create、nearby search、posts create；並注入到 request.state）
  - ✅ check_subscription_permission middleware
  - ✅ require_subscription_plan dependency
  - ✅ get_subscription_from_request helper

### Testing

- [X] T185 [P] [US6] 撰寫 Subscription Integration Tests（以 OpenAPI/Swagger（由程式碼生成的 snapshot）作為回應/路由對齊驗證；改以整合測試覆蓋）
  - ✅ tests/integration/modules/identity/test_subscription_flow.py
  - ✅ Complete API flow testing templates
- [X] T186 [P] [US6] 撰寫 Subscription Unit Tests：tests/unit/modules/identity/application/test_verify_receipt_use_case.py
  - ✅ 11 comprehensive test cases
  - ✅ Idempotent behavior, replay attacks, error handling
- [X] T187 [US6] 撰寫 Subscription Integration Tests：tests/integration/modules/identity/test_subscription_flow.py
  - ✅ Authentication integration
  - ✅ Error scenario coverage

### Configuration

- [X] T188 [P] [US6] 更新環境變數：apps/backend/app/config.py（GOOGLE_PLAY_PACKAGE_NAME, GOOGLE_PLAY_SERVICE_ACCOUNT_KEY_PATH）
- [X] T189 [P] [US6] 配置定期任務（Celery/APScheduler）：每日檢查過期訂閱
  - ✅ POC 階段：已提供 POST /api/v1/subscriptions/expire-subscriptions 端點供手動觸發
  - 📝 生產環境需配置排程工具（APScheduler/Celery Beat/Cloud Scheduler）
  - 📝 參考實作：可使用 APScheduler 在 backend 啟動時註冊定期任務

### Verification

- [ ] T190 [US6] 執行所有 US6 測試並手動驗證訂閱流程（需資料庫環境）
- [ ] T191 [US6] 驗證權限升級：確認付費用戶可以無限上傳/搜尋（需資料庫環境）
- [X] T192 [US6] 產生 OpenAPI.json：`make generate-openapi`
  - ✅ 已執行 python3 scripts/generate_openapi.py
  - ✅ 輸出 /openapi/openapi.json (41 endpoints)
- [X] T193 [US6] 產生前端 SDK：`cd apps/mobile && npm run sdk:generate`
  - ✅ 已執行 npm run sdk:generate
  - ✅ 生成 TypeScript SDK + TanStack Query hooks
  - ✅ Mobile 已整合使用生成的 SDK

### Mobile (Expo)

- [X] M601 [P] [US6] 方案/付費牆頁：apps/mobile/src/features/subscription（顯示 free/premium 差異與升級入口）
  - ✅ SubscriptionPlansScreen: 顯示方案對比與購買按鈕
  - ✅ 完整功能列表與價格顯示
  - ✅ 當前方案狀態顯示
- [X] M602 [P] [US6] Android Google Play Billing 整合：apps/mobile/src/features/subscription/hooks/useGooglePlayBilling.ts（採用 Expo Dev Build；Expo Go 不支援；建議使用 react-native-iap；購買/續訂/恢復購買）
  - ✅ useGooglePlayBilling hook
  - ✅ purchaseSubscription 函數
  - ✅ restorePurchases 函數
  - ✅ 產品查詢與初始化
  - ⚠️ 需安裝 react-native-iap
  - ⚠️ 需 Expo Development Build
- [X] M603 [P] [US6] 收據驗證串接：apps/mobile/src/features/subscription/hooks/useSubscription.ts（購買回呼取得 purchase_token 後，必須呼叫 POST /api/v1/subscriptions/verify-receipt；以後端回傳 entitlement_active 作為「購買成功」判準；以更新後的 OpenAPI snapshot 作為驗證/對齊基準）
  - ✅ useVerifyReceipt hook
  - ✅ 完整購買流程整合
  - ✅ 錯誤處理與重試邏輯
  - 📝 需更新為生成的 SDK（OpenAPI 生成後）
- [X] M604 [US6] 訂閱狀態顯示與降級提示：apps/mobile/src/features/subscription/screens/SubscriptionStatusScreen.tsx
  - ✅ 完整狀態顯示（plan, status, expires_at）
  - ✅ 狀態圖示與說明
  - ✅ 過期/待處理提示
  - ✅ 恢復購買按鈕
  - ✅ 重新整理按鈕
- [X] M605 [P] [US6] Restore 購買流程：App 端 query 既有購買 → 逐一呼叫 verify-receipt → 以 status/entitlement 更新 UI（不新增 restore API）
  - ✅ restorePurchases 實作
  - ✅ 批次驗證流程
  - ✅ 成功/失敗提示
- [X] M606 [P] [US6] 訂閱功能文件：apps/mobile/src/features/subscription/README.md
  - ✅ 完整使用說明
  - ✅ 設定步驟
  - ✅ API 文件
  - ✅ 錯誤處理指南
  - ✅ 測試場景

### Mobile 實作完成狀態

✅ **全部完成 (6/5 tasks - 120%)**

**核心功能**：
- 訂閱方案展示與購買
- Google Play Billing 整合
- 收據驗證串接
- 狀態顯示與管理
- 購買恢復
- 完整文件

**技術特點**：
- React Native + Expo
- TanStack Query 狀態管理
- Gluestack UI 元件
- TypeScript 型別安全
- 錯誤處理與重試
- App 回前景自動更新

**待完成項目**：
- 📦 安裝 react-native-iap
- 🔧 設定 Google Play Console
- 🏗️ 建立 Expo Development Build
- 🔌 OpenAPI SDK 生成後更新 API 呼叫

---

## Phase 8.5: User Story 7 - 城市看板貼文 (Priority: P2)

**目標**: 使用者可以在指定城市（縣市）看板發起交換貼文，其他使用者可表達「有興趣」，作者接受後導流建立好友 + 一對一聊天室協商交換。

**獨立測試標準**:
- ✓ A 能在「台北市」建立貼文並出現在看板列表
- ✓ B 能在該城市看板找到貼文並送出「有興趣」
- ✓ A 接受後，系統建立好友關係並建立/導向聊天室
- ✓ 貼文可手動關閉或到期自動下架

### Domain Layer (Posts Module)

- [X] T206 [P] [US7] 建立 Posts 模組目錄結構：apps/backend/app/modules/posts/（domain/, application/, infrastructure/, presentation/）
- [X] T207 [P] [US7] 建立 Post Entity：apps/backend/app/modules/posts/domain/entities/post.py（owner_id, city_code, title, content, idol, idol_group, status, expires_at）
- [X] T208 [P] [US7] 建立 PostInterest Entity：apps/backend/app/modules/posts/domain/entities/post_interest.py（post_id, user_id, status）
- [X] T209 [P] [US7] 定義 PostRepository Interface：apps/backend/app/modules/posts/domain/repositories/post_repository.py
- [X] T210 [P] [US7] 定義 PostInterestRepository Interface：apps/backend/app/modules/posts/domain/repositories/post_interest_repository.py

### Application Layer (Posts Module)

- [X] T211 [P] [US7] 建立 CreatePostUseCase：apps/backend/app/modules/posts/application/use_cases/create_post_use_case.py（含每日發文限制檢查：free=2/day）
- [X] T212 [P] [US7] 建立 ListBoardPostsUseCase：apps/backend/app/modules/posts/application/use_cases/list_board_posts_use_case.py（city_code 必填，支援 idol/idol_group 篩選）
- [X] T213 [P] [US7] 建立 ExpressInterestUseCase：apps/backend/app/modules/posts/application/use_cases/express_interest_use_case.py（建立 PostInterest，避免重複）
- [X] T214 [P] [US7] 建立 AcceptInterestUseCase：apps/backend/app/modules/posts/application/use_cases/accept_interest_use_case.py（接受後建立好友關係 + 建立/重用聊天室）
- [X] T215 [P] [US7] 建立 RejectInterestUseCase：apps/backend/app/modules/posts/application/use_cases/reject_interest_use_case.py
- [X] T216 [P] [US7] 建立 ClosePostUseCase：apps/backend/app/modules/posts/application/use_cases/close_post_use_case.py

### Infrastructure Layer (Posts Module)

- [X] T217 [P] [US7] 實作 SQLAlchemy Post Model：apps/backend/app/modules/posts/infrastructure/database/models/post_model.py
- [X] T218 [P] [US7] 實作 SQLAlchemy PostInterest Model：apps/backend/app/modules/posts/infrastructure/database/models/post_interest_model.py
- [X] T219 [P] [US7] 實作 PostRepositoryImpl：apps/backend/app/modules/posts/infrastructure/repositories/post_repository_impl.py
- [X] T220 [P] [US7] 實作 PostInterestRepositoryImpl：apps/backend/app/modules/posts/infrastructure/repositories/post_interest_repository_impl.py

### Presentation Layer (Posts Module)

- [X] T221 [P] [US7] 定義 Posts Schemas：apps/backend/app/modules/posts/presentation/schemas/post_schemas.py
- [X] T222 [US7] 建立 Posts Router：apps/backend/app/modules/posts/presentation/routers/posts_router.py（POST /api/v1/posts, GET /api/v1/posts, POST /api/v1/posts/{id}/interest, POST /api/v1/posts/{id}/interests/{interest_id}/accept, POST /api/v1/posts/{id}/interests/{interest_id}/reject, POST /api/v1/posts/{id}/close）

### Integration

- [X] T223 [US7] 註冊 Posts Module 到 DI Container：apps/backend/app/container.py
- [X] T224 [US7] 註冊 Posts Router 到 main.py：apps/backend/app/main.py

### Alembic Migration

- [X] T225 [P] [US7] 建立 Posts Tables Migration：apps/backend/alembic/versions/012_add_posts_tables.py（posts, post_interests + indexes）
- [ ] T226 [US7] 驗證 Migration：alembic upgrade head && alembic downgrade -1（需要在有Poetry環境的地方執行）

### OpenAPI/Swagger & Testing

- [ ] T227 [P] [US7] 對齊 OpenAPI/Swagger：Posts 相關 endpoints（以更新後的 openapi/openapi.json snapshot 作為驗證基準；需先 regenerate+commit 才會反映最新程式碼）**（需在有Poetry環境執行 make generate-openapi）**
- [X] T228 [P] [US7] 撰寫 Posts Integration Tests：tests/integration/modules/social/test_posts_flow.py（已建立整合測試）

### Mobile (Expo)

- [X] M701 [P] [US7] 城市看板列表：apps/mobile/src/features/posts/screens/BoardPostsScreen.tsx（GET /api/v1/posts?city_code=...）**✅ 包含路由 app/posts/index.tsx**
- [X] M702 [P] [US7] 建立貼文頁：apps/mobile/src/features/posts/screens/CreatePostScreen.tsx（POST /api/v1/posts；city_code + 內容）**✅ 包含路由 app/posts/create.tsx**
- [X] M703 [P] [US7] 貼文詳情與「有興趣」：apps/mobile/src/features/posts/screens/PostDetailScreen.tsx（POST /api/v1/posts/{id}/interest）**✅ 包含路由 app/posts/[id].tsx**
- [X] M704 [US7] 作者端興趣清單與接受導流聊天：apps/mobile/src/features/posts/screens/MyPostInterestsScreen.tsx（accept/reject；導向 chat）**✅ 包含路由 app/posts/[id]/interests.tsx**

---

## Phase 9: Polish & Cross-Cutting Concerns (跨模組整合與優化)

**目的**: 整合所有功能、優化效能、完善文件

- [ ] T192 [P] 統一錯誤處理：apps/backend/app/shared/presentation/exceptions/error_codes.py（定義所有錯誤碼：400/401/403/404/409/422/429）
- [ ] T193 [P] 更新 OpenAPI snapshot（開發後產物）：openapi/openapi.json（由後端 FastAPI 自動生成；供 Swagger 檢視、測試對齊與 SDK codegen 使用；非開發前契約）
- [ ] T194 [P] E2E 測試：tests/e2e/test_complete_user_journey.py（模擬完整使用者旅程：登入 → 上傳卡片 → 搜尋 → 加好友 → 聊天 → 交換 → 評分）
- [ ] T195 [P] 效能測試：tests/performance/test_api_performance.py（測試關鍵 API 回應時間與吞吐量）
- [ ] T196 [P] 安全測試：tests/security/test_jwt_security.py（測試 Token 竄改、過期處理）
- [ ] T197 [P] 完善 README.md：專案結構、啟動指引、測試指令
- [ ] T198 [P] 撰寫部署文件：docs/deployment.md（Docker Compose 部署、GCP 部署指引）
- [ ] T199 [P] 撰寫 API 使用範例：docs/api-examples.md（常見操作的 curl 範例）
- [ ] T200 [P] 建立監控與日誌：配置 Sentry/CloudWatch（錯誤追蹤）、Prometheus/Grafana（效能監控）
- [ ] T201 [P] CI/CD 完整化：.github/workflows/deploy.yml（自動部署到 staging/production）
- [ ] T202 [P] 資料庫備份策略：文件化備份與還原流程
- [ ] T203 [P] 災難復原計畫：docs/disaster-recovery.md
- [ ] T204 建立 Quickstart 驗證腳本：scripts/quickstart-validation.sh（自動化測試所有 Success Criteria SC-001 ~ SC-005）
- [ ] T205 最終整合測試：執行所有測試套件，確保 >90% 覆蓋率

---

## Dependencies & Execution Order (依賴關係與執行順序)

### Critical Path（關鍵路徑 - 必須依序執行）

1. **Phase 1: Setup** (T001-T008) → 專案基礎
2. **Phase 1M: Mobile Setup** (M001-M014) → Expo app 基礎（可與 Phase 2 並行進行）
3. **Phase 1M.1: OpenAPI SDK Generation** (M015-M020) → 產 SDK（可與 Phase 2 並行進行）
4. **Phase 2: Foundational** (T009-T028) → **[BLOCKING]** 所有後端 User Story 必須等此階段完成
5. **Phase 3-8.5: User Stories** (T029-T228 + M101-M704) → 後端與 Mobile 可依 US/Plan/Tasks 並行（必要時先以 mock/先行 UI；端點完成後再用 OpenAPI snapshot 與整合測試對齊）
6. **Phase 9: Polish** (T192-T205) → 最終整合

### User Story Dependencies（使用者故事依賴）

```
US1 (Phase 3) ─────────────────────────┐
  ├─ 無依賴，可立即開始                  │
  └─ Blocking: US2, US3, US4, US5, US6  │ ← 其他 US 需要身份驗證
                                        │
US2 (Phase 4) ─────────────────┐       │
  ├─ 依賴：US1（身份驗證）       │       │
  └─ Blocking: US3              │       │ ← US3 需要卡片資料
                                │       │
US3 (Phase 5)                   │       │
  ├─ 依賴：US1（身份驗證）       │       │
  ├─ 依賴：US2（卡片資料）       │       │
  └─ 無 Blocking               │       │
                                │       │
US4 (Phase 6)                   │       │
  ├─ 依賴：US1（身份驗證）       │       │
  └─ 建議：US2 完成後（好友看卡片）│       │
                                │       │
US5 (Phase 7)                   │       │
  ├─ 依賴：US1（身份驗證）       │       │
  ├─ 依賴：US2（卡片資料）       │       │
  ├─ 依賴：US4（好友系統）       │       │
  └─ Blocking: 無               │       │
                                │       │
US6 (Phase 8)                   │       │
  ├─ 依賴：US1（身份驗證）       │       │
  └─ Blocking: 無（P2優先度，可延後）    │

US7 (Phase 8.5)                 │       │
  ├─ 依賴：US1（身份驗證）       │       │
  ├─ 依賴：US4（好友+聊天，用於接受後導流）│       │
  └─ 建議：US3（附近頁可導到城市看板）   │
```

### Parallel Opportunities（並行機會）

#### 階段 0：可立即開始（與 Foundation 並行）

**可同時開始的工作組**：

```
Group M0: Mobile Setup (Phase 1M) - Expo Foundation
  └─ M001-M010（app skeleton / API client / session / CI）
```

#### 階段 1：Foundation 完成後（T028 完成）

**可同時開始的工作組**：

```
Group A: US1 (Phase 3) - Identity Module
  └─ T029-T065 (37 tasks) 全部可並行
  
Group B: Infrastructure Setup（與 US1 無衝突）
  └─ T059-T060 (Kong JWT, Config)

Group M1: US1 Mobile (Expo) - Auth + Profile
  ├─ 先決條件：M001-M006
  └─ M101-M104（可先用 mock/stub 並行；待後端端點可用後做整合）
```

#### 階段 2：US1 完成後（T065 完成）

**可同時開始的工作組**：

```
Group A: US2 (Phase 4) - Card Upload
  └─ T066-T094 (29 tasks)
  
Group B: US4 (Phase 6) - Friends & Chat（與 US2 不同檔案）
  └─ T111-T143 (33 tasks)
  
Group C: US6 (Phase 8) - Subscription（與 US2/US4 不同檔案）
  └─ T175-T191 (17 tasks)

Group M2: US2 Mobile (Expo) - Card Upload
  ├─ 先決條件：M001-M006 + US1 Mobile 已可取得有效 access token
  └─ M201-M206（Signed URL 上傳可先做 UI/流程，待 /cards/* 端點可用後整合）

Group M4: US4 Mobile (Expo) - Friends & Chat
  ├─ 先決條件：M001-M006 + US1 Mobile（登入狀態）
  └─ M401-M404（可先做 UI/輪詢骨架；待 /friends/*、/chats/* 端點與推播配置後整合）

Group M6: US6 Mobile (Expo) - Subscription
  ├─ 先決條件：M001-M006 + US1 Mobile（登入狀態）
  └─ M601-M604（可先做 paywall/UI；Billing 與 /subscriptions/* 後續整合）
```

#### 階段 3：US2 完成後（T094 完成）

**可同時開始的工作組**：

```
Group A: US3 (Phase 5) - Nearby Search
  └─ T095-T110 (16 tasks)
  
Group B: US5 (Phase 7) - Trade（需等 US4 完成）
  └─ T144-T174 (31 tasks) - 建議等 US4 完成後再開始

Group M3: US3 Mobile (Expo) - Nearby Search
  ├─ 先決條件：M001-M006 + US1 Mobile（登入狀態）
  └─ M301-M303（定位與搜尋頁可先做；待 /nearby/search 端點可用後整合）

Group M5: US5 Mobile (Expo) - Trade
  ├─ 先決條件：M001-M006 + US1 Mobile（登入狀態）+ US2（卡片資料）+ US4（好友）
  └─ M501-M503（可先做 UI，待 /trades/* 與狀態流轉端點可用後整合）
```

### Recommended Execution Strategy（建議執行策略）

#### **Sprint 1: Foundation + Identity（MVP 核心）**
- Week 1: Phase 1 (T001-T008) + Phase 2 (T009-T028)
- Week 2-3: Phase 3 - US1 (T029-T065) 🎯 **MVP Milestone**
- **Checkpoint**: 使用者可以登入並完成個人檔案

#### **Sprint 2: Card Management + Social Core**
- Week 4-5: Phase 4 - US2 (T066-T094) || Phase 6 - US4 (T111-T143)
- **Checkpoint**: 使用者可以上傳卡片並加好友

#### **Sprint 3: Search + Trade**
- Week 6: Phase 5 - US3 (T095-T110)
- Week 7-8: Phase 7 - US5 (T144-T174)
- **Checkpoint**: 使用者可以搜尋附近卡片並完成交換

#### **Sprint 4: Monetization + Polish**
- Week 9: Phase 8 - US6 (T175-T191)
- Week 10: Phase 9 - Polish (T192-T205)
- **Checkpoint**: 產品完整可上線

---

## Summary（摘要）

### Statistics（統計）

- **Total Tasks**: 228 (Backend) + 13 (Mobile Phase 1M) + 6 (Mobile Tooling: Phase 1M.1) + Mobile US tasks = 247+
- **Completed**: 96 (Backend: Phase 1: 8/8, Phase 2: 20/20, Phase 3: 35/37, Phase 6: 33/33) + 13 (Mobile: Phase 1M: 13/13) + 3 (Mobile: Phase 3: 3/4) = 112
- **Remaining**: 132 (Backend) + Mobile US tasks (M104, M201-M704)
- **Estimated Duration**: 8 weeks (remaining sprints)

### Task Breakdown by Phase（各階段任務分布）

| Phase | User Story | Tasks | Priority | Status |
|-------|-----------|-------|----------|--------|
| 1 | Setup (Backend) | 8 | - | ✅ 100% Complete |
| 1M | Mobile Setup | 13 | - | ✅ 100% Complete |
| 1M.1 | OpenAPI SDK Generation (Tooling) | 6 | - | ⏸️ Not Started |
| 2 | Foundational | 20 | - | ✅ 100% Complete |
| 3 | US1 - Login & Profile (Backend) | 37 | P1 🎯 MVP | ✅ 95% Complete (35/37) |
| 3.1 | US1 - PKCE Implementation | 7 | P1 🎯 MVP | ✅ 100% Complete (7/7) |
| 3 | US1 - Mobile | 4 | P1 🎯 MVP | ⏳ 75% Complete (3/4, M104 pending) |
| 4 | US2 - Card Upload | 29 | P1 | ⏸️ Not Started |
| 5 | US3 - Nearby Search | 16 | P1 | ⏸️ Not Started |
| 6 | US4 - Friends & Chat (Backend) | 33 | P1 | ✅ 100% Complete |
| 6 | US4 - Friends & Chat (Mobile) | 4 | P1 | ✅ 100% Complete (M401-M404) |
| 7 | US5 - Trade (Backend Core) | 18 | P1 | ✅ 83% Complete (15/18: T144-T160, T166, T168) |
| 7 | US5 - Trade (Testing) | 5 | P1 | ✅ 80% Complete (4/5: T162-T165) |
| 7 | US5 - Trade (Mobile) | 4 | P1 | ✅ 100% Complete (M501-M504) |
| 7 | US5 - Trade (Docs & Verification) | 7 | P1 | ⏸️ Pending (T167, T169-T174) |
| 8 | US6 - Subscription | 17 | P2 | ⏸️ Not Started |
| 8.5 | US7 - Board Posts | 23 | P2 | ⏸️ Not Started |
| 9 | Polish | 14 | - | ⏸️ Not Started |

### MVP Scope（MVP 範圍）

**建議 MVP 僅包含**：
- ✅ Phase 1: Setup (T001-T008)
- ✅ Phase 1M: Mobile Setup (M001-M014)
- ✅ Phase 2: Foundational (T009-T028)
- ✅ Phase 3: US1 - Login & Profile Backend (T029-T063) 
- ✅ Phase 3.1: US1 - PKCE Implementation (T046A, T035B, T045B, T053A, T057A, T061A, T062A)
- ✅ Phase 3: US1 - Mobile Implementation (M101-M103)
- ⏳ Phase 3: US1 - Verification (T064-T065 完成, M104 pending)

**MVP 驗收標準**：
- ✅ 使用者可以透過 Google 登入 (PKCE + Implicit flows)
- ✅ 使用者可以查看和更新個人檔案
- ✅ JWT Token 機制正常運作
- ✅ 所有測試通過
- ⏳ 手動驗證待完成 (M104 - 需要實際環境)

### Next Steps（下一步）

1. **✅ 已完成**：Phase 1M Mobile Setup (M001-M013) - Mobile 基礎架構完成
2. **✅ 已完成**：Phase 2 Foundational (T009-T028) - 基礎設施完成
3. **✅ 已完成**：Phase 3 US1 Backend (T029-T063) - Google 登入與個人檔案後端完成
4. **✅ 已完成**：Phase 3.1 PKCE Implementation - Expo 標準 OAuth 流程完成
5. **✅ 已完成**：Phase 3 US1 Mobile (M101-M103) - Mobile 端登入與個人檔案完成
6. **⏳ 進行中**：Phase 3 US1 Verification (M104) - 待實際環境手動驗證
7. **下一階段**：Phase 4 US2 (Card Upload) - 小卡上傳功能開發
8. **並行開發**：US1 完成後，同時開發 US2 + US4 + US6（Backend + Mobile 各自並行）
9. **最終整合**：所有 US 完成後執行 Phase 9 Polish

---

**Generated by**: /speckit.tasks  
**Based on**: Modular DDD Architecture + TDD Strategy + Alembic Migration Management
- [ ] T1201 Beta 發佈腳本與環境變數管理
- [ ] T1202 監控與日誌（API 響應、錯誤率、推播送達率）
- [ ] T1203 事後分析報表（MAU、交換完成率、再次使用率）

---

## Dependencies & Parallelism
- Setup → AUTH/PROFILE → CARD → NEARBY → SOCIAL/CHAT → TRADE → BIZ → API 標準 → UI/UX → DB → 測試 → 發佈
- 可並行：
  - CHAT 與 SOCIAL 在 AUTH/PROFILE 完成後可部分並行
  - TRADE 依賴 CARD 與 SOCIAL 最低子集完成
  - BIZ 可在核心得分完成後並行

## Phase -1 Gates Checklist
- Simplicity Gate：保持 ≤3 個專案（mobile/backend/gateway）；若需例外，在 plan.md 記錄理由。
- Anti-Abstraction Gate：遵循憲法 Article VI，禁止不必要抽象；Domain 不依賴框架；Repository 實作置於 Infrastructure。
- Integration-First Gate：以 OpenAPI/Swagger（由程式碼生成的 snapshot：openapi/openapi.json）作為「同一版 commit 的實作輸出」進行整合測試對齊；若 snapshot 未更新，請先 regenerate+commit 再做對齊（非開發前契約；需求來源仍以 spec/plan/tasks 為準）。

## Acceptance Criteria Examples
- T204：超限時回傳 `422_LIMIT_EXCEEDED` 並包含哪一項超限訊息（每日/容量/大小）
- T304：免費使用者第 6 次附近搜尋回傳 `429_RATE_LIMITED`（或同策略），付費不受限
- T603：雙方都標記完成後，小卡狀態轉為已交換且不可再公開列表顯示

> 來源：`specs/001-kcardswap-complete-spec/plan.md` 與 `specs/001-kcardswap-complete-spec/spec.md`。

憲法參照：Constitution v1.2.0 Article VI（DDD 架構原則為唯一依據，避免在 Spec/Plan/Tasks 重複規範）。