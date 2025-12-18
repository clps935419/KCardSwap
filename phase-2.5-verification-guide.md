# Phase 2.5 驗證指南

本文件提供 Phase 2.5 Admin System 的完整驗證步驟。

## 前置條件

1. 確保資料庫遷移已執行：
```bash
cd apps/backend
alembic upgrade head
```

2. 確保所有依賴已安裝（包含 bcrypt）。

## 驗證清單

### ✅ 1. 資料庫 Schema 驗證

檢查 users 表是否包含新欄位：

```sql
-- 連接到資料庫
psql -U kcardswap -d kcardswap

-- 查看 users 表結構
\d users

-- 應該看到以下欄位：
-- - password_hash (varchar(255), nullable)
-- - role (varchar(20), default 'user')
-- - google_id (varchar(255), nullable) -- 從 NOT NULL 改為 NULLABLE
```

### ✅ 2. 腳本功能驗證

#### Test A: init_admin.py（Idempotent）

```bash
cd apps/backend

# 第一次執行：應該建立管理員
python scripts/init_admin.py --email test@admin.com --password test123

# 輸出應該類似：
# ✅ Default admin user created successfully!
#    Email: test@admin.com
#    Role: admin
#    User ID: <uuid>

# 第二次執行：應該跳過（idempotent）
python scripts/init_admin.py --email test@admin.com --password test123

# 輸出應該類似：
# ℹ️  Admin user 'test@admin.com' already exists (ID: <uuid>)
#    Role: admin
#    Skipping creation.
```

#### Test B: create_admin.py（Fail-fast）

```bash
cd apps/backend

# 建立新管理員：應該成功
python scripts/create_admin.py --email manual@admin.com --password pass123 --role admin

# 輸出應該類似：
# ✅ Admin user created successfully!
#    Email: manual@admin.com
#    Role: admin
#    User ID: <uuid>

# 嘗試重複建立：應該報錯
python scripts/create_admin.py --email manual@admin.com --password pass123 --role admin

# 輸出應該類似：
# Error: User with email 'manual@admin.com' already exists.
# (exit code 1)
```

### ✅ 3. API Endpoint 驗證

#### 方法 1: 使用 curl

```bash
# 測試管理員登入
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@admin.com",
    "password": "test123"
  }'

# 預期回應：
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "<uuid>",
    "email": "test@admin.com",
    "role": "admin"
  },
  "error": null
}

# 測試錯誤情況：錯誤密碼
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@admin.com",
    "password": "wrongpassword"
  }'

# 預期回應（401）：
{
  "data": null,
  "error": {
    "code": 401,
    "message": "Invalid email or password",
    "details": null
  }
}

# 測試錯誤情況：非管理員用戶
# （需要先建立一個 role='user' 的用戶）
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "regular@user.com",
    "password": "password"
  }'

# 預期回應（401）：
{
  "data": null,
  "error": {
    "code": 401,
    "message": "Insufficient permissions. Admin role required.",
    "details": null
  }
}
```

#### 方法 2: 使用 Swagger UI

1. 啟動後端服務：
```bash
docker compose up -d
# 或
cd apps/backend && uvicorn app.main:app --reload
```

2. 開啟 Swagger UI：
```
http://localhost:8000/docs
```

3. 在左側找到 **"Admin"** 標籤（應該顯示一個端點）

4. 點擊 **POST /api/v1/auth/admin-login**

5. 點擊 "Try it out"

6. 輸入請求 body：
```json
{
  "email": "test@admin.com",
  "password": "test123"
}
```

7. 點擊 "Execute"

8. 檢查回應：
   - Status code: 200
   - Response body 包含 access_token 和 role

### ✅ 4. 單元測試驗證

```bash
cd apps/backend

# 執行所有 admin_login 相關測試
pytest tests/unit/application/use_cases/auth/test_admin_login.py -v

# 預期輸出：
# test_admin_login.py::test_admin_login_success PASSED
# test_admin_login.py::test_super_admin_login_success PASSED
# test_admin_login.py::test_admin_login_wrong_password PASSED
# test_admin_login.py::test_admin_login_user_not_found PASSED
# test_admin_login.py::test_non_admin_cannot_login PASSED
# test_admin_login.py::test_oauth_user_cannot_use_password_login PASSED
# test_admin_login.py::test_jwt_token_contains_role PASSED
# test_admin_login.py::test_creates_refresh_token PASSED

# 全部測試應該 PASSED
```

### ✅ 5. Docker 整合驗證

#### Test: Docker 啟動時自動初始化

1. 設定環境變數（`.env` 檔案）：
```bash
INIT_DEFAULT_ADMIN=true
DEFAULT_ADMIN_EMAIL=docker@admin.com
DEFAULT_ADMIN_PASSWORD=DockerPass123
DEFAULT_ADMIN_ROLE=admin
```

2. 啟動 Docker：
```bash
docker compose down -v  # 清除舊資料
docker compose up -d
```

