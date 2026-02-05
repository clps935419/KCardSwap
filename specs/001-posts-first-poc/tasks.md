---

description: "Task list for implementing Posts-first POC (V2)"
---

# Tasks: Posts-first POC (V2)

**Input**: Design documents from `specs/001-posts-first-poc/`
- Required: `specs/001-posts-first-poc/spec.md`, `specs/001-posts-first-poc/plan.md`
- Available (detected): `openapi/openapi.json`

**Prerequisites**: `spec.md` (user stories), `plan.md` (project structure + constraints)

**Tests**: 本任務清單包含後端 pytest 與 Web 基本測試/E2E 建議（plan.md 的「測試優先開發」要求）。

**Organization**: Tasks 依 user story 分組，確保每個 user story 可獨立實作與驗收。

## Format（必須符合）

- 每個 task 必須是：`- [ ] T### [P?] [US#?] 動作 + 檔案路徑`
- **[P]**：可平行（不同檔案、無未完成依賴）
- **[US#]**：只用在 User Story phases（US1..US5）

---

## Phase 1: Setup（Shared Infrastructure）

**Purpose**: 建立 Web POC 專案骨架與 repo-level 工具串接（不做任何功能邏輯）。

- [x] T001 建立 Web app 目錄與基礎 README（新增 apps/web/README.md）
- [x] T002 初始化 Next.js App Router 專案骨架（建立 apps/web/package.json 與 apps/web/src/app/ 入口檔）
- [x] T003 [P] 設定 Web 開發環境檔案（新增 apps/web/.env.example 與 apps/web/.env.local 指引寫在 apps/web/README.md）
- [x] T004 [P] 設定 Web lint/format（新增 apps/web/eslint.config.js、apps/web/prettier.config.js）
- [x] T005 [P] 安裝並初始化 shadcn/ui（更新 apps/web/components.json 並建立 apps/web/src/components/ui/）
- [x] T006 [P] 設定 TanStack Query Provider 與 queryClient（新增 apps/web/src/app/providers.tsx 與 apps/web/src/lib/query-client.ts）
- [x] T007 [P] 建立共用 UI/utility 結構（新增 apps/web/src/components/、apps/web/src/lib/、apps/web/src/features/ 目錄占位檔）
- [x] T008 建立 Web 專案的路由骨架（新增 apps/web/src/app/(auth)/login/page.tsx 與 apps/web/src/app/(app)/layout.tsx）

---

## Phase 2: Foundational（Blocking Prerequisites）

**Purpose**: 所有 user story 共同依賴的後端合約、認證、錯誤格式、配額與 SDK 生成流程。

- [x] T009 盤點現有 API 與本 POC 規格缺口（更新 specs/001-posts-first-poc/research.md，輸出需含：①要新增/調整的 endpoints 清單（path+method+owner）②明確「不使用/需移除」清單（NEARBY/TRADE/評分相關；含 path+method→對應 router/module/test 檔案與處理策略：移除/停用/保留但不曝光）③是否已從 openapi/openapi.json 移除）
- [x] T010 定義 POC 共用錯誤格式（新增 apps/backend/app/shared/presentation/errors/limit_exceeded.py，支援 422_LIMIT_EXCEEDED payload: limit_key/limit_value/current_value/reset_at）
- [x] T011 實作「所有瀏覽需登入」的共用依賴（新增 apps/backend/app/shared/presentation/deps/require_user.py 並套用到後續 routers）
- [x] T012 [P] 新增/調整 cookie-JWT（access/refresh）設定（更新 apps/backend/app/config.py，加入 cookie 名稱、TTL、SameSite、Secure 等設定項）
- [x] T013 實作 refresh endpoint 改為 httpOnly cookie 流程（更新 apps/backend/app/modules/identity/presentation/routers/auth_router.py，讓 /api/v1/auth/refresh 旋轉/換發 access cookie）
- [x] T014 [P] 新增後端整合測試：refresh cookie 行為（新增 apps/backend/tests/integration/modules/identity/test_auth_refresh_cookie.py）
- [x] T015 統一「內容/媒體配額」domain 介面（新增 apps/backend/app/shared/domain/quota/ 目錄，包含 limit keys 與 reset policy）
- [x] T016 [P] 實作 posts_per_day 配額檢查（新增 apps/backend/app/modules/posts/application/services/post_quota_service.py 並在建立貼文 use case 套用）
- [x] T017 [P] 實作 media 配額介面（新增 apps/backend/app/shared/domain/quota/media_quota_service.py，支援 media_file_bytes_max 與 media_bytes_per_month）
- [x] T018 Web：建立 API client 與 cookie 傳遞規則（新增 apps/web/src/lib/api/axios.ts，預設 withCredentials 並集中處理 baseURL）
- [x] T019 Web：建立 401 → refresh → retry 機制（新增 apps/web/src/lib/api/auth-refresh.ts 與 apps/web/src/lib/api/axios-interceptors.ts）
- [x] T020 OpenAPI 生成流程對齊（更新 apps/backend/scripts/generate_openapi.py 的說明文件：apps/backend/README.md 新增 POC 流程段落）
- [x] T021 生成並提交最新 OpenAPI snapshot（更新 openapi/openapi.json）
- [x] T022 Web：建立 hey-api 生成設定與輸出位置（新增 apps/web/openapi.config.ts 與 apps/web/src/shared/api/generated/ 目錄）
- [x] T023 Web：新增 SDK 生成腳本（更新 apps/web/package.json 新增 "sdk:generate" 指令，讀取 repo root openapi/openapi.json）

**Checkpoint**: Foundation 完成後，US1..US5 可開始分工實作。

---

## Phase 3: User Story 1 - 發文與瀏覽貼文（global/city + 分類篩選）(Priority: P1) 🎯 MVP

**Goal**: 已登入使用者可發文（scope=global/city）並在 global/城市列表瀏覽；可依分類與城市篩選。

**Independent Test**: 兩帳號 A/B；A 發佈 1 則 global + 1 則 city；B 在 global 與指定 city 列表可看到對應貼文；可用分類篩選。

### Tests（後端）

- [x] T024 [P] [US1] 新增 posts 建立/列表整合測試（新增 apps/backend/tests/integration/modules/posts/test_posts_create_and_list_v2.py）

### Backend（DDD: posts module）

- [x] T025 [P] [US1] 定義 PostCategory 與 PostScope（新增 apps/backend/app/modules/posts/domain/models/post_enums.py）
- [x] T026 [P] [US1] 調整 Post domain model 支援 scope/city_code/category（更新 apps/backend/app/modules/posts/domain/models/post.py）
- [x] T027 [US1] 調整 CreatePostRequest/Response schema（更新 apps/backend/app/modules/posts/presentation/schemas/post_schemas.py）
- [x] T028 [US1] 調整 list_posts 查詢支援 global（含 city）與 city 篩選（更新 apps/backend/app/modules/posts/infrastructure/repositories/post_repository.py）
- [x] T029 [US1] 更新 posts router 合約支援 scope/city_code/category（更新 apps/backend/app/modules/posts/presentation/routers/posts_router.py；GET/POST /api/v1/posts 依 specs/001-posts-first-poc/spec.md FR-003/FR-004/FR-005）
- [x] T030 [US1] 將 require_user 依賴套用到 posts router（更新 apps/backend/app/modules/posts/presentation/routers/posts_router.py）

### Web（apps/web）

- [x] T031 [P] [US1] 建立貼文列表頁骨架（新增 apps/web/src/app/(app)/posts/page.tsx）
- [x] T032 [P] [US1] 建立貼文列表查詢 hook（新增 apps/web/src/features/posts/hooks/usePostsList.ts，使用生成的 TanStack Query hooks）
- [x] T033 [P] [US1] 建立貼文篩選 UI（新增 apps/web/src/features/posts/components/PostFilters.tsx）
- [x] T034 [US1] 建立發文頁與表單（新增 apps/web/src/app/(app)/posts/new/page.tsx 與 apps/web/src/features/posts/components/CreatePostForm.tsx）
- [x] T035 [US1] 串接建立貼文 mutation（更新 apps/web/src/features/posts/components/CreatePostForm.tsx）

**Checkpoint**: US1 可獨立 demo（文字貼文 + global/city + 分類/城市篩選）。

---

## Phase 4: User Story 2 - 管理個人小卡相簿並瀏覽他人相簿 (Priority: P2)

**Goal**: 使用者可新增/刪除/排序自己的相簿卡；他人可在個人頁瀏覽。

**Independent Test**: A 新增 3 張 → 調整排序 → 刪 1 張；B 進 A 個人頁看見 2 張且順序正確。

### Tests（後端）

- [x] T036 [P] [US2] 新增 gallery cards CRUD+reorder 整合測試（新增 apps/backend/tests/integration/modules/social/test_gallery_cards_v2.py）

### Backend（建議：social module 新增 GalleryCard bounded context；避免使用 trading/traded 狀態）

- [x] T037 [P] [US2] 定義 GalleryCard domain model（新增 apps/backend/app/modules/social/domain/entities/gallery_card.py）
- [x] T038 [P] [US2] 定義排序規則與 reordering use case（新增 apps/backend/app/modules/social/application/use_cases/reorder_gallery_cards.py）
- [x] T039 [P] [US2] 建立 repository（新增 apps/backend/app/modules/social/infrastructure/repositories/gallery_card_repository.py 與 domain/repositories/i_gallery_card_repository.py）
- [x] T040 [US2] 建立 gallery router endpoints（新增 apps/backend/app/modules/social/presentation/routers/gallery_router.py 並在 apps/backend/app/main.py 註冊；包含 users/{user_id}/gallery/cards、gallery/cards/me、POST gallery/cards、DELETE gallery/cards/{card_id}、PUT gallery/cards/reorder）
- [x] T041 [US2] 將 require_user 依賴套用到 gallery router（更新 apps/backend/app/modules/social/presentation/routers/gallery_router.py）

### Web（apps/web）

- [x] T042 [P] [US2] 建立個人頁與相簿區塊 UI（新增 apps/web/src/app/(app)/users/[userId]/page.tsx 與 apps/web/src/features/gallery/components/GalleryGrid.tsx）
- [x] T043 [P] [US2] 建立我的相簿管理頁（新增 apps/web/src/app/(app)/me/gallery/page.tsx）
- [x] T044 [US2] 串接新增/刪除/排序 mutations（新增 apps/web/src/features/gallery/hooks/useGalleryMutations.ts）

---

## Phase 5: User Story 3 - 貼文附圖與媒體上傳確認 (Priority: P2)

**Goal**: 媒體上傳必須走 presign → upload → confirm → attach；且配額只在 confirm 時計入；同一媒體可被貼文或相簿引用。

**Independent Test**: 發佈 1 則帶 1 張圖的貼文；重整仍可見。未 confirm 的媒體不可 attach 且不計入媒體總量。

### Tests（後端）

- [x] T045 [P] [US3] 新增 media 上傳確認與 attach 整合測試（新增 apps/backend/tests/integration/modules/media/test_media_upload_confirm_attach.py）

### Backend（新增 media module）

- [x] T046 [P] [US3] 建立 MediaAsset domain model（新增 apps/backend/app/modules/media/domain/models/media_asset.py）
- [x] T047 [P] [US3] 建立 presign use case（新增 apps/backend/app/modules/media/application/use_cases/create_upload_url.py）
- [x] T048 [P] [US3] 建立 confirm use case（新增 apps/backend/app/modules/media/application/use_cases/confirm_upload.py）
- [x] T049 [P] [US3] 建立 attach-to-post / attach-to-gallery use cases（新增 apps/backend/app/modules/media/application/use_cases/attach_media.py）
- [x] T050 [P] [US3] 建立 media repository（新增 apps/backend/app/modules/media/infrastructure/repositories/media_repository.py）
- [x] T051 [US3] 建立 media router endpoints（新增 apps/backend/app/modules/media/presentation/routers/media_router.py 並在 apps/backend/app/main.py 註冊；包含 media/upload-url、media/{media_id}/confirm、posts/{post_id}/media/attach、gallery/cards/{card_id}/media/attach）
- [x] T052 [US3] 在 confirm use case 套用 media 配額（更新 apps/backend/app/modules/media/application/use_cases/confirm_upload.py 使用 apps/backend/app/shared/domain/quota/media_quota_service.py）

### Web（apps/web）

- [x] T053 [P] [US3] 建立通用上傳 helper（新增 apps/web/src/lib/media/uploadFlow.ts：presign→PUT→confirm）
- [x] T054 [US3] 發文表單加入圖片欄位並串接 attach（更新 apps/web/src/features/posts/components/CreatePostForm.tsx）
- [x] T055 [US3] 相簿新增卡流程加入圖片上傳（更新 apps/web/src/features/gallery/components/GalleryCreateCardForm.tsx）

---

## Phase 6: User Story 5 - 私信作者（含陌生人訊息請求）與 Inbox 信箱 (Priority: P2)

**Goal**: 私信作者會先建立 Message Request；接收者 accept 後變成唯一 thread；Inbox 區分 Requests 與 Threads；可帶 post_id 引用；可拒絕陌生人私訊。

**Independent Test**: A 私信 B → B 在 Requests 看見並 Accept → A/B 在 Inbox 看見同一 thread 並可互傳訊息。

### Tests（後端）

- [x] T056 [P] [US5] 新增 message request/accept/thread 唯一性整合測試（新增 apps/backend/tests/integration/modules/social/test_message_requests_v2.py）

### Backend（建議：social/chat 擴充）

- [x] T057 [P] [US5] 定義 MessageRequest/Thread/Message domain models（新增 apps/backend/app/modules/social/domain/models/message_request.py 與 apps/backend/app/modules/social/domain/models/message.py）
- [x] T058 [P] [US5] 實作唯一對話規則（新增 apps/backend/app/modules/social/application/services/thread_uniqueness_service.py）
- [x] T059 [P] [US5] 實作 request create/accept/decline use cases（新增 apps/backend/app/modules/social/application/use_cases/message_requests/ 目錄）
- [x] T060 [P] [US5] 實作 thread list/message list/send message use cases（新增 apps/backend/app/modules/social/application/use_cases/messages/ 目錄）
- [x] T061 [US5] 建立 message request + threads routers（新增 apps/backend/app/modules/social/presentation/routers/message_requests_router.py 與 apps/backend/app/modules/social/presentation/routers/threads_router.py；包含 message-requests create/inbox/accept/decline 與 threads list/messages list/send）
- [x] T062 [US5] 封鎖/隱私設定檢查（更新 apps/backend/app/modules/identity/application/services/privacy_service.py：拒絕陌生人私訊 + block 規則）

### Web（apps/web）

- [x] T063 [P] [US5] 建立 Inbox UI：Requests/Threads tabs（新增 apps/web/src/app/(app)/inbox/page.tsx）
- [x] T064 [P] [US5] 建立 thread 頁與訊息列表（新增 apps/web/src/app/(app)/inbox/threads/[threadId]/page.tsx）
- [x] T065 [US5] 串接送出訊息（新增 apps/web/src/features/inbox/hooks/useSendMessage.ts）
- [x] T066 [US5] 在貼文詳情/卡片加入「私信作者」入口（更新 apps/web/src/features/posts/components/PostCard.tsx）

---

## Phase 7: User Story 4 - Like 與互動量 (Priority: P3)

**Goal**: 使用者可按讚/取消讚；like_count 正確且不重複計數。

**Independent Test**: 同一貼文按讚→取消→再按讚；like_count 正確變化且狀態一致。

### Tests（後端）

- [x] T067 [P] [US4] 新增 like create/delete/idempotent 整合測試（新增 apps/backend/tests/integration/modules/posts/test_post_likes_v2.py）

### Backend（posts module）

- [x] T068 [P] [US4] 定義 PostLike domain model（新增 apps/backend/app/modules/posts/domain/models/post_like.py）
- [x] T069 [P] [US4] 建立 like repository（新增 apps/backend/app/modules/posts/infrastructure/repositories/post_like_repository.py）
- [x] T070 [P] [US4] 建立 like use cases（新增 apps/backend/app/modules/posts/application/use_cases/toggle_like.py）
- [x] T071 [US4] 新增 like endpoints 與回傳欄位（更新 apps/backend/app/modules/posts/presentation/routers/posts_router.py 與 apps/backend/app/modules/posts/presentation/schemas/post_schemas.py；POST/DELETE posts/{post_id}/like；Post response 帶 like_count、liked_by_me）

### Web（apps/web）

- [x] T072 [P] [US4] 建立 LikeButton 元件（新增 apps/web/src/features/posts/components/LikeButton.tsx）
- [x] T073 [US4] 在貼文卡片串接 like mutation 與 optimistic update（更新 apps/web/src/features/posts/components/PostCard.tsx）

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 跨故事品質、文件、SDK 對齊與 Demo 驗收。

- [ ] T074 補齊 Web POC 快速開始文件（新增 specs/001-posts-first-poc/quickstart.md，描述 apps/web 啟動、同源 cookie、SDK 生成流程）
- [ ] T075 [P] 建立 E2E 測試骨架（新增 apps/web/playwright.config.ts 與 apps/web/tests/e2e/posts_first_poc.spec.ts）
- [ ] T076 [P] 後端：避免 N+1（更新 apps/backend/app/modules/posts/infrastructure/repositories/post_repository.py 加入 eager loading/最佳化）
- [ ] T077 Web：為「所有頁面需登入」加上 route guard（更新 apps/web/src/middleware.ts 與 apps/web/src/app/(app)/layout.tsx）
- [ ] T078 Web：確認不出現 NEARBY/TRADE/評分相關 UI/字樣（掃描並更新 apps/web/src/）
- [ ] T079 後端：更新 OpenAPI 說明與重新生成（更新 openapi/openapi.json）
- [ ] T080 依 specs/001-posts-first-poc/spec.md 的 Success Criteria 撰寫 Demo Checklist（新增 specs/001-posts-first-poc/checklists/demo.md）
- [ ] T081 [P] 後端：確認/移除 NEARBY/TRADE/評分相關 endpoints 或模組註冊（掃描 apps/backend/app/modules/ 與 openapi/openapi.json；如存在則移除 router 註冊、相關 schemas/use cases、並更新/移除對應測試後重新生成 openapi/openapi.json）

---

## Phase 9: Media Read Signed URLs（Images view with login-only access）

**Goal**: 登入後才能取得圖片的長效 GET signed URL（可調 TTL），前端支援批次取得。 

### Tests（後端）

- [ ] T082 [P] [US3] 新增 media 讀取 URL 整合測試（新增 apps/backend/tests/integration/modules/media/test_media_read_urls.py）

### Backend（media module）

- [ ] T083 [P] [US3] 定義 read signed URL request/response schema（新增 apps/backend/app/modules/media/presentation/schemas/media_read_url_schemas.py）
- [ ] T084 [P] [US3] 新增批次 read signed URLs use case（新增 apps/backend/app/modules/media/application/use_cases/get_read_urls.py）
- [ ] T085 [US3] 新增 media read URLs endpoint（更新 apps/backend/app/modules/media/presentation/routers/media_router.py；POST /api/v1/media/read-urls）
- [ ] T086 [US3] 加入 media 可見性驗證（更新 apps/backend/app/modules/media/application/services/media_access_service.py 或新增；確認登入即可查看貼文/相簿圖片）
- [ ] T087 [US3] 後端回傳圖片 ID（更新 apps/backend/app/modules/posts/presentation/schemas/post_schemas.py 與對應 use case；PostResponse/PostListResponse 加入 media_asset_ids: UUID[]，若無圖回空陣列）

### Web（apps/web）

- [ ] T088 [P] [US3] 建立批次 read URL hook（新增 apps/web/src/features/media/hooks/useReadMediaUrls.ts；輸入 media_asset_ids，回傳 media_id -> url 對照）
- [ ] T089 [US3] 帖文/相簿列表改用 read URL 顯示圖片（更新 apps/web/src/features/posts/components/PostsList.tsx 與 apps/web/src/features/gallery/components/GalleryGrid.tsx；從 PostResponse.media_asset_ids 蒐集並呼叫 read-urls）

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1（Setup）→ Phase 2（Foundational）→ User Stories
- Phase 2 完成前，不應開始任何 US 實作

### User Story Dependencies（建議）

- US1（P1）是 MVP；可在 Phase 2 完成後優先交付
- US2（P2）、US3（P2）、US5（P2）可在 Phase 2 後平行
- US4（P3）依賴 US1（需要貼文存在與列表/詳情 UI）

---

## Parallel Execution Examples

### US1

- [P] T025（enums）、T026（domain model）、T031（頁面骨架）、T032（hook）、T033（filters）可平行

### US2

- [P] T037（domain）、T038（use case）、T039（repo）、T042（個人頁 UI）、T043（管理頁 UI）可平行

### US3

- [P] T046..T050（domain/use cases/repo）可平行；Web 的 T053 可與後端並行

### US5

- [P] T057..T060（domain/use cases/services）可平行；Web 的 T063/T064 可先做 UI skeleton

### US4

- [P] T068..T070 可平行；T072 可與後端並行

---

## Implementation Strategy

### MVP First（US1 only）

1. 完成 Phase 1 + Phase 2（包含 cookie refresh、SDK 生成）
2. 完成 US1（文字貼文 + global/city + 篩選）
3. 以 US1 的 Independent Test 驗收

### Incremental Delivery

- 依 P2（US2/US3/US5）平行開發，最後再補 US4（Like）與 Polish/E2E。
