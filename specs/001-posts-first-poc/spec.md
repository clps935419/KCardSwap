# Feature Specification: Posts-first POC (V2)

**Feature Branch**: `001-posts-first-poc`  
**Created**: 2026-01-23  
**Status**: Draft  
**Input**: 以「貼文為核心入口」的 POC；包含貼文（global/city 發布範圍）、貼文附圖、Like、私信作者（含陌生人訊息請求）、Inbox 信箱、個人小卡相簿（可管理），並以統一的內容/媒體配額限制使用量。

## Clarifications

### Session 2026-01-23

- Q: 你希望「global（不限）」貼文列表的內容是？ → A: Global 列表顯示「所有貼文」（`scope=global` + 所有 `scope=city`），城市列表是額外的篩選入口。
- Q: 未登入使用者是否可瀏覽內容？ → A: 不可；所有瀏覽（貼文列表/貼文詳情/個人頁/相簿）都需要登入。
- Q: 本次 POC 要優先實作哪個客戶端？ → A: Web 端。
- Q: Web POC 的框架與 UI/Form 方案？ → A: Next.js + shadcn/ui；表單使用 react-hook-form；資料抓取與快取使用 TanStack Query。
- Q: Web 端的 API client/hook 會怎麼做？ → A: 使用 hey-api（`@hey-api/openapi-ts`）從 `openapi/openapi.json` 生成 TypeScript SDK，並透過 `@tanstack/react-query` plugin 產生 TanStack Query 的 hooks（避免手寫 API 串接）。
- Q: Web 前端登入方式與前後端驗證要怎麼做？ → A: Web 使用 NextAuth 做 Google 登入；前端與後端的驗證採用 httpOnly cookie（不使用 LocalStorage token，也不以 Authorization: Bearer header 作為主要驗證方式）。
- Q: httpOnly cookie 具體採用哪種策略（session id vs JWT）？ → A: 本 POC 採用「cookie-JWT」：`access_token`（短效）與 `refresh_token`（長效）皆存放於 httpOnly cookie；當 access 過期時以前端呼叫 refresh 端點換發新的 access。
- Q: 部署與 SameSite 策略？ → A: Web 與 API 會同機同源部署；POC 預設 cookie 採 `SameSite=Lax`（並依環境搭配 `Secure`）。

## Scope

**In Scope（本版必做）**

- Web 端 POC（以 web 客戶端完成本規格的主要 user journeys）
- AUTH/PROFILE（登入、個人頁、隱私設定）
- POSTS（貼文列表、發文、篩選）
- POST MEDIA（貼文附圖）
- Like（類似 FB 讚：可新增/取消）
- DM + Inbox（私信作者 + 陌生人訊息請求 + 信箱列表）
- Profile Gallery（小卡相簿：新增/刪除/排序 + 他人可瀏覽）
- BIZ（統一內容/媒體配額 + 超額錯誤結構）
- REPORT/BLOCK（基本安全機制）

**Removed in V2（明確移除、不得出現任何詳細規格/端點/資料模型/驗收）**

- NEARBY 附近搜尋
- TRADE 交換狀態機
- trade 綁定評分

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - 發文與瀏覽貼文（含不限/指定城市）(Priority: P1)

已登入使用者可以瀏覽貼文列表，並能發佈貼文到「不限（全域）」或「指定城市」。貼文有固定分類（trade/giveaway/group/showcase/help/announcement），且可依分類與範圍做基本篩選。

**Why this priority**: 這是整個 V2 的核心入口；只要貼文可被發佈與瀏覽，就能驗證內容互動與資訊流是否成立。

**Independent Test**: 用兩個帳號：A 發佈 1 則 global 貼文與 1 則 city 貼文；B 可以分別在 global 與指定城市列表看到對應貼文，並可用分類篩選。

**Acceptance Scenarios**:

1. **Given** 使用者已登入，**When** 發佈一則貼文並選擇 scope=global，**Then** 任何瀏覽 global 列表的使用者都能看到該貼文。
2. **Given** 使用者已登入，**When** 發佈一則貼文並選擇 scope=city 且指定 city_code，**Then** 該貼文會在 global 列表可見，且也能在對應的城市列表中被找到。
3. **Given** 貼文已存在，**When** 使用者用分類進行篩選，**Then** 列表只顯示符合分類的貼文。