3. 檢查日誌：
```bash
docker compose logs backend | grep -i "admin"
```

4. 驗證管理員已建立：
```bash
# 連接到資料庫
docker compose exec db psql -U kcardswap -d kcardswap

# 查詢管理員
SELECT id, email, role FROM users WHERE email = 'docker@admin.com';

# 應該看到一筆記錄
```

5. 測試登入：
```bash
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "docker@admin.com",
    "password": "DockerPass123"
  }'
```

### ✅ 6. 安全性驗證

#### Test A: 密碼雜湊

```bash
# 連接到資料庫
docker compose exec db psql -U kcardswap -d kcardswap

# 查看 password_hash
SELECT email, password_hash FROM users WHERE role IN ('admin', 'super_admin');

# 應該看到 bcrypt hash（以 $2b$ 開頭）
# 例如：$2b$12$abcdef...（絕不會是明文密碼）
```

#### Test B: Role 驗證

```bash
# 嘗試用 regular user 登入 admin endpoint（應該失敗）
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "regular@user.com",
    "password": "password"
  }'

# 預期：401 Unauthorized
```

#### Test C: JWT Token 包含 role

```bash
# 登入並解析 JWT token
ACCESS_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@admin.com","password":"test123"}' \
  | jq -r '.data.access_token')

# 解析 token（在 jwt.io 貼上或使用 jwt-cli）
echo $ACCESS_TOKEN | jwt decode -

# 應該包含：
# {
#   "sub": "<user_id>",
#   "email": "test@admin.com",
#   "role": "admin",  ← 重要！
#   "exp": <timestamp>
# }
```

## 驗證結果檢查表

Phase 2.5 所有功能驗證：

- [ ] ✅ T029: User Entity 包含 password_hash 和 role
- [ ] ✅ T030: Alembic migration 003 成功執行
- [ ] ✅ T031: ORM Model 正確映射 password_hash 和 role
- [ ] ✅ T032: 密碼服務正確雜湊和驗證密碼
- [ ] ✅ T033: AdminLoginUseCase 正確驗證管理員身份
- [ ] ✅ T034: POST /api/v1/auth/admin-login 端點可用
- [ ] ✅ T035: create_admin.py 可手動建立管理員
- [ ] ✅ T035A: init_admin.py 可自動初始化管理員（idempotent）
- [ ] ✅ T036: API Contract 定義完整
- [ ] ✅ T037: 資料模型文件已更新
- [ ] ✅ T038: 單元測試全部通過
- [ ] ✅ T039: bcrypt 依賴已添加

## 常見問題

### Q1: 為什麼有兩個建立管理員的腳本？

請參考 `PHASE-2.5-ADMIN-SCRIPTS-CLARIFICATION.md` 獲得完整解釋。

簡單來說：
- `create_admin.py` - 手動建立（fail-fast）
- `init_admin.py` - 自動初始化（idempotent）

### Q2: 如何重設管理員密碼？

方法 1：直接刪除並重建
```bash
# 使用資料庫刪除
DELETE FROM users WHERE email = 'admin@example.com';

# 重新建立
python scripts/create_admin.py --email admin@example.com --password newpass123
```

方法 2：使用 psql 更新（需要手動雜湊密碼）
```python
# 生成 bcrypt hash
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash = pwd_context.hash("newpassword")
print(hash)
```

```sql
UPDATE users 
SET password_hash = '<生成的hash>' 
WHERE email = 'admin@example.com';
```

### Q3: 如何在生產環境安全地管理管理員密碼？

建議使用環境變數 + secrets management：

```bash
# 在 .env 或 secrets manager
DEFAULT_ADMIN_PASSWORD=$(openssl rand -base64 32)

# 在 CI/CD 中設定
export DEFAULT_ADMIN_PASSWORD=${{ secrets.ADMIN_PASSWORD }}
```

### Q4: 測試失敗怎麼辦？

1. 檢查 Python 版本（需要 3.9+）
2. 檢查依賴是否安裝（`pip install -e .` 或 `poetry install`）
3. 檢查資料庫連線
4. 檢查 alembic migration 是否執行

## 相關文件

- `PHASE-2.5-COMPLETE.md` - Phase 2.5 完成報告
- `PHASE-2.5-ADMIN-SCRIPTS-CLARIFICATION.md` - 腳本設計說明
- `INIT-DATA-DESIGN.md` - 資料初始化設計文件
- `specs/001-kcardswap-complete-spec/tasks.md` - 任務清單
- `specs/001-kcardswap-complete-spec/contracts/auth/admin_login.json` - API Contract

## 總結

Phase 2.5 Admin System 已完整實作並通過驗證：

✅ 所有 12 個任務（T029-T039 + T035A）完成  
✅ 兩個腳本設計合理且功能正常  
✅ API 端點可通過 Swagger 存取  
✅ 單元測試全部通過  
✅ Docker 整合正常  
✅ 安全性驗證通過（bcrypt、role checking）

可以繼續進行 Phase 3 的開發！
