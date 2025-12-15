# Data Model（資料模型綜覽）

**更新日期**: 2025-12-15  
**對應版本**: Alembic migration 002 (add indexes)

## 目的

集中維護資料表、索引、關聯與不變條件，避免分散於多處文件。此文件與 Alembic migrations 保持同步，確保文件與實際資料庫結構一致。

## 來源與對應

- **Schema 定義來源**: `apps/backend/alembic/versions/` 中的 migration scripts
  - `001_initial_schema.py`: 所有表結構
  - `002_add_indexes.py`: 所有索引
- **ORM 模型**: `apps/backend/app/infrastructure/database/models.py`
- **初始化腳本**: `infra/db/init.sql`（僅保留資料庫級設定：extensions, users, grants）

## 資料表總覽

### 1. users（使用者）

**用途**: 儲存 Google OAuth 認證使用者基本資訊

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 使用者唯一識別碼 |
| google_id | VARCHAR(255) | UNIQUE, NOT NULL | Google OAuth ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 電子郵件 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引**:
- `idx_users_google_id` ON (google_id)
- `idx_users_email` ON (email)

**關聯**:
- → profiles (1:1)
- → refresh_tokens (1:N)
- → subscriptions (1:N)
- → cards (1:N)

**不變條件**:
- email 必須正規化且小寫唯一
- google_id 由 Google OAuth 提供，必須唯一

**Trigger**:
- `update_users_updated_at`: 自動更新 updated_at

---

### 2. profiles（個人檔案）

**用途**: 儲存使用者個人資訊與隱私設定

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| user_id | UUID | PK, FK(users.id) ON DELETE CASCADE | 使用者 ID |
| nickname | VARCHAR(100) | NULLABLE | 暱稱 |
| avatar_url | TEXT | NULLABLE | 頭像 URL |
| bio | TEXT | NULLABLE | 個人簡介 |
| region | VARCHAR(100) | NULLABLE | 地區 |
| preferences | JSONB | NULLABLE | 偏好設定 |
| privacy_flags | JSONB | DEFAULT (見下) | 隱私旗標 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**預設值**:
```json
privacy_flags: {
  "nearby_visible": true,
  "show_online": true,
  "allow_stranger_chat": true
}
```

**關聯**:
- users.id ← user_id (1:1)

**不變條件**:
- user_id 必須存在於 users 表中
- privacy_flags 必須包含三個布林鍵值

**Trigger**:
- `update_profiles_updated_at`: 自動更新 updated_at

---

### 3. subscriptions（訂閱）

**用途**: 儲存使用者會員方案資訊

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 訂閱唯一識別碼 |
| user_id | UUID | NOT NULL, FK(users.id) ON DELETE CASCADE | 使用者 ID |
| plan | VARCHAR(50) | NOT NULL, DEFAULT 'free' | 方案類型 |
| started_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 開始時間 |
| expires_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 到期時間 |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'inactive' | 狀態 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引**:
- `idx_subscriptions_user_id` ON (user_id)

**關聯**:
- users.id ← user_id (N:1)

**不變條件**:
- plan ∈ {free, premium} (應用層驗證)
- status ∈ {active, inactive, expired} (應用層驗證)
- active 訂閱必須有 started_at 和 expires_at

**Trigger**:
- `update_subscriptions_updated_at`: 自動更新 updated_at

---

### 4. refresh_tokens（刷新令牌）

**用途**: 儲存 JWT refresh tokens 用於身份驗證

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 令牌唯一識別碼 |
| user_id | UUID | NOT NULL, FK(users.id) ON DELETE CASCADE | 使用者 ID |
| token | VARCHAR(500) | UNIQUE, NOT NULL | Refresh token 值 |
| expires_at | TIMESTAMP WITH TIME ZONE | NOT NULL | 到期時間 |
| revoked | BOOLEAN | DEFAULT false | 是否已撤銷 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引**:
- `idx_refresh_tokens_user_id` ON (user_id)
- `idx_refresh_tokens_token` ON (token)

