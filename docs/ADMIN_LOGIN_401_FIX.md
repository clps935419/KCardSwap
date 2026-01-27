# 管理員登入 401 錯誤解決指南

## 問題描述

當調用管理員登入 API (`POST /api/v1/auth/admin-login`) 時收到 401 Unauthorized 錯誤。

## 根本原因分析

### API 返回 401 的可能原因

根據代碼邏輯（`apps/backend/app/modules/identity/application/use_cases/auth/admin_login.py`），管理員登入失敗可能由以下原因導致：

| # | 原因 | 說明 |
|---|------|------|
| 1 | **用戶不存在** | 數據庫中沒有對應 email 的用戶記錄 |
| 2 | **用戶無密碼** | 用戶通過 Google OAuth 創建，沒有設置密碼 |
| 3 | **密碼錯誤** | 提供的密碼與數據庫中的密碼哈希不匹配 |
| 4 | **角色不是管理員** | 用戶的 role 不是 `admin` 或 `super_admin` |

### 最常見的問題

**管理員用戶未被創建**

默認情況下，系統不會自動創建管理員用戶。需要：
1. 在 `.env` 中設置 `INIT_DEFAULT_ADMIN=true` 並提供密碼，或
2. 手動運行初始化腳本

## 解決方案

### 方案 1: 啟用自動初始化（推薦用於開發環境）

1. **編輯 `.env` 文件**：

```bash
# 啟用管理員自動初始化
INIT_DEFAULT_ADMIN=true
DEFAULT_ADMIN_EMAIL=admin@kcardswap.local
DEFAULT_ADMIN_PASSWORD=Admin123!@#
DEFAULT_ADMIN_ROLE=admin
```

⚠️ **注意**：
- 必須提供密碼，不能留空
- 在生產環境中使用強密碼
- 密碼最少 8 個字符

2. **重啟後端服務**：

```bash
# 停止並重新啟動服務
docker compose down
docker compose up -d

# 查看日誌確認管理員已創建
docker compose logs backend | grep -i "admin"
```

3. **驗證管理員登入**：

```bash
# 使用 curl 測試
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@kcardswap.local",
    "password": "Admin123!@#"
  }'
```

成功響應應包含 access_token 和 user 信息。

---

### 方案 2: 手動創建管理員（推薦用於生產環境）

1. **確保後端服務正在運行**：

```bash
docker compose up -d
docker compose ps
```

2. **運行初始化腳本**：

```bash
# 使用默認配置（會提示輸入密碼）
docker compose exec backend python scripts/init_admin.py

# 或使用命令行參數指定
docker compose exec backend python scripts/init_admin.py \
  --email admin@kcardswap.com \
  --password "YourStrongPassword123!" \
  --role admin
```

3. **驗證創建成功**：

腳本會輸出類似以下信息：

```
✅ Default admin user created successfully!
   Email: admin@kcardswap.com
   Role: admin
   User ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Profile created: Admin (admin)

   Login at: POST /api/v1/auth/admin-login
   Credentials: admin@kcardswap.com / [password provided]
```

---

### 方案 3: 檢查現有用戶（排查問題）

如果管理員已創建但仍無法登入，可以檢查數據庫中的用戶信息：

```bash
# 連接到數據庫容器
docker compose exec db psql -U kcardswap -d kcardswap

# 查詢所有用戶
SELECT id, email, role, 
       password_hash IS NOT NULL as has_password,
       google_id IS NOT NULL as is_oauth
FROM users
ORDER BY created_at;

# 退出
\q
```

檢查結果：
- ✅ `has_password` 應該是 `t` (true)
- ✅ `role` 應該是 `admin` 或 `super_admin`
- ❌ 如果 `is_oauth` 是 `t` 且 `has_password` 是 `f`，說明這是 OAuth 用戶，無法使用密碼登入

---

## 常見錯誤排查

### 錯誤 1: "Invalid credentials or not an admin"

**可能原因**：
1. Email 或密碼錯誤
2. 用戶不是管理員角色
3. 用戶是 OAuth 用戶（沒有密碼）

