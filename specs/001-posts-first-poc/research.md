# Research: API Gap Analysis for Posts-first POC

**Date**: 2026-01-23  
**Task**: T009 - 盤點現有 API 與本 POC 規格缺口

## Executive Summary

本文件記錄現有後端 API 與 POC 規格的差異分析，並提供明確的處理策略。

## Current API Inventory

### 已存在的模組與路由

基於 `apps/backend/app/main.py` 的註冊，目前有以下模組：

1. **Identity Module** (保留)
   - `/api/v1/auth/*` - 認證相關 (需調整為 cookie-JWT)
   - `/api/v1/profile/*` - 個人資料
   - `/api/v1/idols` - 偶像清單
   - `/api/v1/subscription/*` - 訂閱管理

2. **Social Module** (需要調整/移除部分)
   - `/api/v1/cards/*` - 卡片管理 (需重構為相簿卡片)
   - `/api/v1/friends/*` - 好友關係 (保留)
   - `/api/v1/chat/*` - 聊天室 (需重構為 Message Requests + Threads)
   - `/api/v1/ratings/*` - **❌ 移除** (POC 不需要評分)
   - `/api/v1/reports/*` - 檢舉功能 (保留)
   - `/api/v1/nearby/*` - **❌ 移除/停用** (POC 不需要附近搜尋)
   - `/api/v1/trade/*` - **❌ 移除/停用** (POC 不需要交換功能)

3. **Posts Module** (需大幅調整)
   - `/api/v1/posts/*` - 城市貼文板 (需改為 scope=global/city + 分類)

4. **Locations Module** (保留)
   - `/api/v1/cities` - 城市清單 (保留)

## POC 需要的 API (依規格)

### 1. Auth (Cookie-JWT)

**需要調整**:
- ✅ 既有: `POST /api/v1/auth/google-login` (可能需要調整回傳格式以支援 cookie)
- ✅ 既有: `POST /api/v1/auth/refresh` (需調整為讀取 refresh cookie 並設定 access cookie)
- ❌ 缺少: Cookie 設定邏輯 (需在 config.py 新增 cookie 相關設定)

**處理策略**:
- 更新 `app/modules/identity/presentation/routers/auth_router.py` 的 refresh endpoint
- 更新 `app/config.py` 新增 cookie 名稱、TTL、SameSite、Secure 設定
- 新增 `app/shared/presentation/deps/require_user.py` 作為統一的登入檢查依賴

### 2. Posts (Global/City + Category + Like)

**需要調整**:
現有 `posts_router.py` 是針對城市板且包含 interest 功能 (類似交換請求)，需要：

- ✅ 既有: `POST /api/v1/posts` (需調整 schema 支援 scope/city_code/category)
- ✅ 既有: `GET /api/v1/posts` (需調整查詢支援 global 與 city 篩選)
- ❌ 缺少: Like 功能 (`POST /api/v1/posts/{post_id}/like`, `DELETE /api/v1/posts/{post_id}/like`)
- ❌ 缺少: 貼文附圖支援 (需要 media 模組)
- ⚠️ 移除: Interest 相關端點 (express_interest/accept_interest/reject_interest) → POC 不需要

**處理策略**:
- 調整 `app/modules/posts/domain/models/post.py` 支援 scope/city_code/category
- 新增 `app/modules/posts/domain/models/post_enums.py` (PostCategory, PostScope)
- 調整 `app/modules/posts/presentation/schemas/post_schemas.py`
- 調整 `app/modules/posts/infrastructure/repositories/post_repository.py` 查詢邏輯
- 新增 `app/modules/posts/domain/models/post_like.py`
- 新增 `app/modules/posts/infrastructure/repositories/post_like_repository.py`
- 更新 posts_router.py 的 endpoints

### 3. Media (Presign + Upload + Confirm + Attach)

**需要新建**:
- ❌ 缺少: 完整的 media 模組 (presign/confirm/attach 流程)

**處理策略**:
- 新建 `app/modules/media/` 模組
- 實作 `POST /api/v1/media/upload-url` (presign)
- 實作 `POST /api/v1/media/{media_id}/confirm` (confirm upload)
- 實作 `POST /api/v1/posts/{post_id}/media/attach` (attach to post)
- 實作 `POST /api/v1/gallery/cards/{card_id}/media/attach` (attach to gallery)

### 4. Gallery (個人相簿小卡)

**需要重構**:
現有 `cards_router.py` 是針對交換卡片 (含 trading 狀態)，需要：

