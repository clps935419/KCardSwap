# Priority 5 - 測試缺漏分析報告

## 📊 當前測試狀態總覽

### 已完成的 E2E 測試 (88 tests)

| 模組 | 路由器 | 測試數 | 狀態 |
|------|--------|--------|------|
| Identity | Subscription | 10 | ✅ 完成 |
| Identity | Profile | 9 | ✅ 完成 |
| Identity | Idols | 3 | ✅ 完成 |
| Social | Cards | 17 | ✅ 完成 |
| Social | Friends | 12 | ✅ 完成 |
| Social | Chat | 18 | ✅ 完成 |
| Social | Threads | 19 | ✅ 完成 |
| **總計** | **7 routers** | **88 tests** | ✅ |

**注意**: 實際測試數量為 88 個（含 fixture 方法），純測試函數約 73 個。

---

## ❌ 缺漏分析：按路由器比對

### 1. Auth Router (Priority: 高) - **完全缺漏**

**現有端點** (4 endpoints):
```python
POST /api/v1/auth/google-callback     # PKCE OAuth flow
POST /api/v1/auth/google-login        # Implicit OAuth flow  
POST /api/v1/auth/refresh             # Refresh token
POST /api/v1/auth/logout              # Logout
```

**已有測試** (非 E2E):
- ✅ `test_auth_flow.py` - Google OAuth PKCE flow (7 tests) - **但這不是 E2E 測試**
- ✅ `test_auth_refresh_cookie.py` - Refresh token flow (3 tests) - **但這不是 E2E 測試**

**缺少的 E2E 測試** (建議 8-12 tests):
- ❌ POST /auth/google-callback 的完整 E2E 流程
- ❌ POST /auth/google-login 的完整 E2E 流程
- ❌ POST /auth/refresh 的完整 E2E 流程
- ❌ POST /auth/logout 的完整 E2E 流程
- ❌ 各端點的錯誤場景 (401, 400, 422)

**建議檔案**: `test_auth_router_e2e.py`

---

### 2. Subscription Router - ⚠️ 部分缺漏

**現有端點** (3 endpoints):
```python
POST /api/v1/subscriptions/verify-receipt     # ✅ 已測試
GET  /api/v1/subscriptions/status             # ✅ 已測試
POST /api/v1/subscriptions/expire-subscriptions # ✅ 已測試
```

**已測試** (10 tests): ✅ 完整

**潛在補充**:
- ⚠️ 可增加更多邊界條件測試（如收據重複使用、多平台測試）

---

### 3. Profile Router - ✅ 完整

**現有端點** (2 endpoints):
```python
GET /api/v1/profile/me  # ✅ 已測試
PUT /api/v1/profile/me  # ✅ 已測試
```

**已測試** (9 tests): ✅ 完整涵蓋

---

### 4. Idols Router - ✅ 完整

**現有端點** (1 endpoint):
```python
GET /api/v1/idols/groups  # ✅ 已測試
```

**已測試** (3 tests): ✅ 完整涵蓋

---

### 5. Cards Router - ⚠️ 部分缺漏

**現有端點** (5 endpoints):
```python
POST /api/v1/cards/upload-url           # ✅ 已測試
GET  /api/v1/cards/me                   # ✅ 已測試
DELETE /api/v1/cards/{card_id}          # ✅ 已測試
POST /api/v1/cards/{card_id}/confirm-upload # ✅ 已測試
GET  /api/v1/cards/quota/status         # ✅ 已測試
```

**已測試** (17 tests): ✅ 涵蓋所有端點

**潛在補充**:
- ⚠️ 可增加更複雜的場景（如並發上傳、配額邊界測試）

---

### 6. Friends Router - ⚠️ 部分缺漏

**現有端點** (2 endpoints):
```python
POST /api/v1/friends/block    # ✅ 已測試
POST /api/v1/friends/unblock  # ✅ 已測試
```

**已測試** (12 tests): ✅ 涵蓋所有端點

**PRIORITY_5_ROADMAP 提到的缺漏端點**:
```python
GET    /api/friends           # ❌ 不存在於實際路由器中
DELETE /api/friends/{friend_id} # ❌ 不存在於實際路由器中
```

**分析**: 路由器實際上只實作了 block/unblock，沒有好友列表和刪除功能。
- 這些端點可能在其他路由器（如 gallery_router 或未來的 friends 管理）

