# 初始化資料 (Init Data) 設計文件

## 概述

此專案實作了 **idempotent init data** 模式，確保資料庫遷移後能自動或手動初始化預設管理員帳號。

### 特點

- ✅ **Idempotent（冪等性）**：可重複執行，不會重複建立資料
- ✅ **彈性配置**：支援環境變數或命令列參數
- ✅ **自動化友善**：可整合至 CI/CD 和 Docker 啟動流程
- ✅ **安全**：密碼自動雜湊，支援隨機密碼生成

## 使用方式

### 方法 1: 手動執行（推薦用於開發）

```bash
cd apps/backend

# 使用預設值（會生成隨機密碼）
python scripts/init_admin.py

# 自訂 email 和密碼
python scripts/init_admin.py --email admin@example.com --password SecurePass123

# 建立 super_admin
python scripts/init_admin.py --email superadmin@example.com --password SecurePass123 --role super_admin

# 靜默模式（不輸出訊息）
python scripts/init_admin.py --quiet
```

### 方法 2: 透過環境變數

```bash
cd apps/backend

# 設定環境變數
export DEFAULT_ADMIN_EMAIL="admin@example.com"
export DEFAULT_ADMIN_PASSWORD="SecurePass123"
export DEFAULT_ADMIN_ROLE="admin"

# 執行腳本
python scripts/init_admin.py
```

### 方法 3: Docker 啟動時自動初始化

在 `docker-compose.yml` 或 `.env` 中設定：

```yaml
services:
  backend:
    environment:
      - INIT_DEFAULT_ADMIN=true
      - DEFAULT_ADMIN_EMAIL=admin@kcardswap.com
      - DEFAULT_ADMIN_PASSWORD=SecurePassword123
      - DEFAULT_ADMIN_ROLE=admin
```

或在 `.env` 檔案：

```bash
INIT_DEFAULT_ADMIN=true
DEFAULT_ADMIN_EMAIL=admin@kcardswap.com
DEFAULT_ADMIN_PASSWORD=SecurePassword123
DEFAULT_ADMIN_ROLE=admin
```

Docker 容器啟動時會自動：
1. 執行 `alembic upgrade head`
2. 執行 `python scripts/init_admin.py`（如果 `INIT_DEFAULT_ADMIN=true`）

### 方法 4: 在 Alembic Migration 中初始化

```bash
cd apps/backend

# 設定環境變數後執行 migration
INIT_DEFAULT_ADMIN=true \
DEFAULT_ADMIN_EMAIL=admin@example.com \
DEFAULT_ADMIN_PASSWORD=SecurePass123 \
alembic upgrade head
```

## 環境變數說明

| 變數名稱 | 說明 | 預設值 | 必填 |
|---------|------|--------|------|
| `INIT_DEFAULT_ADMIN` | 是否自動初始化（Docker/Migration） | `false` | 否 |
| `DEFAULT_ADMIN_EMAIL` | 管理員 email | `admin@kcardswap.local` | 否 |
| `DEFAULT_ADMIN_PASSWORD` | 管理員密碼 | 隨機生成 | **建議** |
| `DEFAULT_ADMIN_ROLE` | 管理員角色 (`admin`/`super_admin`) | `admin` | 否 |

## 行為說明

### Idempotent（冪等性）

- ✅ 如果 email 已存在，**跳過建立**，不會報錯
- ✅ 可以安全地重複執行
- ✅ 適合放在自動化部署流程中

範例輸出：

```bash
# 第一次執行
$ python scripts/init_admin.py --email admin@test.com --password test123
✅ Default admin user created successfully!
   Email: admin@test.com
   Role: admin
   User ID: 248c81fb-affb-4a7e-9f14-19864f6476bc

# 第二次執行（已存在）
$ python scripts/init_admin.py --email admin@test.com --password test123
ℹ️  Admin user 'admin@test.com' already exists (ID: 248c81fb-affb-4a7e-9f14-19864f6476bc)
   Role: admin
   Skipping creation.
```

## 整合範例

### 與 Makefile 整合

在 `Makefile` 中新增：

```makefile
.PHONY: init-admin
init-admin:
	cd apps/backend && python scripts/init_admin.py

.PHONY: init-admin-prod
init-admin-prod:
	cd apps/backend && \
	DEFAULT_ADMIN_EMAIL=$(ADMIN_EMAIL) \
	DEFAULT_ADMIN_PASSWORD=$(ADMIN_PASSWORD) \
	python scripts/init_admin.py
```

使用：

```bash
# 開發環境（隨機密碼）
make init-admin

# 生產環境（指定密碼）
ADMIN_EMAIL=admin@prod.com ADMIN_PASSWORD=secure123 make init-admin-prod
```

### CI/CD 流程

```yaml
# .github/workflows/deploy.yml
- name: Run Database Migrations
  run: |
    cd apps/backend
    alembic upgrade head

- name: Initialize Default Admin
  env:
    DEFAULT_ADMIN_EMAIL: ${{ secrets.ADMIN_EMAIL }}
    DEFAULT_ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
  run: |
    cd apps/backend
    python scripts/init_admin.py --quiet
```