---

### User Story 2 - 管理個人小卡相簿並瀏覽他人相簿 (Priority: P2)

已登入使用者可以建立自己的小卡相簿內容（新增/刪除/排序），並在他人的個人頁瀏覽對方公開的相簿小卡。

**Why this priority**: 相簿是使用者的展示資產，能支撐「私信作者」與內容互動的動機；同時這也是本版必做且需納入配額的主要媒體來源。

**Independent Test**: A 新增 3 張相簿小卡 → 調整順序 → 刪除其中 1 張；B 進入 A 的個人頁能看到剩餘 2 張，且順序正確。

**Acceptance Scenarios**:

1. **Given** 使用者已登入，**When** 新增一張相簿小卡並提供必要資訊（例如標題/備註）與圖片，**Then** 相簿中出現新卡且可被他人瀏覽。
2. **Given** 使用者相簿已有多張小卡，**When** 調整排序，**Then** 重新整理後順序仍維持。
3. **Given** 使用者相簿已有小卡，**When** 刪除其中一張，**Then** 該卡不再被任何人看到，且不影響其他卡。

---

### User Story 3 - 貼文附圖與媒體上傳確認 (Priority: P2)

已登入使用者可以在發文時附加圖片。系統必須提供「上傳授權 → 上傳 → 上傳確認 → 綁定到貼文/相簿」的流程，避免產生幽靈資料，並確保媒體配額只在成功確認後計入。

**Why this priority**: 圖片是內容互動的核心；同時此流程直接關係到成本與配額正確性。

**Independent Test**: 使用者發佈一則帶 1 張圖片的貼文，重新整理後圖片仍可見；若上傳未完成則不應出現在貼文中，也不應計入媒體總量。

**Acceptance Scenarios**:

1. **Given** 使用者已登入且有可用媒體額度，**When** 完成圖片上傳並確認後再發佈貼文，**Then** 貼文會顯示圖片。
2. **Given** 使用者未完成圖片上傳確認，**When** 嘗試將該圖片綁定到貼文或相簿，**Then** 系統必須拒絕並要求重新上傳。

### User Story 4 - Like 與互動量 (Priority: P3)

已登入使用者可以對貼文按讚與取消讚，並看到貼文的 like 數量。

**Why this priority**: Like 是最低摩擦的互動；可用於驗證互動意願並支撐熱門排序或作者回饋（是否加入排序屬後續優化）。

**Independent Test**: 使用者對同一則貼文按讚→取消→再按讚，like_count 會正確變化且不會重複計數。

**Acceptance Scenarios**:

1. **Given** 使用者已登入，**When** 對貼文按讚，**Then** like_count 增加且使用者再次按讚不會重複增加。
2. **Given** 使用者已按讚，**When** 取消讚，**Then** like_count 減少且貼文狀態更新。

---

### User Story 5 - 私信作者（含陌生人訊息請求）與 Inbox 信箱 (Priority: P2)

已登入使用者可以在貼文上點選「私信作者」。若雙方尚未建立對話，系統建立一筆訊息請求（Message Request），接收者可選擇接受或拒絕；接受後進入正式對話（thread），並在 Inbox（信箱）中可見。接收者可設定是否接受陌生人私訊。

**Why this priority**: 這是「互動 → 轉換」的主路徑；不依賴交換狀態機也能達成溝通。

**Independent Test**: A 對 B 私信 → B 在 Requests 看到並 Accept → A/B 在 Inbox 看到同一個 thread 並可互傳訊息。

**Acceptance Scenarios**:

1. **Given** 使用者已登入且作者允許陌生人私訊，**When** 點選「私信作者」並送出第一則訊息，**Then** 作者會在 Requests 中看到該請求。
2. **Given** 作者收到請求，**When** Accept，**Then** 雙方會有唯一的 thread 並出現在 Inbox。
3. **Given** 作者關閉陌生人私訊，**When** 陌生人嘗試私信作者，**Then** 系統必須拒絕且不建立 request/thread。
4. **Given** 同一對 user 已存在 pending request 或 accepted thread，**When** 再次嘗試私信，**Then** 系統必須導向同一個對話（不得建立第二個 thread）。

