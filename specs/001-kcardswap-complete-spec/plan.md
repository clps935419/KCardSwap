# KCardSwap 技術規劃（Tech Plan）

更新說明（2025-12-12）：本計畫已同步最新規格說明，DDD 架構原則改以專案憲法的 Article VI 作為唯一依據。此處僅保留與本專案實作直接相關的目錄結構與服務切分，避免重複規範。

**API 描述（OpenAPI snapshot）**：本專案會把後端「已實作 API」的 OpenAPI 規格以 snapshot 形式提交到 repo，供檢視、SDK 生成與測試對齊使用；它是開發後產物，**不是開發前的合約**。
1) OpenAPI snapshot：openapi/openapi.json（由後端 FastAPI 自動生成後提交到 repo；用於檢視/SDK/驗證）
2) 資料模型綜覽：specs/001-kcardswap-complete-spec/data-model.md（與 infra/db/init.sql 對齊）

本計劃對應 `specs/001-kcardswap-complete-spec/spec.md`，包含詳細的架構設計、API 規格、資料庫 Schema、前後端任務分解、限制與政策、測試策略、里程碑與風險控管。

## 0. 里程碑與時間線（POC → Beta）
- M0（Week 0）：專案初始化、基礎架構就緒（Kong、DB、GCS、CI）。
- M1（Week 1-2）：AUTH + PROFILE 完成（Google OAuth、JWT、個人檔案）。
- M2（Week 3-4）：CARD 上傳與管理完成（含上限檢查與 Mobile-only 縮圖快取）。
- M3（Week 5）：NEARBY 附近搜尋（距離計算、隱私、排序、次數限制）。
- M3.5（Week 5-6）：POSTS 城市/行政區佈告欄（發文、看板列表、興趣請求、接受後導流聊天、到期/關閉）。
- M4（Week 6-7）：SOCIAL + CHAT（好友、評分、檢舉、輪詢 + 推播）。
- M5（Week 8）：TRADE（提案、狀態機、歷史）。
- M6（Week 9）：BIZ（免費/付費權限、容量與大小限制、升級/降級）。
- M7（Week 10）：E2E 測試與 Beta 封測（100–200 MAU）。

## 1. 架構與基礎設施
- **專案目錄結構**（**已更新 2025-12-15，採用 Modular DDD**）：
  - 頂層目錄：`apps/mobile`, `apps/backend`, `gateway/kong`, `infra/db`, `infra/gcs`, `infra/ci`
  - **後端模組化結構** (`apps/backend/app/`)：
    ```
    app/
    ├── main.py                 # 應用程式入口與路由聚合
    ├── container.py            # 全域依賴注入容器
    ├── modules/                # 業務模組核心（取代原有的 routers/services/ 分層）
    │   ├── identity/           # [Module] 認證與使用者管理（Auth + User）
    │   │   ├── domain/         # Entity, Value Objects, Repository Interfaces
    │   │   ├── application/    # Use Cases, DTOs
    │   │   ├── infrastructure/ # Repository Implementations, External Services
    │   │   ├── presentation/   # Routers, Schemas, Dependencies
    │   │   └── __init__.py
    │   │
	│   ├── social/             # [Module] 個人檔案與社交功能（Profile）
    │       ├── domain/
    │       ├── application/
    │       ├── infrastructure/
    │       ├── presentation/
    │       └── __init__.py
	│
	│   └── posts/              # [Module] 城市/行政區佈告欄貼文（Posts / Bulletin Board）
	│       ├── domain/
	│       ├── application/
	│       ├── infrastructure/
	│       ├── presentation/
	│       └── __init__.py
    │
    └── shared/                 # 共用核心（Shared Kernel）
        ├── domain/             # 共用 Value Objects (e.g., Email, UserId)
        ├── infrastructure/     # 資料庫連線、安全性工具、通用 Repository 基類
        ├── presentation/       # 通用中介軟體、例外處理器
        └── __init__.py
    ```
- 架構原則來源：Constitution v1.2.0 Article VI（四層架構 Domain/Application/Infrastructure/Presentation；Repository、CQRS、Domain Events、Value Objects）。
- **模組化設計原則**：
  - 每個業務模組（`identity`, `social`）包含完整的 DDD 四層架構
  - 模組間透過定義良好的介面（Use Cases / Domain Events）通訊
  - 禁止模組直接存取其他模組的 Infrastructure 或 Domain 層
  - 共用邏輯（如資料庫連線、JWT 處理）集中於 `shared/` 目錄
