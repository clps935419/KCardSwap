# Data Model（資料模型綜覽）

**更新日期**: 2025-12-18  
**對應版本**: Alembic migration 003 (add admin fields) + 後續擴展（見「未來擴展」）

## 目的

集中維護資料表、索引、關聯與不變條件，避免分散於多處文件。此文件與 Alembic migrations 保持同步，確保文件與實際資料庫結構一致。

## 來源與對應

- **Schema 定義來源**: `apps/backend/alembic/versions/` 中的 migration scripts
  - `001_initial_schema.py`: 所有表結構
  - `002_add_indexes.py`: 所有索引
  - `003_add_admin_fields.py`: 管理員認證欄位 (password_hash, role)
- **ORM 模型**: `apps/backend/app/infrastructure/database/models.py`
- **初始化腳本**: `infra/db/init.sql`（僅保留資料庫級設定：extensions, users, grants）

## 資料表總覽

### 1. users（使用者）

**用途**: 儲存 Google OAuth 認證使用者基本資訊

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 使用者唯一識別碼 |
| google_id | VARCHAR(255) | UNIQUE, NULLABLE | Google OAuth ID（管理員可為 NULL）|
| email | VARCHAR(255) | UNIQUE, NOT NULL | 電子郵件 |
| password_hash | VARCHAR(255) | NULLABLE | 密碼雜湊（僅管理員使用，bcrypt）|
| role | VARCHAR(20) | NOT NULL, DEFAULT 'user' | 角色：'user', 'admin', 'super_admin' |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引**:
- `idx_users_google_id` ON (google_id)
- `idx_users_email` ON (email)
- `idx_users_role` ON (role)

**關聯**:
- → profiles (1:1)
- → refresh_tokens (1:N)
- → subscriptions (1:N)
- → cards (1:N)

**不變條件**:
- email 必須正規化且小寫唯一
- 一般用戶：google_id NOT NULL, password_hash NULL, role='user'
- 管理員：password_hash NOT NULL, google_id 可為 NULL, role IN ('admin', 'super_admin')
- password_hash 必須使用 bcrypt 加密（成本因子 12 以上）
- role 必須為有效值之一：'user', 'admin', 'super_admin'

**Trigger**:
- `update_users_updated_at`: 自動更新 updated_at

---

### 2. profiles（個人檔案）

**用途**: 儲存使用者個人資訊與隱私設定

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Profile 唯一識別碼 |
| user_id | UUID | UNIQUE, NOT NULL, FK(users.id) ON DELETE CASCADE | 使用者 ID |
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

**索引**:
- `idx_profiles_user_id` ON (user_id)

**關聯**:
- users.id ← user_id (1:1)

**不變條件**:
- user_id 必須存在於 users 表中且唯一
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
- **縮圖為 Mobile 端本機衍生快取**：後端不產生/不儲存/不回傳任何 `thumb_*` / `thumbnail_*` 欄位
- size_bytes 與上傳限制由應用層依環境變數驗證（參見 `apps/backend/app/config.py`：`MAX_FILE_SIZE_MB`, `DAILY_UPLOAD_LIMIT_FREE`, `TOTAL_STORAGE_GB_FREE`）

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
- **003_add_admin_fields.py**: 管理員認證欄位 (password_hash, role)
- **004_add_profile_id.py**: 為 profiles 表添加獨立的 id 主鍵欄位

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

### subscription_purchase_tokens（訂閱收據/去重用）— Schema 草案（US6 / 待實作）

**目的**:
- 保存 Google Play purchase_token 與驗證結果摘要，提供：token 綁定、冪等、跨裝置 restore、以及稽核追蹤
- 避免「App 端僅以 UI 成功即升級」的風險：權限以後端 verify-receipt 驗證後更新為準

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 記錄唯一識別碼 |
| user_id | UUID | NOT NULL, FK(users.id) ON DELETE CASCADE | 綁定的使用者 |
| platform | VARCHAR(20) | NOT NULL | android（POC 僅 android） |
| purchase_token | TEXT | UNIQUE, NOT NULL | Google Play purchase token（不可跨 user 重放） |
| product_id | VARCHAR(120) | NOT NULL | 對應的訂閱商品 ID |
| purchase_time | TIMESTAMP WITH TIME ZONE | NULLABLE | 購買時間（若可取得） |
| expires_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 到期時間（由 server verify 結果寫入） |
| acknowledged_at | TIMESTAMP WITH TIME ZONE | NULLABLE | acknowledge 成功時間（POC 建議由後端寫入） |
| last_verified_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 最近一次後端驗證時間 |
| raw_payload | JSONB | NULLABLE | 原始驗證回應/必要欄位（可選，避免存敏感資訊過量） |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引/約束（建議）**:
- UNIQUE(purchase_token)
- `idx_subscription_purchase_tokens_user_id_created_at` ON (user_id, created_at DESC)

**不變條件（應用層 + DB 層）**:
- purchase_token 必須唯一且不可跨 user 綁定（防重放）
- 同 purchase_token 重送 verify-receipt 應回傳冪等結果（避免重複升級/寫入）
- entitlement 的 source of truth 為後端驗證結果（而非 App UI）

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
- **posts**: 城市/行政區佈告欄貼文（看板發文）
- **post_interests**: 對貼文表達「有興趣」的請求（作者接受後導流聊天/好友）

---

