# Feature Specification: KCardSwap 完整產品規格

**Feature Branch**: `master`  
**Created**: 2025-12-10  
**Status**: Draft  
**Input**: User description: "/speckit.specify 讀取您的憲法文件（Constitution v1.2.0） 自動生成詳細的規格文件，包含以下 11 個核心部分：使用者認證與個人檔案、小卡管理功能、附近的人搜尋、社交功能、聊天與訊息系統、交換流程管理、商業模式細節、API 端點定義、資料庫 Schema、UI/UX 設計指南、城市/行政區佈告欄貼文"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Google 登入與完成基本個人檔案 (Priority: P1)

一般使用者第一次下載 App，使用 Google 帳號一鍵登入，系統自動建立帳號並引導填寫基本個人檔案（暱稱、偏好偶像、地區），完成後即可瀏覽小卡與交換列表。

**Why this priority**: 沒有順暢的註冊與登入流程，其他任何功能都無法使用，是整個產品的入口。

**Independent Test**: 僅實作此流程時，測試者可以從 0 安裝 App → 完成登入 → 看到首頁小卡列表，即可視為此 User Story 已可獨立驗收。

**Acceptance Scenarios**:

1. **Given** 使用者第一次開啟 App，**When** 點選「使用 Google 登入」並成功授權，**Then** 系統自動建立帳號並進入基本資料填寫畫面。
2. **Given** 使用者完成暱稱與地區填寫，**When** 點選「完成」，**Then** 回到首頁並能看到小卡列表，JWT token 已安全儲存在裝置端。

---

### User Story 2 - 上傳並管理個人小卡 (Priority: P1)

已登入使用者可以拍照或從相簿選擇小卡照片，系統自動壓縮後上傳至雲端，並輸入偶像、專輯、版本、稀有度等資訊。上傳完成後，小卡會顯示在個人卡冊中，可隨時編輯或下架。

**Why this priority**: 小卡資料是整個交換平台的核心資產，沒有穩定的小卡管理，其他搜尋與交換功能都失去意義。

**Independent Test**: 僅實作此流程時，測試者可以登入 → 上傳至少 1 張小卡 → 在「我的小卡」看到完整資訊並可編輯/刪除，即可通過驗收。

**Acceptance Scenarios**:

1. **Given** 使用者已登入且授權相機/相簿，**When** 拍攝或選擇一張圖片並填寫小卡資訊，**Then** 圖片成功壓縮並上傳，卡片顯示於個人卡冊。
2. **Given** 使用者已有已上傳小卡，**When** 編輯該卡片的備註或狀態（持有/欲交換），**Then** 更新結果立即反映在列表中。

---

### User Story 3 - 搜尋附近可以交換的小卡 (Priority: P1)

使用者開啟「附近的人」功能並授權定位後，系統根據使用者位置顯示一定半徑內也在尋找交換的其他使用者，列表會顯示距離、可交換小卡數量與評分。

**Why this priority**: 面對面交換是此產品的核心價值，附近搜尋是關鍵觸發點。

**Independent Test**: 僅實作此流程時，可在兩台裝置上分別登入、開啟定位，確認彼此會出現在對方的附近列表內，即可視為可獨立驗收。

**Acceptance Scenarios**:

1. **Given** 使用者已授權定位，**When** 開啟「附近的人」頁面並選擇 5km 篩選，**Then** 顯示 5km 內的可交換對象，並顯示大約距離與可交換卡片數。
2. **Given** 使用者啟用「隱身模式」，**When** 其他使用者執行附近搜尋，**Then** 隱身使用者不會出現在搜尋結果中。

---

### User Story 4 - 建立好友關係與聊天協商交換 (Priority: P1)

使用者在瀏覽他人小卡或附近使用者時，可以送出好友邀請；成為好友後，雙方可以在一對一聊天室內協商交換細節，系統透過短輪詢與推播確保訊息即時性。

**Why this priority**: 交換前的溝通是必要步驟，沒有穩定聊天與好友機制，難以建立信任與安排見面。

**Independent Test**: 僅實作此流程時，可在兩個帳號互相加好友 → 開啟聊天室 → 互傳訊息，驗證輪詢與推播通知是否正常。

**Acceptance Scenarios**:

1. **Given** 使用者 A 瀏覽使用者 B 的小卡，**When** 點選「加好友」並由 B 接受邀請，**Then** 雙方出現在彼此好友列表中，並自動建立一個聊天室。
2. **Given** 雙方已在聊天室中互傳訊息，**When** 其中一方離開聊天畫面但 App 仍於前景，**Then** 系統每 3–5 秒輪詢新訊息並更新畫面。
3. **Given** App 在背景或關閉狀態，**When** 收到新訊息，**Then** 會透過 FCM 推播通知提醒使用者。

