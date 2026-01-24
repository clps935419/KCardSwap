# POC API 清理與測試計劃

## 摘要

檢查 `openapi/openapi.json` 後，發現目前有 **50 個 endpoints**，其中 **23 個不在 POC 範圍內**需要移除。

根據 `specs/001-posts-first-poc/spec.md` 規格：
- **In Scope**: AUTH/PROFILE, POSTS, POST MEDIA, Like, DM+Inbox, Profile Gallery, REPORT/BLOCK
- **Removed**: NEARBY, TRADE, trade-bound ratings (已完成✅)
- **Extra (需移除)**: Cards, Friends, Chats, Interests, Subscriptions, Idols, Admin-login

## 一、API 分析

### ✅ 應保留的 POC Endpoints (~27個)

#### Authentication (3)
- `POST /api/v1/auth/google-login`
- `GET /api/v1/auth/google-callback`
- `POST /api/v1/auth/refresh`

#### Profile (1)
- `GET /api/v1/profile/me`

#### Posts (3)
- `GET /api/v1/posts` - 列表 + 篩選
- `POST /api/v1/posts` - 建立貼文
- `POST /api/v1/posts/{post_id}/like` - Like 功能
- `POST /api/v1/posts/{post_id}/close` - 關閉貼文

#### Gallery (5)
- `GET /api/v1/gallery/cards` - 查看他人相簿
- `GET /api/v1/gallery/cards/me` - 我的相簿
- `POST /api/v1/gallery/cards` - 新增卡片
- `DELETE /api/v1/gallery/cards/{card_id}` - 刪除卡片
- `PUT /api/v1/gallery/cards/reorder` - 排序
- `GET /api/v1/users/{user_id}/gallery/cards` - 查看指定使用者相簿

#### Media (4)
- `POST /api/v1/media/upload-url` - 取得上傳 URL
- `POST /api/v1/media/{media_id}/confirm` - 確認上傳
- `POST /api/v1/media/posts/{post_id}/attach` - 綁定到貼文
- `POST /api/v1/media/gallery/cards/{card_id}/attach` - 綁定到相簿

#### Messages (6)
- `POST /api/v1/message-requests` - 建立訊息請求
- `GET /api/v1/message-requests/inbox` - 查看收到的請求
- `POST /api/v1/message-requests/{request_id}/accept` - 接受請求
- `POST /api/v1/message-requests/{request_id}/decline` - 拒絕請求
- `GET /api/v1/threads` - 對話列表
- `GET /api/v1/threads/{thread_id}/messages` - 訊息列表
- `POST /api/v1/threads/{thread_id}/messages` - 發送訊息

#### Reports & Blocking (3)
- `POST /api/v1/reports` - 檢舉
- `POST /api/v1/friends/block` - 封鎖（FR-025）
- `POST /api/v1/friends/unblock` - 解除封鎖

#### Locations (1)
- `GET /api/v1/locations/cities` - 城市列表

#### Health (2)
- `GET /` - Root
- `GET /health` - Health check
- `GET /api/v1/health` - API health

### ❌ 應移除的非 POC Endpoints (23個)

#### 1. Cards System (5) - 舊卡片系統，已被 Gallery 取代
```
/api/v1/cards/me
/api/v1/cards/quota/status
/api/v1/cards/upload-url
/api/v1/cards/{card_id}
/api/v1/cards/{card_id}/confirm-upload
```
**移除檔案:**
- `apps/backend/app/modules/social/presentation/routers/cards_router.py`
- `apps/backend/app/modules/social/application/use_cases/cards/*`
- `apps/backend/app/modules/social/domain/entities/card.py`
- `apps/backend/app/modules/social/infrastructure/repositories/card_repository_impl.py`
- 相關測試

#### 2. Friends System (3) - 好友功能不在 POC，只保留 block/unblock
```
/api/v1/friends (GET - 好友列表)
/api/v1/friends/request (POST - 發送好友請求)
/api/v1/friends/{friendship_id}/accept (POST - 接受好友)
```
**修改檔案:**
- `apps/backend/app/modules/social/presentation/routers/friends_router.py`
  - 只保留 `/block` 和 `/unblock` endpoints
  - 移除好友請求相關功能

#### 3. Chats System (3) - 舊聊天系統，已被 Message Threads 取代
```
/api/v1/chats
/api/v1/chats/{room_id}/messages
/api/v1/chats/{room_id}/messages/{message_id}/read
```
**移除檔案:**
- `apps/backend/app/modules/social/presentation/routers/chat_router.py`
- `apps/backend/app/modules/social/application/use_cases/chat/*`
- `apps/backend/app/modules/social/domain/entities/chat_room.py`, `message.py`
- `apps/backend/app/modules/social/infrastructure/repositories/chat_room_repository_impl.py`, `message_repository_impl.py`
- 相關測試