---

### 7. Chat Router - ✅ 完整

**現有端點** (4 endpoints):
```python
GET  /api/v1/chats                              # ✅ 已測試
GET  /api/v1/chats/{room_id}/messages           # ✅ 已測試
POST /api/v1/chats/{room_id}/messages           # ✅ 已測試
POST /api/v1/chats/{room_id}/messages/{message_id}/read # ✅ 已測試
```

**已測試** (18 tests): ✅ 完整涵蓋

---

### 8. Threads Router - ✅ 完整

**現有端點** (3 endpoints):
```python
GET  /api/v1/threads                     # ✅ 已測試
GET  /api/v1/threads/{thread_id}/messages # ✅ 已測試
POST /api/v1/threads/{thread_id}/messages # ✅ 已測試
```

**已測試** (19 tests): ✅ 完整涵蓋

---

### 9. Posts Router (Priority: 高) - **完全缺漏 E2E**

**現有端點** (4 endpoints):
```python
GET  /api/v1/posts               # List posts
POST /api/v1/posts               # Create post
POST /api/v1/posts/{post_id}/like   # Like post
POST /api/v1/posts/{post_id}/unlike # Unlike post
```

**已有測試** (非完整 E2E):
- ✅ `test_posts_create_and_list_v2.py` (部分整合測試)
- ✅ `test_post_likes_v2.py` (部分整合測試)

**缺少的 E2E 測試** (建議 10-15 tests):
- ❌ 完整的 CRUD E2E 流程測試
- ❌ Like/Unlike 的完整場景
- ❌ 權限控制測試
- ❌ 分頁和篩選測試

**建議檔案**: `test_posts_router_e2e.py`

---

### 10. Locations Router (Priority: 中) - **完全缺漏 E2E**

**現有端點** (1 endpoint):
```python
GET /api/v1/locations/cities  # List cities
```

**已有測試** (非完整 E2E):
- ✅ `test_city_list_flow.py` (1 test) - 但不是完整的 E2E 測試

**缺少的 E2E 測試** (建議 3-5 tests):
- ❌ 獲取城市列表的各種場景
- ❌ 篩選和搜尋測試
- ❌ 錯誤處理測試

**建議檔案**: `test_location_router_e2e.py`

---

### 11. Media Router (Priority: 中) - **完全缺漏 E2E**

**現有端點** (4 endpoints):
```python
POST /api/v1/media/upload-url         # Generate upload URL
POST /api/v1/media/{media_id}/confirm # Confirm upload
POST /api/v1/media/{media_id}/attach  # Attach to entity
POST /api/v1/media/{media_id}/detach  # Detach from entity (假設)
```

**已有測試** (非完整 E2E):
- ✅ `test_media_upload_confirm_attach.py` (3 tests) - 但不是完整的 E2E 測試

**缺少的 E2E 測試** (建議 8-12 tests):
- ❌ 完整的上傳流程 E2E
- ❌ 附加和分離媒體的 E2E
- ❌ 錯誤場景和權限測試

**建議檔案**: `test_media_router_e2e.py`

---

### 12. Gallery Router (Priority: 中) - **完全缺漏 E2E**

**現有端點** (5 endpoints):
```python
POST   /api/v1/gallery/cards           # Create gallery card
GET    /api/v1/gallery/cards/me        # Get my cards
GET    /api/v1/users/{user_id}/gallery/cards # Get user's cards
PUT    /api/v1/gallery/cards/{card_id} # Update card
DELETE /api/v1/gallery/cards/{card_id} # Delete card
```

**已有測試** (非完整 E2E):
- ✅ `test_gallery_cards_v2.py` (多個測試) - 但不是完整的 E2E 測試

**缺少的 E2E 測試** (建議 10-15 tests):
- ❌ 完整的 CRUD E2E 流程
- ❌ 跨用戶訪問測試
- ❌ 權限和隱私測試

**建議檔案**: `test_gallery_router_e2e.py`

---

### 13. Message Requests Router (Priority: 中) - **完全缺漏 E2E**

**現有端點** (4 endpoints):
```python
GET  /api/v1/message-requests/inbox            # Get inbox
POST /api/v1/message-requests                  # Create request
POST /api/v1/message-requests/{request_id}/accept  # Accept request
POST /api/v1/message-requests/{request_id}/decline # Decline request
```