---

### User Story 5 - 建立並完成一次交換流程 (Priority: P1)

兩位使用者在聊天中選定各自提供的小卡，使用者 A 發送交換提案，使用者 B 確認後雙方線下見面完成交換，回到 App 中標記「交換完成」並互相給予評分。

**Why this priority**: 交換流程直接對應到產品最核心的價值主張，必須被完整追蹤與記錄。

**Independent Test**: 僅實作此流程時，可由兩個帳號選定卡片 → 建立提案 → 接受 → 標記完成 → 各自的交換歷史中出現紀錄，即可通過驗收。

**Acceptance Scenarios**:

1. **Given** 雙方已是好友且各自有可交換的小卡，**When** A 在聊天中選擇「發起交換」，**Then** 可以選擇自己與對方的卡片組合送出提案。
2. **Given** B 收到交換提案，**When** 點選「接受」並在見面後雙方都按下「交換完成」，**Then** 產生一筆交換紀錄並可在歷史中查看。
3. **Given** 交換完成後，**When** 任一方提交 1–5 星評分與文字回饋，**Then** 該評分會累積到對方的信譽分數中。

  - 補充規則：評分必須對應一筆「已完成（completed）」的交換，且每位參與者對同一筆 completed trade 最多只能評分一次。

---

### User Story 6 - 免費/付費會員差異體驗 (Priority: P2)

免費會員可以有限度地上傳小卡、發布交換貼文與附近搜尋；升級為付費會員後，各項限制解除並獲得進階篩選與優先排序等權益。

**Why this priority**: 這是營收關鍵環節，必須明確定義限制與升級後的體驗差異。

**Independent Test**: 僅實作此流程時，可建立一個免費帳號與一個付費帳號，比較每日上傳次數、附近搜尋次數與搜尋排序差異。

**Acceptance Scenarios**:

1. **Given** 使用者為免費會員，**When** 當日已上傳第 3 張小卡後再次嘗試上傳，**Then** 系統阻擋並顯示需隔日或升級付費的提示。
2. **Given** 使用者升級為付費會員，**When** 再次嘗試上傳或附近搜尋，**Then** 當日不再受原有限制，且在搜尋結果中具有優先排序。

---

### User Story 7 - 城市/行政區佈告欄發起交換貼文 (Priority: P2)

使用者可以在指定城市/行政區的「佈告欄」發起交換貼文（例如「我在台北市大安區，想換某偶像版本」），吸引同城市或附近地區的人互相聯絡交換。貼文可設定到期時間；其他使用者可對貼文表達「有興趣」，貼文作者接受後系統建立好友關係並建立一對一聊天室供協商交換。

**Why this priority**: 這是以地點為核心的增量獲客/促成交換場景，能補足「僅好友內交換」的不足，但可在既有 AUTH/SOCIAL/CHAT 基礎上循序加入，屬 P2。

**Independent Test**: 僅實作此流程時，測試者可以 A 建立台北市佈告欄貼文 → B 在台北市佈告欄看到並點選「有興趣」→ A 接受後自動建立聊天室 → 雙方可互傳訊息，即可視為可獨立驗收。

**Acceptance Scenarios**:

1. **Given** 使用者已登入，**When** 在「台北市/大安區」佈告欄建立貼文並設定 14 天到期，**Then** 貼文出現在該城市/行政區佈告欄列表中，且不顯示精確地址。
2. **Given** 使用者位於台北市，**When** 開啟佈告欄並以偶像/團體篩選，**Then** 可看到符合條件的貼文列表，並可查看貼文詳情。
3. **Given** 使用者 B 對貼文點選「有興趣」，**When** 貼文作者 A 接受該興趣請求，**Then** 系統建立 A 與 B 的好友關係並建立一對一聊天室，雙方可在聊天室內協商交換。
4. **Given** 貼文已到期或作者手動關閉，**When** 其他使用者瀏覽佈告欄，**Then** 該貼文不再出現在預設列表中。

---

### Edge Cases

- 使用者拒絕提供定位權限時，附近搜尋該如何降級顯示（例如僅顯示城市層級熱門交換）？
- 網路不穩或圖片上傳中斷時，是否提供重新上傳與中斷續傳機制？
- 聊天輪詢 API 長時間無回應或多次失敗時，前端應如何顯示錯誤與重試機制？
- 交換提案被多次反悔或修改時，如何避免狀態錯亂與衝突？
- 使用者遭多次檢舉但未明顯違規時，信譽與封鎖策略應如何平衡？

---

## Requirements *(mandatory)*

### Functional Requirements

以下以 11 個核心主題分組定義功能需求，每一條皆應可被測試驗證。

#### 1. 使用者認證與個人檔案（Google OAuth、管理員登入、JWT、隱私設定）