**解決方法**：
- 使用方案 3 檢查數據庫中的用戶信息
- 確認使用的 email 和密碼正確
- 確認用戶的 role 是 `admin` 或 `super_admin`

---

### 錯誤 2: 腳本提示 "Admin user already exists"

**情況**：管理員已存在但忘記密碼

**解決方法**：

```bash
# 1. 連接數據庫
docker compose exec db psql -U kcardswap -d kcardswap

# 2. 刪除現有管理員（會級聯刪除相關數據）
DELETE FROM users WHERE email = 'admin@kcardswap.local';

# 3. 退出
\q

# 4. 重新創建管理員
docker compose exec backend python scripts/init_admin.py \
  --email admin@kcardswap.local \
  --password "NewPassword123!"
```

---

### 錯誤 3: 數據庫連接失敗

**症狀**：
```
Error: could not connect to database
```

**解決方法**：

1. **檢查數據庫服務狀態**：
```bash
docker compose ps db
```

2. **查看數據庫日誌**：
```bash
docker compose logs db
```

3. **確認數據庫健康檢查通過**：
```bash
docker compose exec db pg_isready -U kcardswap
```

4. **重啟所有服務**：
```bash
docker compose down
docker compose up -d
```

---

## 開發環境快速設置

如果是第一次設置開發環境，請按照以下步驟：

```bash
# 1. 複製環境變數範例
cp .env.example .env

# 2. 編輯 .env 文件，設置管理員初始化
# INIT_DEFAULT_ADMIN=true
# DEFAULT_ADMIN_PASSWORD=Admin123!@#

# 3. 啟動所有服務
docker compose up -d

# 4. 等待服務啟動（約 30 秒）
docker compose logs -f backend

# 5. 驗證管理員登入
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@kcardswap.local", "password": "Admin123!@#"}'
```

---

## API 端點說明

### 管理員登入

**端點**: `POST /api/v1/auth/admin-login`

**請求體**:
```json
{
  "email": "admin@kcardswap.local",
  "password": "Admin123!@#"
}
```

**成功響應** (200):
```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "email": "admin@kcardswap.local",
    "role": "admin"
  },
  "meta": null,
  "error": null
}
```

**失敗響應** (401):
```json
{
  "detail": {
    "code": "UNAUTHORIZED",
    "message": "Invalid credentials or not an admin"
  }
}
```

**Cookie 設置**：
- `access_token`: JWT 訪問令牌（httpOnly, 15 分鐘過期）
- `refresh_token`: JWT 刷新令牌（httpOnly, 7 天過期）

---

## 安全建議

### 開發環境
- ✅ 使用 `INIT_DEFAULT_ADMIN=true` 方便開發
- ✅ 使用簡單密碼（如 `Admin123!@#`）
- ⚠️ 不要提交 `.env` 文件到版本控制

### 生產環境
- ❌ **禁止**使用 `INIT_DEFAULT_ADMIN=true`
- ✅ 手動創建管理員並使用強密碼
- ✅ 使用密碼管理器生成和存儲密碼
- ✅ 定期更換管理員密碼
- ✅ 使用環境變數或密鑰管理服務存儲敏感信息
- ✅ 啟用 HTTPS 和 Cookie Secure 標誌

---

## 相關文件

- 初始化腳本：`apps/backend/scripts/init_admin.py`
- 啟動腳本：`apps/backend/start.sh`
- 認證路由：`apps/backend/app/modules/identity/presentation/routers/auth_router.py`
- 管理員登入用例：`apps/backend/app/modules/identity/application/use_cases/auth/admin_login.py`
- 環境變數範例：`.env.example`

---

## 需要更多幫助？

如果以上解決方案都無法解決問題：

1. 檢查後端日誌：`docker compose logs backend`
2. 檢查數據庫日誌：`docker compose logs db`
3. 查看完整的 API 文檔：`http://localhost:8000/docs`
4. 參考認證文檔：`apps/backend/docs/authentication.md`
