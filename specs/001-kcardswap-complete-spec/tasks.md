# Tasks: 001 KCardSwap Complete Spec

## Phase 0: Setup
- [X] T001 初始化 mono-repo 目錄與工作流（apps/backend, gateway/kong, infra/db, specs, plans, tasks）
- [X] T002 建立 `.env` 與機密管理策略（本機 `.env`、CI/Prod 使用 Secret Manager）
- [X] T003 Docker Compose 一鍵啟動（Kong、Backend、Postgres、(可選)Nginx）路徑：`docker-compose.yml`
- [X] T004 Kong 宣告式設定與路由 `/api/v1/*` → backend 路徑：`gateway/kong/kong.yaml`
- [X] T005 CI/CD：lint/test/build、PR 檢查（GitHub Actions / GitLab CI）
- [X] T006 後端依賴管理遷移至 Poetry（pip → Poetry）
  - 詳細任務：`specs/copilot/modify-requirements-backend/tasks.md`（52 個子任務）
  - 實作計畫：`specs/copilot/modify-requirements-backend/plan.md`
  - 狀態：✅ Phase 1-6 完成（技術實作就緒），Phase 7 待完成（團隊培訓）
  - 影響範圍：開發環境、Docker、CI/CD、文件

## Phase 1: AUTH/PROFILE (P1)
- [X] T101 後端 Google OAuth 換 token 與使用者建立（`apps/backend/app/routers/auth.py`）
- [X] T102 JWT 生成/刷新/登出（access 15m, refresh 7d）（`apps/backend/app/services/auth.py`）
- [X] T103 Profile CRUD + 隱私設定（`apps/backend/app/routers/profile.py`）
- [X] T104 Kong 與後端 JWT 驗證串接（Kong jwt 插件預留、後端中介層）
- [X] T105 單元/整合測試：401/403/刷新流程、隱私旗標
  - [X] CT-Auth 契約測試：對齊 `contracts/auth/login.json`（成功/驗證失敗/未授權）

## Phase 2: CARD (P1)
- [ ] T201 Signed URL 服務：副檔名/大小驗證（`apps/backend/app/routers/cards.py`）
- [ ] T202 卡片 CRUD（image_url、thumb_url、屬性）（`apps/backend/app/routers/cards.py`）
- [ ] T203 縮圖產生管線（200x200；後端任務或 Cloud Function）（`apps/backend/app/services/images.py`）
- [ ] T204 上限檢查（每日數量/總容量/單張大小），錯誤碼 `422_LIMIT_EXCEEDED`
- [ ] T205 查詢與篩選（owner=me、filters、分頁）
- [ ] T206 測試：大小驗證、上限達成時的訊息與行為
  - [ ] CT-Cards 契約測試：對齊 `contracts/cards/create.json`（201/400/401）

## Phase 3: NEARBY (P1)
- [ ] T301 位置來源：最近一次上傳座標或明確定位（資料欄位與更新）
- [ ] T302 距離計算與排序（距離升序、付費優先）
- [ ] T303 隱身過濾（不出現在他人結果）
- [ ] T304 次數限制（免費 5 次/天、付費不限；Kong rate-limit 標籤）
- [ ] T305 測試：限次計數與重置、隱私正確性

## Phase 4: SOCIAL (P1)
- [ ] T401 好友邀請/接受/拒絕/封鎖（`apps/backend/app/routers/social.py`）
- [ ] T402 評分 API（交易完成後評分，公開評價匯總）（`apps/backend/app/routers/social.py`）
- [ ] T403 檢舉 API 與審查標記（`apps/backend/app/routers/social.py`）
- [ ] T404 測試：封鎖後的可見性與互動限制、檢舉累積邏輯

## Phase 5: CHAT (P1)
- [ ] T501 聊天室模型（`apps/backend/app/models/chat.py`）與訊息模型（`apps/backend/app/models/message.py`）
- [ ] T502 輪詢 API（`GET /api/v1/chats/{id}/messages?since=...`）
- [ ] T503 FCM 推播整合（背景通知導向聊天室）
- [ ] T504 訊息狀態：sent/delivered/read 的標示與回傳
- [ ] T505 測試：前景輪詢 3–5 秒、背景推播送達率

## Phase 6: TRADE (P1)
- [ ] T601 提案建立 API（`POST /api/v1/trades`）與資料表 `trade_items`
- [ ] T602 狀態機：draft → proposed → accepted → completed | rejected | canceled
- [ ] T603 完成鎖定（兩邊確認後，小卡狀態改為已交換）
- [ ] T604 交換歷史查詢與分頁
- [ ] T605 測試：狀態流轉、雙向完成條件
  - [ ] CT-Trade 契約測試：對齊 `contracts/trade/create.json`（201/409/401）

