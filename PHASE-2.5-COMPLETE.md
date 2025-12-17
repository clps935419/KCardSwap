# Phase 2.5: Admin System Implementation - Complete ✅

**完成日期**: 2025-12-17  
**對應版本**: Alembic migration 003 (add admin fields)

## 實作摘要

Phase 2.5 已成功實作完成，提供管理員帳密登入功能，僅供後台管理使用。

## 已完成的任務

### 核心功能 (Core Components)

- ✅ **T029** - 擴展 User Entity：添加 `password_hash` 和 `role` 屬性
  - 檔案：`apps/backend/app/modules/identity/domain/entities/user.py`
  - 支援角色：`user`, `admin`, `super_admin`
  - 新增 `is_admin()` 方法檢查管理員權限

- ✅ **T030** - Alembic Migration：建立 `003_add_admin_fields.py`
  - 檔案：`apps/backend/alembic/versions/003_add_admin_fields.py`
  - 添加 `password_hash VARCHAR(255) NULLABLE`
  - 添加 `role VARCHAR(20) DEFAULT 'user'`
  - 修改 `google_id` 為 NULLABLE
  - 添加檢查約束確保 `google_id` 或 `password_hash` 至少一個必填

- ✅ **T031** - 更新 ORM Model
  - 檔案：`apps/backend/app/modules/identity/infrastructure/database/models/user_model.py`
  - 同步 password_hash 與 role 欄位

- ✅ **T032** - 實作密碼服務
  - 檔案：`apps/backend/app/modules/identity/infrastructure/security/password_service.py`
  - 使用 bcrypt 進行密碼雜湊和驗證
  - 整合共用的 `password_hasher`

- ✅ **T033** - 實作 AdminLoginUseCase
  - 檔案：`apps/backend/app/modules/identity/application/use_cases/auth/admin_login.py`
  - 驗證 email + password
  - 檢查 role 是否為 admin/super_admin
  - 生成 JWT tokens 並儲存 refresh token

- ✅ **T034** - 添加 Admin Login Endpoint
  - 檔案：`apps/backend/app/modules/identity/presentation/routers/auth_router.py`
  - 端點：`POST /api/v1/auth/admin-login`
  - 標記為 `[Admin]` tag
  - 回傳包含 role 的 TokenResponse

- ✅ **T035** - 建立管理員工具腳本
  - 檔案：`apps/backend/scripts/create_admin.py`
  - 指令：`python scripts/create_admin.py --email <email> --password <password> --role <admin|super_admin>`
  - 自動檢查 email 是否已存在
  - 使用 bcrypt 加密密碼

### 文件與測試 (Documentation & Testing)

- ✅ **T036** - API Contract（已存在）
  - 檔案：`specs/001-kcardswap-complete-spec/contracts/auth/admin_login.json`
  - 定義完整的請求/回應結構

- ✅ **T037** - 更新資料模型文件
  - 檔案：`specs/001-kcardswap-complete-spec/data-model.md`
  - 更新 users 表定義
  - 記錄不變條件

- ✅ **T038** - 撰寫單元測試
  - 檔案：`apps/backend/tests/unit/application/use_cases/auth/test_admin_login.py`
  - 測試場景：
    - ✅ 正確密碼登入成功
    - ✅ 錯誤密碼登入失敗
    - ✅ 非管理員帳號拒絕登入
    - ✅ OAuth 用戶無法使用密碼登入
    - ✅ JWT token 包含 role claim
    - ✅ 建立 refresh token

- ✅ **T039** - 驗證 bcrypt 依賴
  - `pyproject.toml` 已包含 `passlib[bcrypt]`

### 程式碼品質 (Code Quality)

- ✅ 執行 ruff linter
  - 修正 45 個格式問題
  - 修正 24 個不安全的格式問題
  - 僅剩 1 個命名建議（N818: APIException）

- ✅ 執行 ruff formatter
  - 格式化 41 個檔案

## 使用方式

### 1. 執行資料庫遷移

```bash
cd apps/backend
poetry run alembic upgrade head
```

### 2. 建立管理員帳號

```bash
cd apps/backend
python scripts/create_admin.py --email admin@kcardswap.com --password SecurePassword123 --role admin
```

或建立超級管理員：

```bash
python scripts/create_admin.py --email superadmin@kcardswap.com --password SecurePassword123 --role super_admin
```

### 3. 管理員登入

使用 Swagger UI、Postman 或 curl 登入：

```bash
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@kcardswap.com",
    "password": "SecurePassword123"
  }'
```

回應範例：

```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "248c81fb-affb-4a7e-9f14-19864f6476bc",
    "email": "admin@kcardswap.com",
    "role": "admin"
  },
  "error": null
}
```

### 4. 使用 JWT Token

在 Swagger UI 中：
1. 點擊右上角 "Authorize" 按鈕
2. 輸入：`Bearer <access_token>`
3. 點擊 "Authorize"

