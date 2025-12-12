# Data Model（資料模型綜覽）

目的：集中維護資料表、索引、關聯與不變條件，避免分散於多處文件。

來源與對應：
- 以 `infra/db/init.sql` 為真實來源，本文提供可讀綜覽與設計理由。
- 若 SQL 變更，本文必須同步更新，並在 `plan.md` 標註影響範圍。

範例綱要（將隨實作逐步補齊）：
- users
  - PK: id (uuid)
  - 索引：email UNIQUE
  - 不變條件：email 正規化、小寫唯一；狀態列舉(active/suspended)
- cards
  - PK: id (uuid)
  - 外鍵：owner_id -> users.id
  - 索引：owner_id, (rarity, created_at)
  - 不變條件：rarity ∈ {common, rare, epic, legendary}
- trades
  - PK: id (uuid)
  - 外鍵：buyer_id, seller_id -> users.id
  - 索引：status, created_at
  - 不變條件：狀態流轉：`pending -> accepted|rejected -> settled`

接下來工作：
- 從 `infra/db/init.sql` 抽取實際表結構並補齊本文詳細段落與圖示。