#### 4. Post Interests (5) - 貼文興趣表達不在 POC
```
/api/v1/posts/{post_id}/interest
/api/v1/posts/{post_id}/interests
/api/v1/posts/{post_id}/interests/{interest_id}
/api/v1/posts/{post_id}/interests/{interest_id}/accept
/api/v1/posts/{post_id}/interests/{interest_id}/reject
```
**修改檔案:**
- `apps/backend/app/modules/posts/presentation/routers/posts_router.py`
  - 移除所有 interest 相關 endpoints
**移除檔案:**
- `apps/backend/app/modules/posts/application/use_cases/express_interest_use_case.py`
- `apps/backend/app/modules/posts/application/use_cases/accept_interest_use_case.py`
- `apps/backend/app/modules/posts/application/use_cases/reject_interest_use_case.py`
- `apps/backend/app/modules/posts/application/use_cases/list_post_interests_use_case.py`
- `apps/backend/app/modules/posts/domain/entities/post_interest.py`
- 相關測試

#### 5. Subscriptions (3) - 不是核心 POC
```
/api/v1/subscriptions/expire-subscriptions
/api/v1/subscriptions/status
/api/v1/subscriptions/verify-receipt
```
**移除檔案:**
- `apps/backend/app/modules/identity/presentation/routers/subscription_router.py`
- `apps/backend/app/modules/identity/application/use_cases/subscription/*`
- 相關 models, repositories, tests

#### 6. Idols (1) - 不在 POC 範圍
```
/api/v1/idols/groups
```
**移除檔案:**
- `apps/backend/app/modules/identity/presentation/routers/idols_router.py`
- 相關 use cases, repositories, tests

#### 7. Admin Login (1) - Web POC 不需要
```
/api/v1/auth/admin-login
```
**修改檔案:**
- `apps/backend/app/modules/identity/presentation/routers/auth_router.py`
  - 註解或移除 `/admin-login` endpoint

## 二、清理步驟

### Step 1: 更新 main.py 移除 router 註冊
```python
# apps/backend/app/main.py

# 移除:
# - idols_router
# - cards_router
# - chat_router
# - subscription_router

# 保留:
# - auth_router (移除 admin-login endpoint)
# - profile_router
# - posts_router (移除 interest endpoints)
# - gallery_router
# - media_router
# - message_requests_router
# - threads_router
# - report_router
# - friends_router (只保留 block/unblock)
# - location_router
```

### Step 2: 刪除檔案
按照上述列表逐一刪除不需要的 routers, use cases, entities, repositories, tests。

### Step 3: 清理 module.py 與 __init__.py
移除已刪除 use cases 的依賴注入配置。

### Step 4: 重新生成 OpenAPI
```bash
cd apps/backend
python scripts/generate_openapi.py
```

### Step 5: 驗證
- 檢查 `openapi/openapi.json` 只包含 ~27 個 POC endpoints
- 執行測試確保沒有破壞現有功能
- 更新前端 SDK

## 三、測試策略

### 目標: 100% 覆蓋率

#### 已實作的整合測試 (Phase 4-7)
✅ `tests/integration/modules/social/test_gallery_cards_v2.py`
✅ `tests/integration/modules/media/test_media_upload_confirm_attach.py`
✅ `tests/integration/modules/social/test_message_requests_v2.py`
✅ `tests/integration/modules/posts/test_post_likes_v2.py`

#### 需補充的測試

**1. Gallery Cards 完整測試**
```python
# tests/integration/modules/social/test_gallery_cards_comprehensive.py

class TestGalleryCardsComprehensive:
    # 邊界案例
    - test_create_card_at_quota_limit
    - test_create_card_exceeds_quota
    - test_reorder_with_invalid_positions
    - test_delete_non_existent_card
    - test_reorder_empty_gallery
    
    # 併發測試
    - test_concurrent_creates
    - test_concurrent_reorders
    
    # 權限測試
    - test_cannot_delete_others_card
    - test_cannot_reorder_others_gallery
    
    # 資料完整性
    - test_display_order_gaps_handled
    - test_display_order_uniqueness
```

**2. Media Upload 完整測試**
```python
# tests/integration/modules/media/test_media_comprehensive.py

class TestMediaComprehensive:
    # 配額測試
    - test_file_size_at_limit
    - test_file_size_exceeds_limit
    - test_monthly_bytes_at_limit
    - test_monthly_bytes_exceeds_limit
    
    # 生命週期測試
    - test_pending_media_cannot_attach
    - test_confirmed_media_can_attach
    - test_attached_media_cannot_reattach
    - test_expired_presigned_url
    
    # 錯誤處理
    - test_confirm_non_existent_media
    - test_attach_to_non_existent_post
    - test_attach_others_media
```