### Kubernetes InitContainer

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: backend
spec:
  initContainers:
    - name: db-migrate
      image: backend:latest
      command:
        - /bin/sh
        - -c
        - |
          alembic upgrade head
          python scripts/init_admin.py --quiet
      env:
        - name: DEFAULT_ADMIN_EMAIL
          valueFrom:
            secretKeyRef:
              name: admin-secrets
              key: email
        - name: DEFAULT_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: admin-secrets
              key: password
```

## 安全考量

### ⚠️ 密碼管理

**不要將密碼寫在程式碼或版本控制中！**

建議做法：

1. **開發環境**：使用隨機生成的密碼
   ```bash
   python scripts/init_admin.py  # 會輸出生成的密碼
   ```

2. **測試環境**：使用環境變數
   ```bash
   DEFAULT_ADMIN_PASSWORD=test123 python scripts/init_admin.py
   ```

3. **生產環境**：使用 Secrets Management
   - Kubernetes Secrets
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - GCP Secret Manager

### 🔒 生產環境建議

```bash
# 1. 在 Secret Manager 中儲存密碼
# 2. 在部署時注入環境變數
# 3. 確保只有授權人員能存取 Secrets

# 範例：使用 AWS Secrets Manager
aws secretsmanager create-secret \
  --name kcardswap/admin-password \
  --secret-string "SecureRandomPassword123!"

# 在 ECS Task Definition 中引用
{
  "environment": [
    {
      "name": "DEFAULT_ADMIN_PASSWORD",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:kcardswap/admin-password"
    }
  ]
}
```

## 檔案結構

```
apps/backend/
├── alembic/
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_indexes.py
│       ├── 003_add_admin_fields.py
│       └── 004_init_default_admin.py      # 可選的資料 migration
├── scripts/
│   ├── create_admin.py                     # 手動建立管理員（任意 email）
│   ├── init_admin.py                       # 初始化預設管理員（idempotent）★
│   └── seed.py                             # 測試資料 seed
└── start.sh                                # Docker 啟動腳本（整合 init_admin）
```

## Migration vs Script 比較

| 功能 | Migration 004 | init_admin.py Script |
|------|---------------|----------------------|
| 執行時機 | `alembic upgrade head` | 手動或 Docker 啟動 |
| 需要環境變數 | `INIT_DEFAULT_ADMIN=true` | 無（但建議設定密碼） |
| 密碼處理 | 必須提供 | 可自動生成 |
| 適用場景 | 自動化 pipeline | 開發/運維手動操作 |
| 推薦用途 | ❌ 較複雜 | ✅ **推薦使用** |

**建議：優先使用 `init_admin.py` script**，更靈活且容易除錯。

## 常見問題 (FAQ)

### Q: 如果忘記管理員密碼怎麼辦？

A: 使用 `create_admin.py` 建立新的管理員或重設密碼：

```bash
# 方法 1: 建立新的管理員
python scripts/create_admin.py --email newadmin@example.com --password newpass123

# 方法 2: 直接在資料庫更新密碼（需要先產生 hash）
python -c "from app.shared.infrastructure.security.password_hasher import password_hasher; print(password_hasher.hash('newpassword'))"
# 然後在資料庫執行：
# UPDATE users SET password_hash='<hash>' WHERE email='admin@example.com';
```

### Q: 可以初始化多個管理員嗎？

A: `init_admin.py` 只初始化一個預設管理員。如需多個管理員：

```bash
# 建立額外的管理員
python scripts/create_admin.py --email admin1@example.com --password pass1
python scripts/create_admin.py --email admin2@example.com --password pass2
```

### Q: 在 production 環境建議哪種方式？

A: 推薦順序：

1. ✅ **Kubernetes Secrets + InitContainer**
2. ✅ **CI/CD Pipeline + Secrets Management**
3. ✅ **Docker Compose + .env（確保 .env 不在版本控制中）**
4. ⚠️ **手動執行**（適合小型部署）

### Q: 如何驗證管理員已建立？

```bash
# 方法 1: 查詢資料庫
psql -d kcardswap -c "SELECT id, email, role FROM users WHERE role IN ('admin', 'super_admin');"

# 方法 2: 嘗試登入
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@kcardswap.local", "password": "your-password"}'
```

## 下一步

現在您已了解 init data 設計，可以：

1. ✅ 在開發環境執行 `python scripts/init_admin.py` 建立管理員
2. ✅ 在 Docker Compose 中設定 `INIT_DEFAULT_ADMIN=true`
3. ✅ 將管理員密碼儲存在 Secret Manager 中
4. ✅ 更新 CI/CD pipeline 以自動初始化管理員
5. ✅ 查看 `PHASE-2.5-COMPLETE.md` 了解完整的 Admin 系統功能

## 相關文件

- `PHASE-2.5-COMPLETE.md` - Phase 2.5 完整說明
- `scripts/create_admin.py` - 手動建立任意管理員帳號
- `specs/001-kcardswap-complete-spec/contracts/auth/admin_login.json` - API 規格
- `apps/backend/docs/authentication.md` - 認證系統文件