### trades（交換提案與歷史）— Schema 草案（US5 / 待實作）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 交換唯一識別碼 |
| initiator_id | UUID | NOT NULL, FK(users.id) | 發起者 |
| responder_id | UUID | NOT NULL, FK(users.id) | 接受/回應者 |
| status | VARCHAR(20) | NOT NULL | draft/proposed/accepted/completed/rejected/canceled |
| accepted_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 提案被接受時間（進入 accepted 的時間點） |
| initiator_confirmed_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 發起者標記「完成」時間 |
| responder_confirmed_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 回應者標記「完成」時間 |
| completed_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 兩邊都完成後的完成時間 |
| canceled_at | TIMESTAMP WITH TIME ZONE | NULLABLE | 取消時間（包含逾時自動取消） |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引（建議）**:
- `idx_trades_initiator_id_created_at` ON (initiator_id, created_at DESC)
- `idx_trades_responder_id_created_at` ON (responder_id, created_at DESC)
- `idx_trades_status_created_at` ON (status, created_at DESC)

**不變條件（應用層 + DB 層）**:
- status ∈ {draft, proposed, accepted, completed, rejected, canceled}
- completed_at 只能在 initiator_confirmed_at 與 responder_confirmed_at 皆有值時寫入
- status=completed 時 completed_at 必須有值

---

### trade_items（交換物品清單）— Schema 草案（US5 / 待實作）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 交換項目唯一識別碼 |
| trade_id | UUID | NOT NULL, FK(trades.id) ON DELETE CASCADE | 對應 trade |
| card_id | UUID | NOT NULL, FK(cards.id) | 對應小卡 |
| owner_side | VARCHAR(20) | NOT NULL | 此卡片由哪一方提供（initiator/responder） |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |

**索引/約束（建議）**:
- UNIQUE(trade_id, card_id)（避免同一 trade 重複加入同卡）

---

### ratings（評分記錄）— Schema 草案（US4/US5 / 待實作）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 評分唯一識別碼 |
| rater_id | UUID | NOT NULL, FK(users.id) | 評分者 |
| rated_user_id | UUID | NOT NULL, FK(users.id) | 被評分者 |
| trade_id | UUID | NULLABLE, FK(trades.id) | 若提供則代表此評分關聯某筆交換 |
| score | INTEGER | NOT NULL | 1–5 |
| comment | TEXT | NULLABLE | 可選文字回饋 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |

**索引/約束（建議）**:
- `idx_ratings_rated_user_id_created_at` ON (rated_user_id, created_at DESC)
- `idx_ratings_trade_id` ON (trade_id)
- UNIQUE(trade_id, rater_id)（trade_id 不為 NULL 時，確保同一筆 trade 每人最多評一次；可用 partial unique index）

**不變條件（應用層 + DB 層）**:
- score 必須在 1..5
- rater_id != rated_user_id
- 若提供 trade_id：trade 必須存在且 status=completed，且評分者/被評分者必須是該 trade 的兩位參與者
- 若未提供 trade_id：僅允許對「已成為好友」的對象評分（供 ratings 基礎能力；trade 完成後導流則應帶 trade_id）

---

### posts（佈告欄貼文）— Schema 草案（US7 / 待實作）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 貼文唯一識別碼 |
| owner_id | UUID | NOT NULL, FK(users.id) ON DELETE CASCADE | 作者 |
| city_code | VARCHAR(20) | NOT NULL | 城市代碼（例如 TPE） |
| district_code | VARCHAR(20) | NULLABLE | 行政區代碼（例如 Daan） |
| title | VARCHAR(120) | NOT NULL | 標題 |
| content | TEXT | NOT NULL | 內容（禁止精確地址/聯絡方式等個資） |
| idol | VARCHAR(100) | NULLABLE | 偶像名稱（篩選用） |
| idol_group | VARCHAR(100) | NULLABLE | 團體/團名（篩選用） |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'open' | 狀態：open/closed/expired/deleted |
| expires_at | TIMESTAMP WITH TIME ZONE | NOT NULL | 到期時間（預設 created_at + 14d） |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引（建議）**:
- `idx_posts_board_status_created_at` ON (city_code, district_code, status, created_at DESC)
- `idx_posts_owner_id` ON (owner_id)
- `idx_posts_idol` ON (idol)
- `idx_posts_idol_group` ON (idol_group)
- `idx_posts_expires_at` ON (expires_at)

**不變條件（應用層 + DB 層）**:
- status ∈ {open, closed, expired, deleted}
- expires_at > created_at
- city_code 必填；district_code 可選

---

### post_interests（貼文興趣請求）— Schema 草案（US7 / 待實作）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | 興趣請求唯一識別碼 |
| post_id | UUID | NOT NULL, FK(posts.id) ON DELETE CASCADE | 對應貼文 |
| user_id | UUID | NOT NULL, FK(users.id) ON DELETE CASCADE | 送出者 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | 狀態：pending/accepted/rejected |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | 更新時間 |

**索引/約束（建議）**:
- UNIQUE(post_id, user_id)（避免同一使用者重複送出）
- `idx_post_interests_post_id_created_at` ON (post_id, created_at DESC)
- `idx_post_interests_user_id_created_at` ON (user_id, created_at DESC)

**不變條件（應用層）**:
- 只有貼文作者可將 pending 變更為 accepted/rejected
- accepted 時需導流建立好友與聊天室（或若已存在則重用）

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