- **後端依賴管理**（**已更新 2025-12-11**）：
	- **工具**：Poetry（取代 pip + requirements.txt）
	- **配置檔**：pyproject.toml（專案元資料 + 依賴定義 + 工具配置）
	- **鎖定檔**：poetry.lock（確保版本一致性，必須納入版本控制）
	- **依賴分離**：生產依賴 `[tool.poetry.dependencies]` vs 開發依賴 `[tool.poetry.group.dev.dependencies]`
	- **優勢**：自動依賴解析、版本鎖定、現代化工具鏈、符合 PEP 518/517 標準
	- **向下相容**：可導出 requirements.txt 作為備援（`poetry export`）
	- **Docker 支援**：多階段構建，構建階段使用 Poetry，執行階段使用輕量 pip
	- **CI/CD 整合**：GitHub Actions 使用 snok/install-poetry action，快取 .venv 目錄
	- **詳細文件**：參見 `specs/copilot/modify-requirements-backend/`（plan.md, research.md, quickstart.md）
- **資料庫遷移管理**（**已更新 2025-12-15，對應 FR-DB-004**）：
	- **策略**：「遷移為王」—— 所有 schema 變更必須透過 Alembic migration 管理
	- **工具**：Alembic（已配置於 `apps/backend/`）
	- **配置檔**：`alembic.ini`、`alembic/env.py`、`alembic/versions/`
	- **init.sql 責任調整**：僅保留資料庫級設定（CREATE DATABASE、CREATE EXTENSION、CREATE USER/ROLE、GRANT 權限），所有 CREATE TABLE、ALTER TABLE、CREATE INDEX 移除
	- **初始化流程**：
		1. Docker 容器啟動時執行 `init.sql`（建立資料庫、擴展、用戶、權限）
		2. 後端應用啟動前執行 `alembic upgrade head`（建立所有表結構）
	- **開發流程**：
		- 新增/修改資料表：`alembic revision -m "描述"` → 編輯 migration script → `alembic upgrade head`
		- 回滾變更：`alembic downgrade -1` 或 `alembic downgrade <revision>`
		- 查看歷史：`alembic history`、`alembic current`
	- **版本控制**：所有 migration scripts 納入 Git，確保團隊同步
	- **測試環境**：testcontainers 自動執行 Alembic migrations
	- **CI/CD 檢查**：GitHub Actions 檢查 migration scripts 是否可正常升級/降級
	- **優勢**：
		- 消除 init.sql 與 ORM models 雙重維護的同步問題
		- Schema 版本可控、可追溯、可回滾
		- 開發/測試/生產環境 schema 一致性保證
		- 支援複雜 DDL 變更（如資料遷移、欄位重命名）
- Kong Gateway（POC）：
	- 插件：JWT auth、Rate Limiting（依會員等級）、CORS、Request Size Limiter。
	- 路由前綴：`/api/v1/*` → upstream `apps/backend`。
- Nginx：作為前端資源與反向代理（如需）。
- PostgreSQL：部署與連線管理，使用 `pgcrypto`（如需 UUID/加密）。
- GCS：Bucket 結構：`kcardswap/cards/{user_id}/{uuid}.jpg`（僅原圖；不建立 thumbs/；縮圖為 mobile 本機衍生快取）。
- Secrets 管理：本地 `.env` + CI/Prod 使用 Secret Manager。
- CI/CD：GitHub Actions（lint/test/build，PR 檢查，main 部署）或 GitLab CI。

一致性檢查（與憲法）：
- Domain 不依賴 FastAPI/SQLAlchemy；Infrastructure 實作 Repository；Routers 僅含驗證與序列化；Use Cases 不含 SQL/HTTP。

交付與驗收：
- 提供 `docker-compose.yml` 一鍵啟動網關、後端、DB。
- 提供 `Makefile`/npm scripts：`dev`, `test`, `lint`, `seed`。

## 2. 使用者認證與個人檔案（AUTH + PROFILE）
- API 規格：
	- `POST /api/v1/auth/google`：交換 auth code → 建立/登入 → 發 JWT。
	- **[ADDED: 2025-12-17]** `POST /api/v1/auth/admin-login`：管理員帳密登入（僅供後台，不對移動端開放）→ 發 JWT（包含 role）。
	- `POST /api/v1/auth/refresh`：刷新 Access Token。
	- `POST /api/v1/auth/logout`：使 Refresh 失效。
	- `GET /api/v1/profile/me` / `PATCH /api/v1/profile/me`：檢視/更新個人檔案與隱私設定。