**3. Message Threads 完整測試**
```python
# tests/integration/modules/social/test_messages_comprehensive.py

class TestMessagesComprehensive:
    # 唯一性測試
    - test_duplicate_request_returns_existing
    - test_thread_uniqueness_per_user_pair
    
    # 隱私測試
    - test_blocked_user_cannot_message
    - test_stranger_message_when_disabled
    - test_accept_creates_thread
    
    # 訊息測試
    - test_message_ordering
    - test_message_pagination
    - test_message_with_post_reference
```

**4. Post Likes 完整測試**
```python
# tests/integration/modules/posts/test_likes_comprehensive.py

class TestLikesComprehensive:
    # 冪等性測試
    - test_double_like_idempotent
    - test_like_unlike_like
    
    # 計數測試
    - test_like_count_accuracy
    - test_liked_by_me_flag
    - test_concurrent_likes
    
    # 權限測試
    - test_cannot_like_own_post
    - test_can_unlike_own_like
```

**5. Posts 完整測試**
```python
# tests/integration/modules/posts/test_posts_comprehensive.py

class TestPostsComprehensive:
    # 範圍與篩選
    - test_global_shows_all
    - test_city_filter_works
    - test_category_filter
    - test_combined_filters
    
    # 配額測試
    - test_posts_per_day_limit
    - test_quota_resets_at_midnight
    
    # 權限測試
    - test_require_login_to_view
    - test_require_login_to_create
    - test_close_own_post
    - test_cannot_close_others_post
```

**6. Unit Tests for Domain Logic**
```python
# tests/unit/modules/social/domain/test_gallery_card.py
# tests/unit/modules/media/domain/test_media_asset.py
# tests/unit/modules/social/domain/test_message_thread.py
# tests/unit/modules/posts/domain/test_post_like.py
```

### 測試執行
```bash
# 執行所有測試
pytest tests/ --cov=app --cov-report=html --cov-report=term

# 只執行整合測試
pytest tests/integration/ -v

# 只執行單元測試
pytest tests/unit/ -v

# 檢查覆蓋率
coverage report
```

## 四、預期結果

### Before
- Endpoints: 50
- 包含: NEARBY (已移除), TRADE (已移除), Rating (已移除), Cards, Friends, Chats, Interests, Subscriptions, Idols

### After
- Endpoints: ~27
- 只包含 POC 核心功能: AUTH, PROFILE, POSTS, GALLERY, MEDIA, MESSAGES, REPORTS, BLOCKING, LOCATIONS

### 測試覆蓋率目標
- Unit Tests: 100%
- Integration Tests: 100%
- Overall Coverage: 100%

## 五、風險與注意事項

### 風險
1. **依賴關係**: 某些要移除的功能可能被其他模組依賴
2. **測試破壞**: 移除程式碼會導致現有測試失敗
3. **資料庫遷移**: 可能需要移除對應的資料表和欄位
4. **前端影響**: 前端可能仍在使用被移除的 API

### 建議
1. **分階段進行**: 每次移除一個模組，測試後再繼續
2. **保留分支**: 在新分支上進行清理，確保可以回滾
3. **通知團隊**: 確認這些功能確實不需要再移除
4. **更新文件**: 更新 API 文件和前端 SDK

## 六、時程估計

### Phase 1: API 清理 (1-2 days)
- 移除非 POC routers
- 清理相關檔案
- 重新生成 OpenAPI
- 驗證系統仍可運行

### Phase 2: 測試補充 (2-3 days)
- 撰寫 comprehensive integration tests
- 撰寫 unit tests
- 達到 100% 覆蓋率
- 執行所有測試確保通過

### Total: 3-5 days

## 七、執行檢查清單

- [ ] 備份當前分支
- [ ] 創建清理分支
- [ ] 更新 main.py 移除 router 註冊
- [ ] 刪除 Cards 相關檔案
- [ ] 刪除 Chats 相關檔案
- [ ] 刪除 Subscriptions 相關檔案
- [ ] 刪除 Idols 相關檔案
- [ ] 移除 Post Interests 功能
- [ ] 精簡 Friends Router
- [ ] 移除 Admin Login
- [ ] 清理 module.py 依賴注入
- [ ] 清理 __init__.py imports
- [ ] 重新生成 OpenAPI
- [ ] 驗證 endpoint 數量 (~27)
- [ ] 撰寫 Gallery comprehensive tests
- [ ] 撰寫 Media comprehensive tests
- [ ] 撰寫 Messages comprehensive tests
- [ ] 撰寫 Likes comprehensive tests
- [ ] 撰寫 Posts comprehensive tests
- [ ] 撰寫 Domain unit tests
- [ ] 執行所有測試
- [ ] 檢查覆蓋率達 100%
- [ ] 更新前端 SDK
- [ ] Code review
- [ ] Merge to main branch

---

**文件建立日期**: 2026-01-24
**狀態**: 規劃中
**負責人**: @copilot