- **FR-AUTH-001**：系統必須支援使用者透過 Google OAuth 完成首次登入與帳號建立。
- **[ADDED: 2025-12-17] FR-AUTH-001-ADMIN**：系統必須支援管理員透過帳號密碼登入（僅供後台管理使用，不對移動端開放）。管理員帳號需包含 email、password_hash（bcrypt 加密）與 role（admin/super_admin），登入成功後返回與 Google OAuth 相同格式的 JWT tokens。**Why**: 管理員需要獨立的認證方式以進行後台管理操作，不依賴第三方 OAuth 服務。**Acceptance Scenarios**: (1) 管理員可透過 POST /api/v1/auth/admin-login 使用 email + password 登入，返回 access_token、refresh_token 與 role 資訊。(2) 非管理員角色（role='user'）無法透過此 endpoint 登入，返回 401 錯誤。
- **FR-AUTH-002**：系統必須在成功登入後簽發存活時間 15 分鐘的 Access Token 與 7 天的 Refresh Token，並於 API Gateway（Kong）與後端共同驗證。
- **FR-AUTH-003**：行動 App 必須將 JWT 資訊安全儲存在安全儲存區（例如 expo-secure-store），不得以明文存在一般 AsyncStorage。
- **FR-AUTH-004**：使用者必須能在個人檔案頁面檢視與編輯暱稱、頭像、偏好偶像、簡介與所在區域（不顯示精確地址）。
- **FR-AUTH-005**：系統必須提供「隱私設定」讓使用者可控制：是否可被附近搜尋找到、是否顯示線上狀態、是否允許陌生人發起聊天。
- **FR-AUTH-006**：使用者必須能在任何時間登出，登出後本機 JWT 必須被清除且之後的 API 呼叫一律當作未登入處理。
- **[ADDED: 2025-12-17] FR-AUTH-007**：系統必須支援三種使用者角色（user、admin、super_admin），並在 JWT payload 中包含 role 資訊。需保護的 API endpoint 應根據 role 進行權限檢查。**Why**: 提供最小權限原則與管理職責分離，確保敏感操作僅限特定角色存取。**Acceptance Scenarios**: (1) 一般用戶（role='user'）無法存取管理員專用 API。(2) admin 可管理內容與用戶，但無法管理其他 admin。(3) super_admin 擁有最高權限，可管理所有 admin 與系統設定。

#### 2. 小卡管理功能（資料模型、上傳流程、驗證、篩選）

- **FR-CARD-001**：每張小卡資料至少必須包含：擁有者 user_id、偶像名稱、團體/團名、專輯名稱、版本/序號、稀有度、狀態（持有/欲交換/已交換）、圖片 URL（原圖）、建立時間與最後更新時間。
- **FR-CARD-002**：上傳流程必須支援相機拍攝與相簿選擇兩種來源，並在客戶端先行壓縮圖片以符合會員方案大小限制。
- **FR-CARD-003**：後端在產生 GCS signed URL 前必須再次驗證檔案類型與預期大小上限，拒絕非圖片或超出上限的請求。
- **FR-CARD-004**：Mobile 端必須為每張小卡在本機產生縮圖（例如 200x200 WebP）並在列表畫面優先載入本機縮圖快取，以節省頻寬與加快載入；後端不得產生/儲存/回傳任何縮圖 URL 或縮圖相關欄位。
- **FR-CARD-005**：使用者必須能在「我的小卡」中依偶像、專輯、稀有度、狀態進行篩選與排序。
- **FR-CARD-006**：當小卡標記為「已交換」後，預設不得再出現在公開交換列表與附近搜尋中，但仍可在個人歷史中檢視。

#### 3. 附近的人搜尋（地理位置邏輯、距離篩選、隱私模式）

- **FR-NEARBY-001**：系統必須支援使用者選擇距離篩選（1km / 5km / 10km / 全部），並根據使用者最近一次上傳的位置座標計算距離。
- **FR-NEARBY-002**：搜尋結果中不得顯示精確地址或精準座標，只能顯示大約距離與行政區資訊（例如「台北市大安區」）。
- **FR-NEARBY-003**：啟用「隱身模式」的使用者不得出現在其他人的附近搜尋結果中，但仍可主動搜尋別人。
- **FR-NEARBY-004**：附近搜尋結果預設依距離由近到遠排序，付費會員在相同條件下應優先顯示於列表較前方。
- **FR-NEARBY-005**：系統必須對單一使用者的附近搜尋次數依會員等級套用每日限制（免費 5 次/天，付費不限）。

#### 4. 社交功能（好友系統、評分機制、檢舉機制）

