# Implementation Plan: Posts-first POC (V2)

**Branch**: `001-posts-first-poc` | **Date**: 2026-01-23 | **Spec**: [specs/001-posts-first-poc/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-posts-first-poc/spec.md`

## Summary

本 POC 以 Web 端完成「貼文為核心入口」的最小可用產品：需登入才能瀏覽與互動；貼文支援 global/city 發布與篩選；貼文可附圖（授權→上傳→確認→綁定）；互動包含 Like 與私信作者（IG 式 Message Requests + Inbox）；並提供可管理的個人小卡相簿（新增/刪除/排序）。所有貼文圖片與相簿圖片合併計入統一媒體配額，且只在 confirm 成功時計入。

補強互動閉環：在貼文列表/詳情點擊作者頭像或暱稱，可進入「他人個人詳細頁」（UI 風格類 IG：上方頭貼+個人資訊、下方相簿小卡）。

## Technical Context

**Language/Version**: TypeScript（Web）；Python 3.11+（Backend）  
**Primary Dependencies**:
- Web: Next.js（App Router）、shadcn/ui、react-hook-form、TanStack Query
- Web SDK: hey-api（`@hey-api/openapi-ts` + `@hey-api/client-axios`）+ `@tanstack/react-query` plugin（由 `openapi/openapi.json` 生成）
- Backend: FastAPI、SQLAlchemy、Alembic、Poetry
**Storage**: PostgreSQL（apps/backend）  
**Testing**:
- Backend: pytest（單元/整合）
- Web: Jest + React Testing Library（單元/元件）；Playwright（E2E，建議）
**Target Platform**: Web（瀏覽器）+ 既有 Backend API  
**Project Type**: Web application + API（monorepo: apps/backend + apps/web）  
**Performance Goals**: POC 以正確性與可驗收為主；列表與信箱在一般資料量下保持可用（避免 N+1 與重複查詢）  
**Constraints**:
- 需登入才能瀏覽任何內容（含貼文列表/詳情、個人頁/相簿）
- 媒體配額只在上傳 confirm 成功時計入
- global 列表顯示所有貼文（global+city）；城市列表是篩選入口
**Scale/Scope**: POC（最小閉環：發文→互動→私訊→相簿展示）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- API 優先開發：Web 端不直接繞過 API；所有資料讀寫走後端
- 測試優先開發：後端新增 use case/Repository 前先補測試；Web 端關鍵流程補單元與 E2E
- 安全優先：httpOnly cookie（session）、權限檢查、CSRF/同源策略、XSS/輸入驗證、signed URL 上傳流程
- 安全優先：httpOnly cookie（cookie-JWT：access/refresh）、權限檢查、CSRF/同源策略、XSS/輸入驗證、signed URL 上傳流程
- DDD（後端）：Domain/Application/Infrastructure/Presentation 分層與依賴規則遵守

## Project Structure

### Documentation (this feature)

```text
specs/001-posts-first-poc/
├── plan.md              # This file
├── research.md          # (可選) Phase 0：釐清現況與可重用模組
├── data-model.md        # (可選) Phase 1：V2 資料模型草圖
├── quickstart.md        # (可選) Phase 1：Web POC 啟動方式
├── openapi/openapi.json # (後端變更後) 由 FastAPI 生成並提交
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
apps/
├── backend/             # FastAPI + PostgreSQL
├── mobile/              # 既有（本 POC 不以 mobile 為主）
└── web/                 # [NEW] Next.js Web POC

openapi/
└── openapi.json         # 後端生成 snapshot

gateway/
└── kong/                # API Gateway（本地/POC）
```

**Structure Decision**: 新增 `apps/web` 作為 Web POC；後端沿用 `apps/backend`。

## Phases & Milestones

### Phase 0 — Repository & API surface research (0.5–1 day)

- 盤點後端現有模組（identity/profile、media upload、posts 相關）可重用的部分
- 盤點 `openapi/openapi.json` 目前是否已有可用端點；缺口列入 Phase 1
- 決定 Web 的 API 呼叫策略：使用 hey-api 從 `openapi/openapi.json` 生成 TypeScript SDK + TanStack Query hooks（避免手寫 endpoint 串接）

### Phase 1 — Design & Contracts (1–2 days)

- 定義/更新資料模型與端點（以 spec 的 FR 為準）：
  - Posts（含 scope/city_code 與列表篩選）
  - Likes
  - Media（presign/upload/confirm/attach + read signed URLs；長效 TTL，可在登入後查看貼文與相簿圖片）
  - Message Requests + Threads + Messages（唯一對話規則、post_id 引用）
  - Gallery Cards（CRUD + reorder）
  - Quota（keys/defaults、422_LIMIT_EXCEEDED payload）
- 更新並提交 `openapi/openapi.json`（後端產生）

### Phase 2 — Build (Backend + Web) (3–6 days)

**Backend**
- 依 DDD 模組實作：Domain + Use Cases + Repositories + Routers
- Auth：提供 refresh 端點（用 refresh cookie 換發新的 access cookie），支援前端無感續期
- 配額：在 create post / attach media / create gallery card 等關鍵路徑 enforce
- 測試：use case 單元測試 + repository 整合測試 + 主要 API 路徑整合測試

**Web (apps/web)**
- 登入/Session：NextAuth + Google 登入；前後端驗證使用 httpOnly cookie（符合「所有瀏覽需登入」）
- API Client：使用 hey-api 生成的 TanStack Query SDK（不手寫 API 呼叫）
- API Cookie 傳遞：Web 呼叫後端需能攜帶 credentials（同源或跨域 credentials 設定）
- Token 續期：遇到 401 時以 refresh 端點換發 access cookie，並 retry 原請求（對使用者無感）
- 貼文：列表（global+city）、分類/城市篩選、發文（react-hook-form）
- 媒體：上傳流程 UI（授權→PUT→confirm→attach）
- Like：按讚/取消
- Inbox：Requests/Threads 列表、Thread 訊息列表、發送訊息（可帶 post_id）
- Profile：個人頁、相簿小卡列表、相簿管理（新增/刪除/排序）
- 他人個人頁：從貼文作者入口進入，顯示公開個人資訊 + 相簿小卡（IG 樣式）

### Phase 3 — Verification & Demo (1–2 days)

- E2E：登入→發文（含圖片）→Like→私信作者（Request/Accept）→互傳訊息→新增相簿卡
- 配額驗證：至少覆蓋 `posts_per_day`、`media_file_bytes_max`、`media_bytes_per_month` 的超額錯誤

## Risks & Mitigations

- 需求「所有瀏覽需登入」可能影響 SEO/分享：POC 先接受，後續如需公開瀏覽再擴充
- 媒體流程若缺 confirm/狀態管理易產生幽靈資料：以 confirm 為唯一計費點並嚴格限制 attach
- 訊息唯一對話規則若未落實易產生重複 thread：在後端以唯一性約束/查詢策略保證