**已有測試** (非完整 E2E):
- ✅ `test_message_requests_v2.py` (多個測試) - 但不是完整的 E2E 測試

**缺少的 E2E 測試** (建議 8-12 tests):
- ❌ 完整的請求流程 E2E
- ❌ Accept/Decline 場景
- ❌ 權限和狀態測試

**建議檔案**: `test_message_requests_router_e2e.py`

---

### 14. Report Router (Priority: 低) - **完全缺漏 E2E**

**現有端點** (2 endpoints):
```python
POST /api/v1/reports        # Create report
GET  /api/v1/reports/types  # Get report types
```

**已有測試** (非完整 E2E):
- ✅ `test_report_flow.py` (2 tests) - 但不是完整的 E2E 測試

**缺少的 E2E 測試** (建議 4-6 tests):
- ❌ 完整的舉報流程 E2E
- ❌ 各種舉報類型測試
- ❌ 錯誤處理

**建議檔案**: `test_report_router_e2e.py`

---

## 📋 總結：缺漏測試清單

### 🔴 高優先級缺漏 (必須補充)

1. **Auth Router E2E** - 0/4 endpoints tested
   - 建議新增 8-12 tests
   - 檔案: `test_auth_router_e2e.py`

2. **Posts Router E2E** - 0/4 endpoints tested  
   - 建議新增 10-15 tests
   - 檔案: `test_posts_router_e2e.py`

### 🟡 中優先級缺漏 (建議補充)

3. **Gallery Router E2E** - 0/5 endpoints tested
   - 建議新增 10-15 tests
   - 檔案: `test_gallery_router_e2e.py`

4. **Media Router E2E** - 0/4 endpoints tested
   - 建議新增 8-12 tests
   - 檔案: `test_media_router_e2e.py`

5. **Message Requests Router E2E** - 0/4 endpoints tested
   - 建議新增 8-12 tests
   - 檔案: `test_message_requests_router_e2e.py`

6. **Locations Router E2E** - 0/1 endpoint tested
   - 建議新增 3-5 tests
   - 檔案: `test_location_router_e2e.py`

### 🟢 低優先級缺漏 (可選補充)

7. **Report Router E2E** - 0/2 endpoints tested
   - 建議新增 4-6 tests
   - 檔案: `test_report_router_e2e.py`

---

## 📊 測試覆蓋率預估

### 當前狀態
- **已測試端點**: 20/37 endpoints (54%)
- **E2E 測試數**: 88 tests (實際測試函數 ~73)
- **已測試路由器**: 7/14 routers (50%)

### 補充所有缺漏後預估
- **總端點**: 37 endpoints
- **總 E2E 測試**: 150-200 tests
- **路由器覆蓋**: 14/14 routers (100%)

### 覆蓋率目標
- **Priority 5 原定目標**: 92-95% (需要 30-40 tests)
- **已達成**: 88 tests ✅ (超過目標)
- **但是**: 某些重要路由器（Auth, Posts）完全未測試

---

## 🎯 建議行動計劃

### Phase 1: 補充高優先級測試 (2-3 小時)
1. `test_auth_router_e2e.py` (8-12 tests)
2. `test_posts_router_e2e.py` (10-15 tests)

### Phase 2: 補充中優先級測試 (4-5 小時)  
3. `test_gallery_router_e2e.py` (10-15 tests)
4. `test_media_router_e2e.py` (8-12 tests)
5. `test_message_requests_router_e2e.py` (8-12 tests)
6. `test_location_router_e2e.py` (3-5 tests)

### Phase 3: 補充低優先級測試 (1 小時)
7. `test_report_router_e2e.py` (4-6 tests)

---

## 📝 使用 Makefile 執行測試

根據 Makefile，測試資料庫已經配置好：

```bash
# 初始化測試資料庫
make init-test-db

# 執行所有整合測試
make test-integration

# 執行 Identity 模組測試
make test-integration-identity

# 執行 Social 模組測試
make test-integration-social

# 執行帶覆蓋率的整合測試
make test-coverage-integration
```

測試資料庫 URL:
```
postgresql+asyncpg://kcardswap:kcardswap@localhost:5432/kcardswap_test
```

---

**報告生成時間**: 2026-01-25  
**分析範圍**: Priority 5 E2E Tests  
**結論**: 已完成 7/14 路由器的 E2E 測試，建議優先補充 Auth 和 Posts 路由器的測試