- **FR-SOCIAL-001**：使用者必須能向其他使用者送出好友邀請，對方可以選擇接受或拒絕；僅雙方皆同意時建立好友關係。
- **FR-SOCIAL-002**：好友列表應顯示暱稱、頭像、評分平均、完成交換次數與線上狀態（若對方允許顯示）。
- **FR-SOCIAL-003**：每次交換完成後，雙方必須被引導進行 1–5 星評分與可選文字回饋，系統需累積成使用者公開評價。
- **FR-SOCIAL-003A**：系統必須提供 ratings 的基礎能力（建立與查詢），並進行基本驗證：
  - 建立評分：`POST /api/v1/ratings`（1–5 星 + 可選文字回饋）。
  - 查詢評分：需能查詢某使用者收到的評分與平均分數（供好友列表/個人頁顯示）。
  - 基本驗證：評分者不得評分自己；分數必須在 1–5；若任一方互相封鎖則不得評分。
  - 權限規則（擇一滿足即可）：(1) 兩者為已成為好友；或 (2) 提供 trade_id 且該 trade 與雙方關聯。
- **FR-SOCIAL-003B**：交換完成後的流程整合與限制（與交換流程聯動）：
  - 僅允許對「已完成（completed）」的 trade 進行評分（trade_id 必須指向 completed trade）。
  - 每位參與者對同一筆 completed trade 最多只能評分一次（避免重複刷分）。
  - 前端在 trade 完成後必須顯示「去評分」入口/引導（對齊 User Story 5）。
- **FR-SOCIAL-004**：使用者可以對涉嫌詐騙、騷擾或假卡的帳號進行檢舉；檢舉內容需包含原因類別與可選文字說明。
- **FR-SOCIAL-005**：系統必須提供封鎖功能，被封鎖者不得再發起聊天、好友邀請或在附近搜尋中看到封鎖人。
- **FR-SOCIAL-006**：對同一帳號累積多次重大檢舉時，系統必須標記為待審查狀態，並可以根據管理政策暫時停權。

#### 5. 聊天與訊息系統（輪詢時機、FCM 整合、訊息狀態）

- **FR-CHAT-001**：每一對好友必須有一個唯一的一對一聊天室，歷史訊息需持久化儲存於資料庫中。
- **FR-CHAT-002**：當使用者停留在特定聊天室畫面前景時，App 必須每 3–5 秒呼叫輪詢 API 取得新訊息，並以 `after_message_id`（最後已接收的 message_id）做增量載入。
- **FR-CHAT-003**：當 App 在背景或關閉狀態時，新的訊息必須透過 FCM 推播通知傳遞，點擊通知應導向對應聊天室。
- **FR-CHAT-004**：訊息需支援至少三種狀態：已發送（送達伺服器）、已送達（送至對方裝置）、已讀（對方開啟聊天室並看過），並在 UI 中以簡單標記呈現。
- **FR-CHAT-005**：系統必須限制單則訊息最大長度，避免惡意刷頻與影響儲存效能；過長訊息需在前端即時提示並阻止送出。
- **[ADDED: 2025-12-21] FR-CHAT-006**：系統必須定義訊息保留政策：聊天訊息在伺服器端保留 30 天；超過 30 天的訊息可由後端清除。清除排程/清理 job 的實作 **deferred**。

#### 6. 交換流程管理（提案狀態機、面對面確認、歷史記錄）

- **FR-TRADE-001**：交換提案必須包含雙方提供的小卡清單、建立者、目前狀態（草稿/已送出/已接受/已拒絕/已取消/已完成）與時間戳。
- **FR-TRADE-002**：系統必須限制同一對使用者在任一時間最多存在有限數量的「進行中」交換提案，以避免混亂。
- **FR-TRADE-003**：雙方在面對面完成交換後，必須各自獨立標記「交換完成」，僅當兩邊都確認時，狀態才轉為已完成並鎖定相關小卡為已交換狀態。
- **FR-TRADE-004**：所有交換紀錄必須可在「交換歷史」頁面依時間排序檢視，並保留對應的評分與回饋內容。
- **FR-TRADE-005**：交換提案進入「已接受（accepted）」後，若在可配置的時間窗內（預設 48 小時；由 `TRADE_CONFIRMATION_TIMEOUT_HOURS` 控制）仍未完成「雙方都確認完成」，系統必須將該 trade 標記為 **canceled**（不新增 `expired` 狀態）。

#### 7. 商業模式細節（免費/付費限制、計費、升級邏輯）

