# KCardSwap 技術規劃（Tech Plan）

本計劃對應 `specs/001-kcardswap-complete-spec/spec.md`，包含詳細的架構設計、API 規格、資料庫 Schema、前後端任務分解、限制與政策、測試策略、里程碑與風險控管。

## 0. 里程碑與時間線（POC → Beta）
- M0（Week 0）：專案初始化、基礎架構就緒（Kong、DB、GCS、CI）。
- M1（Week 1-2）：AUTH + PROFILE 完成（Google OAuth、JWT、個人檔案）。
- M2（Week 3-4）：CARD 上傳與管理完成（含上限檢查與縮圖）。
- M3（Week 5）：NEARBY 附近搜尋（距離計算、隱私、排序、次數限制）。
- M4（Week 6-7）：SOCIAL + CHAT（好友、評分、檢舉、輪詢 + 推播）。
- M5（Week 8）：TRADE（提案、狀態機、歷史）。
- M6（Week 9）：BIZ（免費/付費權限、容量與大小限制、升級/降級）。
- M7（Week 10）：E2E 測試與 Beta 封測（100–200 MAU）。

## 1. 架構與基礎設施
- 專案目錄：`apps/mobile`, `apps/backend`, `gateway/kong`, `infra/db`, `infra/gcs`, `infra/ci`。
- Kong Gateway（POC）：
	- 插件：JWT auth、Rate Limiting（依會員等級）、CORS、Request Size Limiter。
	- 路由前綴：`/api/v1/*` → upstream `apps/backend`。
- Nginx：作為前端資源與反向代理（如需）。
- PostgreSQL：部署與連線管理，使用 `pgcrypto`（如需 UUID/加密）。
- GCS：Bucket 結構：`kcardswap/cards/{user_id}/{card_id}.jpg`、`thumbs/{card_id}.jpg`。
- Secrets 管理：本地 `.env` + CI/Prod 使用 Secret Manager。
- CI/CD：GitHub Actions（lint/test/build，PR 檢查，main 部署）或 GitLab CI。

交付與驗收：
- 提供 `docker-compose.yml` 一鍵啟動網關、後端、DB。
- 提供 `Makefile`/npm scripts：`dev`, `test`, `lint`, `seed`。

## 2. 使用者認證與個人檔案（AUTH + PROFILE）
- API 規格：
	- `POST /api/v1/auth/google`：交換 auth code → 建立/登入 → 發 JWT。
	- `POST /api/v1/auth/refresh`：刷新 Access Token。
	- `POST /api/v1/auth/logout`：使 Refresh 失效。
	- `GET /api/v1/profile/me` / `PATCH /api/v1/profile/me`：檢視/更新個人檔案與隱私設定。
- 資料表：
	- `users(id, google_id, email, created_at)`
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
	- 免費：每日新增 3、單張 ≤2MB、總容量 ≤100MB。
	- 付費：每日新增不限（受總容量 ≤1GB）、單張 ≤5MB。
	- 失敗訊息：明確指出是「當日數量」或「總容量」超限。
- 資料表：
	- `cards(id, owner_id, idol, group, album, version, rarity, status, image_url, thumb_url, size_bytes, created_at, updated_at)`
	- `card_upload_stats(user_id, date, created_count)`
- 縮圖服務：後端任務或 Cloud Function 產生 `200x200`。
- 測試：
	- 上傳前大小驗證；達上限時的錯誤碼（`422_LIMIT_EXCEEDED`）。

## 4. 附近搜尋（NEARBY）
- API 規格：
	- `GET /api/v1/nearby?radius=1|5|10|all`：回傳距離與行政區。
- 算法與資料：
	- 使用者最近一次上傳座標（或明確定位）作為位置來源。
	- 排序：距離升序，同距離付費會員優先。
- 次數限制：
	- 免費：5 次/天；付費：不限（Kong Rate Limit 標籤）。
- 測試：
	- 隱身模式不出現在他人結果；限次計數與重置。

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
- OpenAPI 規格：在 `apps/backend/openapi.yaml` 維護；自動產生文件站。

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
	- [ ] 卡片 CRUD + 縮圖產生管線
	- [ ] 上限檢查（每日數量/總容量/單張大小）
- NEARBY
	- [ ] 距離計算與排序、隱身過濾
	- [ ] 次數限制與重置機制
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
- [ ] 好友列表與個人頁
- [ ] 聊天列表與聊天室（輪詢、推播導覽）
- [ ] 交換流程（提案、確認、歷史）
- [ ] 會員升級（方案頁、提示、權限變更）

## D. 資料庫與遷移
- [ ] 建立所有表與索引
- [ ] 撰寫 Seed 資料與遷移腳本
- [ ] Query 優化與解說文件

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