- 資料表：
	- `users(id, google_id, email, password_hash, role, created_at, updated_at)`
		- **[UPDATED: 2025-12-17]** 新增 `password_hash VARCHAR(255) NULLABLE`（管理員使用 bcrypt）
		- **[UPDATED: 2025-12-17]** 新增 `role VARCHAR(20) DEFAULT 'user'`（'user', 'admin', 'super_admin'）
		- **[UPDATED: 2025-12-17]** `google_id` 改為 NULLABLE（允許純帳密管理員）
	- `profiles(user_id, nickname, avatar_url, bio, region, preferences, privacy_flags)`
	- `subscriptions(user_id, plan, started_at, expires_at, status)`
- 權限與驗證：
	- JWT（access 15m, refresh 7d）；Kong + backend 雙驗證。
	- 隱私旗標控制：附近可見、線上狀態、陌生人聊天。
- 測試：
	- 單元測試：token 流程、隱私設定 CRUD。
	- 整合測試：Kong 代理與後端協作，401/403/429。 

## 3. 小卡管理（CARD）
- API 規格：
	- `POST /api/v1/cards/upload-url`：回傳 GCS signed URL（驗副檔名/大小上限）。
	- `POST /api/v1/cards`：建立卡（包含圖片 URL、屬性）。
	- `GET /api/v1/cards?owner=me&filters=...`：查詢+分頁。
	- `PATCH /api/v1/cards/{id}` / `DELETE /api/v1/cards/{id}`。
- 上限與政策：
	- 免費：每日新增 2、單張 ≤10MB、總容量 ≤1GB。
	- 付費：每日新增不限（其他限制由應用層配置與驗證；以環境變數為準）。
	- 失敗訊息：明確指出是「當日數量」或「總容量」超限。
- 資料表：
	- `cards(id, owner_id, idol, group, album, version, rarity, status, image_url, size_bytes, created_at, updated_at)`
	- `card_upload_stats(user_id, date, created_count)`
- 縮圖策略：Mobile 端本機產生 `200x200` WebP 並快取（後端不產生/不儲存/不回傳縮圖）。
- Guardrails（硬性約束）：
	- 禁止縮圖欄位：所有 API request/response 不得出現任何 `thumb_*` / `thumbnail_*` 欄位（例如 `thumb_url`, `thumbnail_url`）。
	- 縮圖責任邊界：縮圖為 Mobile 端本機產生並本機快取；不上傳、不入後端 DB、後端不回傳。
	- 後端只負責原圖：後端僅提供原圖上傳 Signed URL 與配額/限制檢查；物件路徑僅允許 `cards/{user_id}/{uuid}.jpg`，禁止 `thumbs/`。
- 測試：
	- 上傳前大小驗證；達上限時的錯誤碼（`422_LIMIT_EXCEEDED`）。
	- 第三方整合測試分層：Unit/Integration 不打真實 GCS；僅 Staging/Nightly 以環境變數啟用少量真實 GCS Smoke（CORS/IAM/PUT 可用性）。

## 4. 附近搜尋（NEARBY）
- API 規格：
	- `PUT /api/v1/nearby/location`：上報目前使用者位置（寫入 profile 的 last_lat/last_lng）。
	- `POST /api/v1/nearby/search`：用座標搜尋附近小卡（距離排序、隱身排除、次數限制）。
- 算法與資料：
	- 位置來源：使用者主動上報位置（/nearby/location）與搜尋請求座標（/nearby/search）。
	- 排序：距離升序。
- 次數限制：
	- 免費：5 次/天。
	- 付費差異（premium unlimited / premium priority）：**deferred 至 Phase 8（BIZ）**。
- 測試：
	- 隱身模式不出現在他人結果；限次計數與重置。

使用流程（Mobile 建議）：
	1. 取得定位權限與座標。
	2. `PUT /api/v1/nearby/location` 上報位置（讓後端 profile.last_lat/last_lng 保持最新）。
	3. `POST /api/v1/nearby/search` 進行搜尋。
	4. 若回傳 HTTP 429（Too Many Requests）：顯示限次提示與升級入口（升級差異 deferred 至 Phase 8）。

## 5. 社交與好友（SOCIAL）
- API 規格：
	- `POST /api/v1/friends/{user_id}/invite`、`POST /api/v1/friends/{user_id}/accept`、`DELETE /api/v1/friends/{user_id}`。
	- `GET /api/v1/friends`：好友列表（暱稱、頭像、評分、完成次數、線上狀態）。
	- `POST /api/v1/reports`：檢舉；`POST /api/v1/ratings`：評分。