- **FR-BIZ-001**：免費會員的資源限制至少包含：每日新增小卡上限 3 張（新增至個人卡冊）、每日發佈交換貼文上限 2 則、附近搜尋次數限制依 FR-NEARBY-005 定義、卡冊圖片總容量上限 100MB、單張小卡圖片最大 2MB。系統在任一項超額時，必須阻擋請求並給出明確且可理解的提示訊息。
- **FR-BIZ-002**：付費會員方案（例如 NT$ 99/月、NT$ 990/年）必須解除每日新增小卡數與每日交換貼文數的限制，附近搜尋次數依 FR-NEARBY-005 定義為不限，同時將卡冊圖片總容量上限提升至 1GB、單張小卡圖片最大 5MB；當達到總容量上限時，使用者需刪除舊卡或調整方案後才能再新增。
- **FR-BIZ-003**：系統必須記錄每個會員方案的起始與到期時間，過期後自動降回免費會員權限。
- **FR-BIZ-004**：升級與續訂流程需整合適當的金流（未在此規格細化具體金流供應商），並提供失敗重試與退款例外處理流程。
 - **FR-BIZ-004**：升級與續訂流程在 Android 採「Google Play Billing」；iOS 次階段採「Apple IAP」。後端僅負責訂閱收據驗證與 `subscriptions` 狀態同步（生效/過期/取消），退款由平台機制處理。需提供失敗重試與狀態回滾例外處理流程。

##### 免費 vs 付費會員資源限制一覽

| 項目 | 免費會員 | 付費會員 |
| --- | --- | --- |
| 每日卡冊新增張數 | 3 張/天 | 不限（受總容量限制） |
| 卡冊圖片總容量 | 100MB | 1GB |
| 單張小卡最大檔案大小 | 2MB | 5MB |
| 每日交換貼文上限 | 2 則/天（數值可由營運後台調整） | 不限（數值可由營運後台調整） |
| 每日附近搜尋次數 | 5 次/天 | 不限 |

#### 8. API 端點定義（完整 RESTful API、請求/回應範例、錯誤碼）

- **FR-API-001**：所有對外後端服務必須透過 `/api/v1/...` 路徑，由 Kong Gateway 統一代理與套用 JWT 驗證、Rate Limiting、CORS 等策略。
- **FR-API-002**：每個主要資源（users、cards、trades、chats、subscriptions）必須具備清楚的 RESTful 端點與對應 HTTP 動詞（GET/POST/PATCH/DELETE）。
**FR-API-002-TRADE**：Trade 相關端點至少必須包含：
  - `POST /api/v1/trades`（建立交換提案）
  - `POST /api/v1/trades/{id}/accept`（接受提案）
  - `POST /api/v1/trades/{id}/reject`（拒絕提案）
  - `POST /api/v1/trades/{id}/cancel`（取消提案）
  - `POST /api/v1/trades/{id}/complete`（我方標記完成；雙方皆完成後轉 completed）
  - `GET /api/v1/trades/history`（交換歷史查詢，分頁）
- **FR-API-003**：所有 API 回應需採用一致格式（例如 `{ "data": ..., "error": null }` 或 `{ "data": null, "error": { code, message } }`）。
- **FR-API-004**：系統必須定義標準錯誤碼集合（例如 400_xxx 驗證錯誤、401_xxx 未授權、403_xxx 權限不足、404_xxx 資源不存在、429_xxx 超出限流）。

#### 9. 資料庫 Schema（所有資料表、關聯、索引）

- **FR-DB-001**：資料庫必須至少包含 users、profiles、cards、trades、trade_items、chats、messages、friendships、ratings、reports、subscriptions 等主要資料表。
- **FR-DB-002**：所有外鍵關聯必須明確定義並採用適當的刪除/更新策略（例如交易歷史不可因使用者刪除而消失）。
- **FR-DB-003**：常用查詢條件（例如依 user_id 查 cards、依 chat_id 查 messages、依地理區域查 users）必須建立適當索引以確保效能。
- **[ADDED: 2025-12-15] FR-DB-004**：所有資料庫 schema 變更（CREATE TABLE、ALTER TABLE、CREATE INDEX 等）必須透過 Alembic migration 管理，init.sql 僅保留資料庫級設定（擴展、函數、權限），確保 schema 版本可控且可回滾。**Why**: 採用「遷移為王」策略，確保開發/測試/生產環境 schema 一致性，避免 init.sql 與 ORM models 雙重維護造成的同步問題。**Acceptance Scenarios**: (1) 當需要新增或修改資料表結構時，開發者建立 Alembic migration script，執行 `alembic upgrade head` 後 schema 變更生效，且可透過 `alembic downgrade` 回滾。(2) 當 Docker 環境首次啟動時，執行 init.sql 與 Alembic migrations 後，init.sql 僅建立資料庫/用戶/擴展，所有表結構由 migration 產生。

#### 10. UI/UX 設計指南（畫面流程、元件規格、互動設計）