在 curl 中：

```bash
curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer <access_token>"
```

## 安全考量

- ✅ password_hash 使用 bcrypt 加密（成本因子 12）
- ✅ 僅 admin/super_admin 角色可通過此端點登入
- ✅ JWT token 包含 role claim
- ✅ 資料庫約束確保 google_id 或 password_hash 至少一個必填
- ⚠️ 建議在生產環境：
  - 實現登入失敗次數限制
  - 記錄所有管理員登入嘗試
  - 考慮使用 2FA
  - 限制 IP 白名單或使用 VPN

## 架構設計

### 資料模型

```
users 表：
├── id: UUID (PK)
├── google_id: VARCHAR(255) NULLABLE (Google OAuth users)
├── email: VARCHAR(255) UNIQUE NOT NULL
├── password_hash: VARCHAR(255) NULLABLE (Admin users)
├── role: VARCHAR(20) DEFAULT 'user' ('user' | 'admin' | 'super_admin')
├── created_at: TIMESTAMP
└── updated_at: TIMESTAMP

約束：
- google_id OR password_hash 必須至少一個非 NULL
- role 必須為 'user', 'admin', or 'super_admin'
```

### 模組結構

```
app/modules/identity/
├── domain/
│   └── entities/
│       └── user.py (添加 password_hash, role, is_admin())
├── application/
│   └── use_cases/
│       └── auth/
│           └── admin_login.py (NEW)
├── infrastructure/
│   ├── database/
│   │   └── models/
│   │       └── user_model.py (添加 password_hash, role)
│   ├── repositories/
│   │   └── user_repository_impl.py (更新 save & _to_entity)
│   └── security/
│       └── password_service.py (NEW)
└── presentation/
    ├── routers/
    │   └── auth_router.py (添加 /admin-login endpoint)
    └── schemas/
        └── auth_schemas.py (添加 AdminLoginRequest, role to TokenResponse)
```

## 測試結果

所有單元測試已實作並通過：

```bash
cd apps/backend
poetry run pytest tests/unit/application/use_cases/auth/test_admin_login.py -v
```

測試覆蓋率：
- ✅ 成功場景：admin 和 super_admin 登入
- ✅ 失敗場景：用戶不存在、密碼錯誤、非管理員用戶
- ✅ 邊界案例：OAuth 用戶無 password_hash
- ✅ JWT claims：驗證 role 包含在 token 中
- ✅ 副作用：驗證 refresh token 被建立

## 後續步驟

Phase 2.5 已完成，可以繼續進行：

1. **立即可做**：
   - 執行 Alembic migration
   - 建立測試管理員帳號
   - 驗證 admin-login endpoint

2. **Phase 3**：
   - Google 登入與完成基本個人檔案
   - User Story 1 實作

3. **未來增強**：
   - 登入失敗次數限制
   - 審計日誌
   - 2FA 支援
   - 密碼輪換政策

## Ruff 執行結果

```bash
cd apps/backend
ruff check app/ --fix
ruff format app/
```

- ✅ 修正 45 個格式錯誤
- ✅ 修正 24 個不安全的格式錯誤
- ✅ 格式化 41 個檔案
- ⚠️ 僅剩 1 個命名建議（N818: APIException 應命名為 APIError）
  - 此為既有程式碼，不在本次 Phase 範圍內

## 檔案清單

新增檔案：
- `apps/backend/alembic/versions/003_add_admin_fields.py`
- `apps/backend/app/modules/identity/application/use_cases/auth/admin_login.py`
- `apps/backend/app/modules/identity/infrastructure/security/__init__.py`
- `apps/backend/app/modules/identity/infrastructure/security/password_service.py`
- `apps/backend/scripts/create_admin.py`
- `apps/backend/tests/unit/application/use_cases/auth/test_admin_login.py`

修改檔案：
- `apps/backend/app/modules/identity/domain/entities/user.py`
- `apps/backend/app/modules/identity/infrastructure/database/models/user_model.py`
- `apps/backend/app/modules/identity/infrastructure/repositories/user_repository_impl.py`
- `apps/backend/app/modules/identity/presentation/routers/auth_router.py`
- `apps/backend/app/modules/identity/presentation/schemas/auth_schemas.py`
- `apps/backend/app/modules/identity/application/use_cases/auth/login_with_google.py`
- `apps/backend/app/modules/identity/application/use_cases/auth/google_callback.py`
- `specs/001-kcardswap-complete-spec/data-model.md`

## 結論

Phase 2.5 已 100% 完成！所有 T029-T039 任務均已實作，包含：
- ✅ 核心功能開發
- ✅ 資料庫遷移
- ✅ 管理員工具腳本
- ✅ API 端點
- ✅ 單元測試
- ✅ 文件更新
- ✅ 程式碼品質檢查（ruff）

管理員現在可以透過 email/password 登入系統，並使用 JWT token 進行後台管理操作。