- 資料表：
	- `friendships(requester_id, accepter_id, status, created_at)`
	- `ratings(rater_id, target_id, trade_id, score, comment, created_at)`
	- `reports(reporter_id, target_id, reason, detail, created_at)`
- 政策與流程：
	- 檢舉累積觸發審查/暫停機制。

## 6. 聊天與訊息（CHAT）
- API 規格：
	- `GET /api/v1/chats`、`GET /api/v1/chats/{id}/messages?since=...`（輪詢）。
	- 推播：FCM 通知，背景喚醒導向聊天室。
- 資料表：
	- `chats(id, user_a, user_b, created_at)`
	- `messages(id, chat_id, sender_id, content, status, created_at)`
- 訊息狀態：sent/delivered/read；前端標示。
- 測試：
	- 前景輪詢 3–5 秒、背景推播到達率。

## 7. 交換流程（TRADE）
- API 規格：
	- `POST /api/v1/trades`（提案）
	- `PATCH /api/v1/trades/{id}`（狀態轉換：送出/接受/拒絕/取消/完成）
	- `GET /api/v1/trades/history`（分頁）
- 狀態機：draft → proposed → accepted → completed | rejected | canceled。
- 資料表：
	- `trades(id, a_id, b_id, status, created_at, completed_at)`
	- `trade_items(id, trade_id, card_id, owner_side)`
- 完成鎖定：兩邊確認後，關聯小卡狀態改為已交換。

## 8. 會員方案與權限（BIZ）
- 權限檢查中介層：依 `subscriptions.plan` 套用各項限制（每日新增、貼文、搜尋、容量/大小）。
 - 訂閱金流：以「Google Play Billing（Android）」為唯一訂閱支付方式；未來 iOS 採用「Apple In‑App Purchase（IAP）」規劃。後端僅負責「訂閱收據驗證」與狀態同步，不直接處理金流與退款。產品不支援卡片買賣或交易金流。需定義訂閱異常處理（重試、狀態回滾；退款流程由平台機制處理）。
- 降級邏輯：過期自動回免費；提示 UI。
- 後台參數：每日貼文上限可配置（預設免費 2、付費不限）。

## 9. API 標準與錯誤處理
- 統一格式：`{ data, error }`；錯誤例如：
	- `400_VALIDATION_FAILED`
	- `401_UNAUTHORIZED`
	- `403_FORBIDDEN`
	- `404_NOT_FOUND`
	- `409_CONFLICT`
	- `422_LIMIT_EXCEEDED`
	- `429_RATE_LIMITED`
- OpenAPI 規格：由後端 FastAPI 自動生成（Swagger/OpenAPI），並提交 snapshot 至 openapi/openapi.json 作為「已實作 API」的權威描述（用於檢視/SDK/測試對齊；非開發前契約）。

## 10. UI/UX 詳細規劃
- Flow：登入 → 完檔 → 上傳首卡 → 附近 → 好友/聊天 → 交換 → 評分。
- UX 規則：
	- 限制提示：明確指出超限類型與下一步（隔日/升級/刪舊卡）。
	- 二次確認：送出交換、完成交換、送出檢舉。
	- Loading/空狀態/錯誤視覺一致。

## 11. 測試策略與品質保障
- 單元測試：權限檢查、上限計數、狀態機、錯誤碼。
- 整合測試：Kong + Backend；JWT 驗證；Rate Limit；GCS 上傳流程。
- 端到端：關鍵 User Story 1–6；指標追蹤（SC-001..005）。
- 性能測試：聊天延遲、附近搜尋查詢時間、圖片上傳吞吐。
- 安全檢查：JWT 竄改、Rate Limit 避免濫用、檔案類型白名單。

Phase -1 Gates（依憲法）
- Simplicity Gate：專案數量 ≤3（mobile/backend/gateway）；避免過度設計，例外將記錄於本節。
- Anti-Abstraction Gate：優先使用框架原生能力，禁止不必要抽象層。
- Integration-First Gate：以 Swagger/OpenAPI（openapi/openapi.json）作為「已實作 API」的對齊基準；優先以真實 DB/Gateway 進行整合測試；路由實作與回應需與 OpenAPI 定義一致（成功/驗證失敗/未授權/衝突等）。