- **FR-UX-001**：產品必須提供從登入 → 完成個人檔案 → 上傳首張小卡 → 瀏覽附近使用者 → 發起交換 → 完成評分的導覽流程，並以清楚的步驟提示完成。
- **FR-UX-002**：主要畫面（首頁小卡列表、附近的人、聊天列表與聊天室、我的小卡、交換歷史）需採用一致的底部導覽或 tab 結構，降低學習成本。
- **FR-UX-003**：所有重要動作（送出交換提案、確認交換完成、送出檢舉）需有二次確認或明顯提示，避免誤觸。
- **FR-UX-004**：列表類畫面須支援下拉更新與分頁/無限卷動，以兼顧效能與使用體驗。

#### 11. 城市/行政區佈告欄貼文（POSTS）

- **FR-POST-001**：系統必須允許使用者在指定城市/行政區建立佈告欄貼文，貼文至少包含：作者 user_id、城市/行政區、標題、內容、狀態（open/closed/expired/deleted）、到期時間、建立/更新時間。
- **FR-POST-002**：系統必須提供以城市為主的佈告欄列表，並可選擇行政區篩選；列表需支援分頁且預設依建立時間由新到舊排序。
- **FR-POST-003**：貼文不得要求或顯示精確地址與精準座標；內容若包含疑似個資（電話、地址格式）應在前端提示並阻止送出，後端亦應進行基本驗證。
- **FR-POST-004**：佈告欄列表必須支援至少以下篩選：偶像名稱、團體/團名、狀態（預設僅 open）。
- **FR-POST-005**：非作者使用者必須能對 open 貼文表達「有興趣」；作者必須能檢視有興趣清單並接受/拒絕。
- **FR-POST-006**：當作者接受某個「有興趣」請求時，系統必須建立雙方好友關係並建立一對一聊天室，供後續協商交換；若雙方已是好友且聊天室存在，則直接導向該聊天室。
- **FR-POST-007**：作者必須能手動關閉貼文（closed）；貼文到期後系統必須自動標記為 expired，且不應出現在預設列表中。
- **FR-POST-008**：貼文建立必須套用會員等級的每日發文限制：免費 2 則/天、付費不限（對齊 FR-BIZ-001/FR-BIZ-002）；超額時回傳一致的錯誤格式與適當錯誤碼（建議 422_LIMIT_EXCEEDED）。
- **FR-POST-009**：系統必須支援對貼文進行檢舉（沿用 reports 機制）；管理員可將違規貼文下架（deleted）並保留稽核痕跡。
- **FR-POST-010**：當貼文收到「有興趣」或被接受/拒絕時，系統應提供通知機制（前景輪詢兜底、背景推播整合於 FR-CHAT-003）。

---

### Key Entities *(include if feature involves data)*

- **User**：代表平台使用者帳號，包含登入識別（Google OAuth ID）、基本資料（暱稱、頭像、地區）、會員等級與帳號狀態。
- **Profile**：延伸使用者檔案資料（偏好偶像、簡介、隱私設定）。
- **Card**：代表一張小卡，包含偶像、專輯、版本、稀有度、圖片連結、狀態與擁有者關聯。
- **Trade**：代表一次交換交易，記錄雙方參與者、狀態、建立時間與完成時間。
- **TradeItem**：交換中單張小卡的關聯紀錄，指出該卡由哪一方提供。
- **Chat**：一對一聊天室實體，關聯兩個 User，並提供訊息串。
- **Message**：聊天室中的單則訊息，包含寄件者、內容、狀態與時間戳。
- **Friendship**：好友關係紀錄，包含邀請方、接受方、狀態與建立時間。
- **Rating**：交換後評分與文字回饋紀錄，關聯評分者與被評分者及對應 Trade。
- **Report**：檢舉紀錄，包含檢舉人、被檢舉人、原因類別與詳細說明。
- **Subscription**：會員方案訂閱紀錄，包含方案類型、起始與到期時間、狀態。
- **Post**：佈告欄貼文，包含作者、城市/行政區、內容、狀態與到期時間。
- **PostInterest**：對貼文表達有興趣的紀錄，包含貼文、送出者、狀態（待處理/已接受/已拒絕）。

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**：新使用者自安裝 App 至完成首次登入與基本個人檔案設定的流程時間，中位數需低於 3 分鐘，且完成率至少 80%。
- **SC-002**：在 100–200 MAU 的 POC 階段，聊天訊息從一方送出至另一方看到的平均延遲（前景 + 背景綜合）需低於 5 秒。
- **SC-003**：成功完成至少 1 次交換流程（含評分）的使用者中，至少 70% 樂於在未來一週內再次使用 App 進行交換（以問卷或使用行為追蹤衡量）。
- **SC-004**：免費會員在合理使用下（每日 3 張上傳、5 次附近搜尋）不會遇到明顯的效能瓶頸或等待時間超過 3 秒的情況（以 API 響應時間及前端體感測試為準）。
- **SC-005**：假卡或詐騙相關檢舉中，80% 以上可在 7 天內完成初步處理（停權、警示或標記）。
- **SC-006**：佈告欄貼文自建立起至第一次收到「有興趣」的時間中位數需低於 24 小時（Beta 期，樣本數 ≥ 50）。
- **SC-007**：在 Beta 期，至少 20% 的交換協商入口來源於佈告欄（以「有興趣→建立聊天室」事件追蹤衡量）。