---

### Edge Cases

- 使用者發文選擇 scope=city 但未提供 city_code 時，必須阻止並提示。
- 使用者嘗試將未完成上傳確認的媒體綁定到貼文/相簿時，必須拒絕。
- 媒體上傳成功但貼文/相簿建立失敗時，媒體不得顯示且不得影響後續可用性（需有清楚錯誤訊息）。
- 媒體配額超額（單檔超大、或月總量不足）時，必須回覆可理解的限制資訊與重置時間。
- 接收者關閉陌生人私訊時，陌生人不得建立 request。
- 使用者被封鎖後，雙方不得互相私信（含發送 request）。
- 同一使用者重複按讚/取消讚，不得造成 like_count 不一致。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 要求使用者登入後才可瀏覽貼文/個人頁/相簿，以及執行發文、按讚、私信、管理相簿。
- **FR-002**: 貼文 MUST 具備固定分類 `trade/giveaway/group/showcase/help/announcement`，不允許其他值。
- **FR-003**: 貼文 MUST 支援發布範圍：`scope=global` 或 `scope=city`。
- **FR-004**: 當 `scope=city` 時，貼文 MUST 具備 `city_code`；當 `scope=global` 時，`city_code` MUST 為空。
- **FR-005**: 系統 MUST 提供貼文列表；global 列表 MUST 顯示所有貼文（`scope=global` + `scope=city`），且使用者 MUST 能依分類與城市進行篩選（城市篩選入口可為「城市列表」）。

- **FR-006**: 系統 MUST 支援貼文附圖，並以「上傳授權 → 上傳 → 上傳確認 → 綁定」的流程確保媒體有效性。
- **FR-007**: 系統 MUST 僅允許綁定「已完成上傳確認」且「屬於該使用者」的媒體。

- **FR-008**: 系統 MUST 支援 Like：使用者可對貼文按讚與取消讚。
- **FR-009**: 每位使用者對同一貼文 MUST 最多只有一個 Like 狀態（不得重複計數）。

- **FR-010**: 系統 MUST 提供「私信作者」能力，且 MUST 要求登入。
- **FR-011**: 系統 MUST 支援 Message Requests：陌生人私訊在被接受前，不得視為正式對話。
- **FR-012**: 接收者 MUST 能 Accept 或 Decline 訊息請求；Accept 後建立 thread。
- **FR-013**: 使用者 MUST 能設定是否接受陌生人私訊；當關閉時，陌生人私信 MUST 被拒絕且不得建立 request/thread。
- **FR-014**: 同一對 user MUST 永遠只有一個對話單元：要嘛是 pending request，要嘛是 accepted thread。
- **FR-015**: 訊息 MAY 附帶 `post_id` 作引用，用於讓接收者知道訊息來源貼文。

- **FR-016**: 系統 MUST 提供 Inbox（信箱）列表，並清楚區分 Requests 與已接受的對話。

- **FR-017**: 系統 MUST 提供小卡相簿（Profile Gallery），使用者 MUST 能新增/刪除/排序自己的相簿小卡。
- **FR-018**: 其他使用者 MUST 能瀏覽對方公開的相簿小卡。
- **FR-019**: 相簿小卡 MUST 為展示用途，不得包含交換狀態（例如持有/欲交換/已交換）。
- **FR-020**: 相簿圖片上傳 MUST 同樣遵循「上傳授權 → 上傳 → 上傳確認 → 綁定」流程。

- **FR-021**: 系統 MUST 實作統一的內容/媒體配額，且媒體配額 MUST 合併計入「貼文圖片 + 相簿圖片」。
- **FR-022**: 媒體配額 MUST 只在「上傳確認成功」時計入。

- **FR-023**: 配額 keys 與預設值 MUST 固定如下：
  - `posts_per_day`：Free=2/day，Premium=20/day（每日 00:00 Asia/Taipei 重置）
  - `post_images_per_post_max`：Free=1，Premium=4
  - `gallery_cards_count_max`：Free=50，Premium=500
  - `media_file_bytes_max`：Free=1MB，Premium=5MB
  - `media_bytes_per_month`：Free=50MB/month，Premium=2GB/month（每月 1 日 00:00 Asia/Taipei 重置；合併計入貼文圖+相簿圖）