## 12. 風險與緩解
- 位置隱私爭議 → 預設不顯示精確地址、僅行政區與距離。
- 上傳濫用 → 檔案型別與大小驗證、Kong Request Size Limiter。
- 推播延遲 → 前景輪詢兜底、通知重試機制。
- 成本上升 → GCS 單價與容量政策可調，付費方案門檻保守。

---

# 任務分解（Tasks）

## A. 架構與環境
- [ ] 初始化 mono-repo 目錄與工作流
- [ ] Docker Compose：Kong、Backend、Postgres、(可選)Nginx
- [ ] Kong 路由與插件配置（JWT、Rate Limit、CORS）
- [ ] GCS Bucket 與服務帳號權限
- [ ] CI：lint/test/build、PR 檢查

## B. 後端 API（按模組）
- AUTH/PROFILE
	- [ ] Google OAuth 換 token 與使用者建立
	- [ ] JWT 生成/刷新/登出
	- [ ] Profile CRUD + 隱私設定
- CARD
	- [ ] Signed URL 服務 + 檔案型別/大小驗證
	- [ ] 卡片 CRUD（縮圖為 Mobile 端本機產生與快取；後端不產生/不儲存/不回傳縮圖）
	- [ ] 上限檢查（每日數量/總容量/單張大小）
- NEARBY
	- [ ] 距離計算與排序、隱身過濾
	- [ ] 次數限制與重置機制
- POSTS
	- [ ] 城市/行政區佈告欄貼文 CRUD（建立/列表/詳情/關閉/刪除）
	- [ ] 興趣請求流程（送出/清單/接受→建立好友+聊天室/拒絕）
	- [ ] 到期策略與下架（expired）
- SOCIAL
	- [ ] 好友邀請/接受/拒絕/封鎖
	- [ ] 評分/檢舉 API 與審查標記
- CHAT
	- [ ] 聊天室與訊息模型
	- [ ] 輪詢 API 與 FCM 推播整合
- TRADE
	- [ ] 提案建立與狀態機
	- [ ] 完成鎖定與歷史查詢
- BIZ
	- [ ] 會員權限檢查中介層
	- [ ] 訂閱金流介面（Play Billing/IAP）與升級/降級流程

## C. 前端（App）
- [ ] 登入/註冊/隱私設定頁
- [ ] 我的小卡（上傳、列表、編輯、刪除、過濾）
- [ ] 附近的人（權限、篩選、排序、次數提示）
- [ ] 城市/行政區佈告欄（列表、發文、詳情、我有興趣/作者接受導流聊天）
- [ ] 好友列表與個人頁
- [ ] 聊天列表與聊天室（輪詢、推播導覽）
- [ ] 交換流程（提案、確認、歷史）
- [ ] 會員升級（方案頁、提示、權限變更）

## D. 資料庫與遷移
- [ ] **[UPDATED: 2025-12-15]** 配置 Alembic 環境（alembic.ini、env.py）
- [ ] **[UPDATED: 2025-12-15]** 建立初始 migration：從現有 init.sql 轉換所有 CREATE TABLE、CREATE INDEX 至 Alembic migration script
- [ ] **[UPDATED: 2025-12-15]** 精簡 init.sql：僅保留 CREATE DATABASE、CREATE EXTENSION、CREATE USER、GRANT 等資料庫級設定
- [ ] **[UPDATED: 2025-12-15]** 驗證 migration 升級/降級流程：`alembic upgrade head` 和 `alembic downgrade base`
- [ ] **[UPDATED: 2025-12-15]** 更新 Docker 初始化流程：init.sql → alembic upgrade head
- [ ] **[UPDATED: 2025-12-15]** 更新 testcontainers 整合測試：自動執行 Alembic migrations
- [ ] **[UPDATED: 2025-12-15]** CI/CD 檢查：驗證 migration scripts 可正常執行
- [ ] 撰寫 Seed 資料腳本（測試/開發環境用）
- [ ] Query 優化與解說文件
- [ ] **[ADDED: 2025-12-15]** 撰寫 migration 開發指南文件（如何建立、測試、回滾 migration）

## E. 測試與品質
- [ ] 單元/整合測試用例覆蓋（>70% 核心模組）
- [ ] E2E 指標檢核（SC-001..005）
- [ ] 安全與限流測試案例

## F. 發佈與運維
- [ ] Beta 發佈腳本與環境變數管理
- [ ] 監控與日誌（API 響應、錯誤率、推播送達率）
- [ ] 事後分析報表（MAU、交換完成率、再次使用率）

---

> 本規劃依據 `specs/001-kcardswap-complete-spec/spec.md` 產生，可隨需求與發現持續細化。