---

#### 目錄結構規範

**說明**：本專案的 DDD 原則請參考專案憲法（Constitution Article VI）。下列為本專案具體目錄與實體定義（專案專屬內容），保留於 Spec 中以利開發實作。

#### 目錄結構規範（**已更新 2025-12-15，採用 Modular DDD**）

[CHANGED: 分層架構 → 模組化架構，原因：提升業務內聚性，符合 DDD Bounded Context 原則]

```
apps/backend/app/
├── main.py                 # 應用程式入口與路由聚合
├── config.py              # 全域配置管理
├── container.py           # 全域依賴注入容器
│
├── modules/               # 業務模組核心（取代原有的分層結構）
│   ├── identity/          # [Module] 認證與使用者管理（Auth + User）
│   │   ├── __init__.py
│   │   ├── domain/        # 領域層（Entities, Value Objects, Repository Interfaces）
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user.py              # User Entity
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user_id.py           # UserId VO
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user_repository_interface.py  # IUserRepository
│   │   │   └── exceptions/
│   │   │       ├── __init__.py
│   │   │       └── user_exceptions.py
│   │   │
│   │   ├── application/   # 應用層（Use Cases, DTOs）
│   │   │   ├── __init__.py
│   │   │   ├── use_cases/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── login_with_google.py
│   │   │   │   ├── refresh_token.py
│   │   │   │   └── logout.py
│   │   │   └── dtos/
│   │   │       ├── __init__.py
│   │   │       └── user_dto.py
│   │   │
│   │   ├── infrastructure/ # 基礎設施層（Repository 實作、外部服務）
│   │   │   ├── __init__.py
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   └── sqlalchemy_user_repository.py
│   │   │   └── external/
│   │   │       ├── __init__.py
│   │   │       └── google_oauth_service.py
│   │   │
│   │   └── presentation/  # 表現層（Routers, Schemas, Dependencies）
│   │       ├── __init__.py
│   │       ├── routers/
│   │       │   ├── __init__.py
│   │       │   └── auth_router.py       # /api/v1/auth/*
│   │       ├── schemas/
│   │       │   ├── __init__.py
│   │       │   └── auth_schemas.py
│   │       └── dependencies/
│   │           ├── __init__.py
│   │           └── auth_dependencies.py
│   │
│   └── social/            # [Module] 個人檔案與社交功能（Profile + Friends + Chat）
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   ├── profile.py           # Profile Entity
│       │   │   ├── friendship.py        # Friendship Entity
│       │   │   ├── chat.py              # Chat Entity
│       │   │   └── message.py           # Message Entity
│       │   ├── value_objects/
│       │   │   ├── __init__.py
│       │   │   ├── location.py          # Location VO
│       │   │   └── rating.py            # Rating VO
│       │   ├── repositories/
│       │   │   ├── __init__.py
│       │   │   ├── profile_repository_interface.py
│       │   │   ├── chat_repository_interface.py
│       │   │   └── friendship_repository_interface.py
│       │   ├── events/
│       │   │   ├── __init__.py
│       │   │   └── message_sent_event.py
│       │   └── exceptions/
│       │       ├── __init__.py
│       │       └── social_exceptions.py
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   ├── use_cases/
│       │   │   ├── __init__.py
│       │   │   ├── profile/
│       │   │   │   ├── get_profile.py
│       │   │   │   └── update_profile.py
│       │   │   ├── friends/
│       │   │   │   ├── send_friend_request.py
│       │   │   │   └── accept_friend_request.py
│       │   │   └── chat/
│       │   │       ├── send_message.py
│       │   │       └── get_chat_history.py
│       │   └── dtos/
│       │       ├── __init__.py
│       │       ├── profile_dto.py
│       │       └── message_dto.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── repositories/
│       │   │   ├── __init__.py
│       │   │   ├── sqlalchemy_profile_repository.py
│       │   │   ├── sqlalchemy_chat_repository.py
│       │   │   └── sqlalchemy_friendship_repository.py
│       │   └── external/
│       │       ├── __init__.py
│       │       └── fcm_notification_service.py
│       │
│       └── presentation/
│           ├── __init__.py
│           ├── routers/
│           │   ├── __init__.py
│           │   ├── profile_router.py    # /api/v1/profile/*
│           │   ├── friends_router.py    # /api/v1/friends/*
│           │   └── chat_router.py       # /api/v1/chats/*
│           ├── schemas/
│           │   ├── __init__.py
│           │   ├── profile_schemas.py
│           │   └── chat_schemas.py
│           └── dependencies/
│               ├── __init__.py
│               └── social_dependencies.py
│
└── shared/                # 共用核心（Shared Kernel）
    ├── __init__.py
    ├── domain/            # 共用 Value Objects
    │   ├── __init__.py
    │   ├── email.py       # Email VO
    │   └── base_entity.py # Entity 基類
    │
    ├── infrastructure/    # 共用基礎設施
    │   ├── __init__.py
    │   ├── database/
    │   │   ├── __init__.py
    │   │   ├── connection.py          # SQLAlchemy Engine/Session
    │   │   └── base_repository.py     # Repository 基類
    │   ├── security/
    │   │   ├── __init__.py
    │   │   ├── jwt_service.py
    │   │   └── password_hasher.py
    │   └── external/
    │       ├── __init__.py
    │       └── gcs_storage_service.py
    │
    └── presentation/      # 共用表現層組件
        ├── __init__.py
        ├── middleware/
        │   ├── __init__.py
        │   ├── error_handler.py
        │   └── logging_middleware.py
        └── exceptions/
            ├── __init__.py
            └── api_exceptions.py
```