- ⚠️ 移除: 交換狀態相關欄位與邏輯
- ✅ 可重用: 基本 CRUD 可部分重用
- ❌ 缺少: Reorder (排序) 功能

**處理策略**:
- 在 social 模組新建 `gallery_card` 子模組 (避免與既有 cards 混淆)
- 實作 `GET /api/v1/users/{user_id}/gallery/cards` (瀏覽他人相簿)
- 實作 `GET /api/v1/gallery/cards/me` (我的相簿)
- 實作 `POST /api/v1/gallery/cards` (新增卡片)
- 實作 `DELETE /api/v1/gallery/cards/{card_id}` (刪除卡片)
- 實作 `PUT /api/v1/gallery/cards/reorder` (排序)

### 5. Messages (Message Requests + Threads + Inbox)

**需要重構**:
現有 `chat_router.py` 可能是簡單聊天室，需要改為 Message Request 流程：

- ❌ 缺少: Message Request (pending/accepted/declined 狀態)
- ❌ 缺少: Thread uniqueness (同一對 user 唯一對話)
- ❌ 缺少: Inbox API (區分 Requests vs Threads)

**處理策略**:
- 新建 `app/modules/social/domain/models/message_request.py`
- 新建 `app/modules/social/domain/models/message.py` (支援 post_id 引用)
- 實作 `POST /api/v1/message-requests` (建立請求)
- 實作 `GET /api/v1/message-requests/inbox` (收到的請求)
- 實作 `POST /api/v1/message-requests/{request_id}/accept`
- 實作 `POST /api/v1/message-requests/{request_id}/decline`
- 實作 `GET /api/v1/threads` (已接受的對話列表)
- 實作 `GET /api/v1/threads/{thread_id}/messages`
- 實作 `POST /api/v1/threads/{thread_id}/messages`

### 6. Quota (配額檢查)

**需要新建**:
- ❌ 缺少: 統一配額 domain 介面
- ❌ 缺少: 422_LIMIT_EXCEEDED 錯誤格式

**處理策略**:
- 新建 `app/shared/domain/quota/` 目錄
- 新建 `app/shared/presentation/errors/limit_exceeded.py`
- 實作 `posts_per_day` 配額檢查
- 實作 `media_file_bytes_max` 與 `media_bytes_per_month` 配額檢查

## 需要移除/停用的 API

### 明確移除 (不得出現在 openapi.json)

1. **NEARBY 附近搜尋** (`/api/v1/nearby/*`)
   - 路由: `app/modules/social/presentation/routers/nearby_router.py`
   - 策略: 從 `main.py` 移除註冊，不生成到 OpenAPI

2. **TRADE 交換功能** (`/api/v1/trade/*`)
   - 路由: `app/modules/social/presentation/routers/trade_router.py`
   - 策略: 從 `main.py` 移除註冊，不生成到 OpenAPI

3. **RATING 評分功能** (`/api/v1/ratings/*`)
   - 路由: `app/modules/social/presentation/routers/rating_router.py`
   - 策略: 從 `main.py` 移除註冊，不生成到 OpenAPI

### 注意事項

- 這些路由的 domain/use case/repository 可以保留在程式碼中 (未來可能重啟)
- 但必須從 `main.py` 移除 `include_router`，確保不出現在 OpenAPI spec
- 任何 schema 中引用到 trade/rating/nearby 的欄位需要移除或標註為 deprecated

## Implementation Checklist

### Phase 2 (Foundational) 執行項目

- [x] T009 完成本文件
- [ ] T010 定義 422_LIMIT_EXCEEDED 錯誤格式
- [ ] T011 實作 require_user 共用依賴
- [ ] T012 新增 cookie-JWT 設定到 config.py
- [ ] T013 調整 auth_router.py 的 refresh endpoint
- [ ] T014 新增 refresh cookie 整合測試
- [ ] T015 建立 quota domain 介面
- [ ] T016 實作 posts_per_day 配額檢查
- [ ] T017 實作 media 配額介面
- [ ] T020 更新 OpenAPI 生成流程文件
- [ ] T021 生成並提交最新 OpenAPI snapshot (移除 NEARBY/TRADE/RATING)

## Conclusion

現有後端已有基礎架構，主要需要：

1. **調整**: Auth (cookie-JWT)、Posts (scope/category/like)
2. **新建**: Media (presign/confirm)、Gallery (reorder)、Messages (requests/threads)、Quota
3. **移除**: Nearby、Trade、Rating 的路由註冊

所有變更需遵守 DDD 分層與測試優先開發原則。