## Phase 7: BIZ (P2)
- [ ] T701 會員權限檢查中介層（每日新增/貼文/搜尋/容量/大小）
 - [ ] T702 Android 訂閱整合：Google Play Billing（用戶端購買流程）；後端僅收據驗證與升級/降級狀態同步
- [ ] T703 後台參數：每日貼文上限可配置（預設免費 2、付費不限）
- [ ] T704 測試：限額邏輯、過期自動降級
 - [ ] T705 訂閱收據驗證 API 與例外處理（重試、狀態回滾；退款由平台機制處理）

## Phase 8: API 標準與錯誤處理
- [ ] T801 統一錯誤格式與錯誤碼（400/401/403/404/409/422/429）
- [ ] T802 OpenAPI 規格檔（`apps/backend/openapi.yaml`）與文件站（FastAPI/Swagger 自動生成亦可）

## Phase 9: UI/UX
- [ ] T901 核心流程頁面：登入→完檔→上傳首卡→附近→好友/聊天→交換→評分
- [ ] T902 限制提示 UX（指出超限類型與下一步：隔日/升級/刪舊卡）
- [ ] T903 二次確認（送出交換、完成交換、送出檢舉）

## Phase 10: 資料庫與遷移 [UPDATED: 2025-12-15, 對應 FR-DB-004]
- [ ] T1001 [P] 配置 Alembic 環境 `apps/backend/alembic.ini` 和 `apps/backend/alembic/env.py`
- [ ] T1002 [P] 建立初始 migration：從 `infra/db/init.sql` 轉換所有 CREATE TABLE 至 `apps/backend/alembic/versions/001_initial_schema.py`
- [ ] T1003 [P] 建立索引 migration：從 `infra/db/init.sql` 轉換所有 CREATE INDEX 至 `apps/backend/alembic/versions/002_add_indexes.py`
- [ ] T1004 精簡 `infra/db/init.sql`：僅保留 CREATE DATABASE、CREATE EXTENSION、CREATE USER、GRANT 等資料庫級設定，移除所有 CREATE TABLE 和 CREATE INDEX
- [ ] T1005 驗證 migration 升級流程：執行 `alembic upgrade head` 確認所有表結構正確建立
- [ ] T1006 驗證 migration 降級流程：執行 `alembic downgrade base` 確認可完全回滾
- [ ] T1007 更新 Docker 初始化腳本 `apps/backend/Dockerfile` 或 `docker-compose.yml`：在應用啟動前執行 `alembic upgrade head`
- [ ] T1008 更新 testcontainers 整合測試設定：自動執行 Alembic migrations 在測試環境
- [ ] T1009 更新 CI/CD workflow `.github/workflows/test.yml`：新增 migration 升級/降級驗證步驟
- [ ] T1010 [P] 撰寫 migration 開發指南文件 `apps/backend/docs/database-migrations.md`：包含如何建立、測試、回滾 migration
- [ ] T1011 [P] Seed 資料腳本 `apps/backend/scripts/seed.py`：測試/開發環境用
- [ ] T1012 Query 優化與解說文件 `apps/backend/docs/query-optimization.md`
  - [ ] DM-001 整理 `specs/001-kcardswap-complete-spec/data-model.md`，與 Alembic migrations 對齊（含索引、外鍵、不變條件）

## Phase 11: 測試與品質
- [ ] T1101 單元測試覆蓋（>70% 核心模組）
- [ ] T1102 整合測試：Kong + Backend；JWT；Rate Limit；GCS 上傳
- [ ] T1103 E2E：User Story 1–6；SC-001..005 指標檢核
- [ ] T1104 性能與安全測試（延遲、吞吐、檔案型別白名單、濫用防護）

## Phase 12: 發佈與運維
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
- Integration-First Gate：先定義 `specs/001-kcardswap-complete-spec/contracts/` 並使用真實 DB/Gateway 進行整合測試；契約測試必備；路由回應需與契約 JSON 對齊。

## Acceptance Criteria Examples
- T204：超限時回傳 `422_LIMIT_EXCEEDED` 並包含哪一項超限訊息（每日/容量/大小）
- T304：免費使用者第 6 次附近搜尋回傳 `429_RATE_LIMITED`（或同策略），付費不受限
- T603：雙方都標記完成後，小卡狀態轉為已交換且不可再公開列表顯示

> 來源：`specs/001-kcardswap-complete-spec/plan.md` 與 `specs/001-kcardswap-complete-spec/spec.md`。

憲法參照：Constitution v1.2.0 Article VI（DDD 架構原則為唯一依據，避免在 Spec/Plan/Tasks 重複規範）。