---

#### 系統架構與設計約束

**DA-002A 架構模式約束**（**已更新 2025-12-15**）

- **架構模式**：[CHANGED: 分層架構 → 模組化架構 (Modular DDD)，原因：提升業務內聚性，符合 DDD Bounded Context 原則]
- **目錄組織原則**：採用「依功能分包 (Package by Feature)」的模組化設計
  - 系統必須按領域邊界（如 Identity、Social）劃分為獨立模組
  - 每個模組包含完整的 Domain、Application、Infrastructure、Presentation 層
  - 禁止使用傳統的依技術分層（如 routers/、services/ 散落在根目錄）
- **模組邊界定義**：
  - `identity` 模組：認證與使用者管理（Auth + User）
  - `social` 模組：個人檔案與社交功能（Profile）
  - `shared` 核心：共用基礎設施（資料庫、安全性、Value Objects）
- **驗收標準**：
  - 修改單一業務功能時，變更應限制在對應的單一模組目錄內
  - 模組間不得出現循環依賴（Circular Dependencies）
  - 共用邏輯必須放置於 `shared/` 目錄

#### 本專案核心 Entities

**DA-003 領域實體定義**

- **User**（使用者實體）：代表平台使用者帳號，包含登入識別、基本資料、會員等級
- **Card**（小卡實體）：代表一張小卡，包含偶像、專輯、版本、稀有度、圖片連結
- **Trade**（交換實體）：代表一次交換交易，記錄雙方參與者、狀態、時間
- **Chat**（聊天實體）：一對一聊天室實體，關聯兩個 User，並提供訊息串
- **Message**（訊息實體）：聊天室中的單則訊息，包含寄件者、內容、狀態
- **Friendship**（好友實體）：好友關係紀錄，包含邀請方、接受方、狀態
- **Rating**（評分實體）：交換後評分與文字回饋紀錄
- **Report**（檢舉實體）：檢舉紀錄，包含檢舉人、被檢舉人、原因類別

**DA-004 Repository 定義**

本專案需實作以下 Repository 介面（定義於 Domain Layer，實作於 Infrastructure Layer）：
- `IUserRepository`：使用者資料存取
- `ICardRepository`：小卡資料存取
- `ITradeRepository`：交換資料存取
- `IChatRepository`：聊天室資料存取
- `IMessageRepository`：訊息資料存取

**DA-005 Domain Events**

本專案需實作以下領域事件：
- `UserRegisteredEvent`：使用者註冊完成 → 發送歡迎通知
- `TradeCompletedEvent`：交換完成 → 更新信譽分數、發送完成通知
- `MessageSentEvent`：訊息發送 → 推送 FCM 通知
- `CardCreatedEvent`：小卡建立 → 通知附近使用者（付費功能）

---

#### 實作檢查清單

開發時必須確保以下項目（參考憲法 Article VI）：

- [ ] 所有 Domain Entities 不依賴 FastAPI、SQLAlchemy 或其他框架
- [ ] Repository 介面定義在 Domain Layer，實作在 Infrastructure Layer
- [ ] Use Cases 不包含 SQL 查詢或 HTTP 請求邏輯
- [ ] Routers 僅負責請求驗證與回應格式化，業務邏輯委派給 Use Cases
- [ ] ORM Models 與 Domain Entities 分離
- [ ] 單元測試覆蓋率達 80% 以上（Domain & Application Layer）