- **FR-024**: 當任何配額超額時，系統 MUST 阻擋請求並回傳 `422_LIMIT_EXCEEDED`，且錯誤內容 MUST 包含：`limit_key`, `limit_value`, `current_value`, `reset_at`。

- **FR-025**: 系統 MUST 提供封鎖與檢舉能力；封鎖雙方不得互相私信（含建立 request）。

- **FR-026**: 系統 MUST 使用 httpOnly cookie 作為主要登入狀態承載方式，且 Web 端登入流程 MUST 以 NextAuth + Google OAuth 完成。
- **FR-027**: 系統 MUST 提供以 refresh token 換發 access token 的機制：當 access token 過期時，前端可呼叫 refresh 端點以取得新的 access token（不需使用者重新登入）。

### Assumptions

- 會員方案至少有 Free 與 Premium 兩種，且每位使用者在任一時間點只會落在其中一種方案。
- `city_code` 來自既有的城市清單（由產品/營運維護），本規格不定義城市清單內容。
- 本版 POC 的內容瀏覽皆需要登入；若未來要支援未登入瀏覽屬後續擴充，不在本版範圍。
- 同一對 user 的「唯一對話」以產品規則為準（不因貼文不同而拆分多個 thread）。
- 本 POC 的 Web 與 API 會同機同源部署；cookie 策略以 `SameSite=Lax` 為預設，以降低跨域與 CSRF 複雜度。

### Dependencies

- 已存在可用的登入機制與最小個人資料（用於識別作者、收件者、封鎖/檢舉關係）。
- 已存在可持久化保存媒體檔案與其擁有者/狀態（用於上傳確認與配額計算）。
- 已存在可查詢/判斷使用者封鎖關係與陌生人私訊設定的能力。
- Web POC 前端以 Next.js 實作，UI 元件以 shadcn/ui 為主，表單使用 react-hook-form。
- Web 的 API 呼叫使用 hey-api 生成的 TanStack Query SDK（`@hey-api/openapi-ts` + `@tanstack/react-query` plugin）；前端不手寫 endpoint。
- Web 的登入/Session 以 httpOnly cookie 為主：前端呼叫 API 時需能攜帶 cookie（同源或跨域 with credentials）。
- Cookie-JWT 採用 access/refresh 雙 token；需有 refresh 端點用於換發新的 access token。

### Key Entities *(include if feature involves data)*

- **Post**: 貼文本體（作者、分類、scope、可選 city_code、內容、狀態）。
- **MediaAsset**: 媒體檔案（圖片），可被貼文或相簿小卡引用。
- **PostMedia**: 貼文與媒體的關聯（同一貼文可有多張圖，受配額限制）。
- **PostLike**: 使用者對貼文的 Like 狀態。
- **MessageRequest**: 陌生人私訊請求（pending/accepted/declined）。
- **MessageThread**: 已接受的對話 thread（同一對 user 唯一）。
- **Message**: 訊息（可選引用 post_id）。
- **GalleryCard**: 相簿小卡（展示用途、可排序、可刪除）。
- **QuotaPolicy**: 會員方案對應的配額配置。
- **QuotaUsage**: 使用者在週期內（或總量）已使用的計數與總量。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 新使用者在完成登入後，能在 2 分鐘內完成「發佈第一則貼文（global 或 city）」。
- **SC-002**: 使用者能在 2 分鐘內完成「新增 1 張相簿小卡（含圖片）」，並可在個人頁被他人看到。
- **SC-003**: 使用者能在 1 分鐘內完成「對貼文按讚與取消讚」，且 like_count 始終一致。
- **SC-004**: 陌生人私訊請求在 30 秒內可被接收者看見，且接收者能在 1 分鐘內完成 Accept 或 Decline。
- **SC-005**: 當使用者超過任一配額時，系統回覆的錯誤資訊足以讓使用者理解「哪個限制超了、目前用了多少、何時重置」。