**關聯**:
- users.id ← user_id (N:1)

**不變條件**:
- token 必須唯一
- expires_at > created_at
- 過期或撤銷的 token 不可使用（應用層驗證）

**Trigger**:
- `update_refresh_tokens_updated_at`: 自動更新 updated_at

---

### 5. cards（小卡）

**用途**: 儲存使用者收藏的小卡資訊

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 小卡唯一識別碼 |
| owner_id | UUID | NOT NULL, FK(users.id) ON DELETE CASCADE | 擁有者 ID |
| idol | VARCHAR(100) | NULLABLE | 偶像名稱 |
| idol_group | VARCHAR(100) | NULLABLE | 偶像團體 |
| album | VARCHAR(100) | NULLABLE | 專輯名稱 |
| version | VARCHAR(100) | NULLABLE | 版本 |
| rarity | VARCHAR(50) | NULLABLE | 稀有度 |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'available' | 狀態 |
| image_url | TEXT | NULLABLE | 圖片 URL |
| thumb_url | TEXT | NULLABLE | 縮圖 URL |
| size_bytes | INTEGER | NULLABLE | 圖片大小（bytes）|
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引**:
- `idx_cards_owner_id` ON (owner_id)
- `idx_cards_status` ON (status)

**關聯**:
- users.id ← owner_id (N:1)

**不變條件**:
- rarity ∈ {common, rare, epic, legendary} (應用層驗證)
- status ∈ {available, trading, traded} (應用層驗證)
- size_bytes ≤ 5MB (5242880 bytes) for premium users
- size_bytes ≤ 2MB (2097152 bytes) for free users

**Trigger**:
- `update_cards_updated_at`: 自動更新 updated_at

---

## 資料庫函數與觸發器

### update_updated_at_column()

自動更新 `updated_at` 欄位的觸發器函數：

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

**應用於**:
- users
- profiles  
- cards
- subscriptions
- refresh_tokens

---

## 擴展（Extensions）

- **uuid-ossp**: UUID 生成函數（`uuid_generate_v4()`）

---

## Migration 管理

### 當前版本

- **001_initial_schema.py**: 建立所有表結構與觸發器
- **002_add_indexes.py**: 建立所有索引

### Schema 變更流程

1. 修改 ORM models (`app/infrastructure/database/models.py`)
2. 建立 migration: `alembic revision --autogenerate -m "描述"`
3. 檢視並編輯生成的 migration script
4. 測試 upgrade 和 downgrade
5. 提交 migration script 到版本控制
6. 更新此文件以反映變更

### 查詢當前 schema 版本

```bash
# 查看當前 migration 版本
poetry run alembic current

# 查看 migration 歷史
poetry run alembic history
```

---

## 未來擴展

以下是計劃中但尚未實作的表結構（Phase 2-6）:

### 待實作表

- **trades**: 交換提案與歷史
- **trade_items**: 交換物品清單
- **friendships**: 好友關係
- **blocks**: 封鎖名單
- **ratings**: 評分記錄
- **reports**: 檢舉記錄
- **chat_rooms**: 聊天室
- **messages**: 訊息記錄
- **notifications**: 推播通知記錄
- **card_upload_stats**: 上傳統計（用於限制檢查）

---

## 參考資料

- Migration 開發指南: `apps/backend/docs/database-migrations.md`
- Query 優化指南: `apps/backend/docs/query-optimization.md`
- SQLAlchemy ORM 模型: `apps/backend/app/infrastructure/database/models.py`
- Alembic migrations: `apps/backend/alembic/versions/`

---

**維護原則**: 
1. 此文件必須與 Alembic migrations 保持同步
2. Schema 變更必須先建立 migration，再更新此文件
3. 不變條件應在應用層和資料庫層雙重驗證
4. 所有索引必須有明確的查詢用途說明
