# 修改摘要：為 API 回應添加 nickname 和 avatar_url

## 目標
所有 API 回應中包含 user_id 相關欄位時，必須同時提供 nickname 和 avatar_url。
Web UI 不再顯示 user_id，改為顯示 nickname 和 avatar。

## Backend 修改

### 1. Schema 更新 (`message_schemas.py`)

#### MessageRequestResponse
新增欄位：
- `sender_nickname: Optional[str]`
- `sender_avatar_url: Optional[str]`
- `recipient_nickname: Optional[str]`
- `recipient_avatar_url: Optional[str]`

#### ThreadResponse
新增欄位：
- `user_a_nickname: Optional[str]`
- `user_a_avatar_url: Optional[str]`
- `user_b_nickname: Optional[str]`
- `user_b_avatar_url: Optional[str]`

#### ThreadMessageResponse
新增欄位：
- `sender_nickname: Optional[str]`
- `sender_avatar_url: Optional[str]`

### 2. Router 更新

#### message_requests_router.py
新增輔助函數 `_get_user_profile_data()` 來取得使用者的 nickname 和 avatar_url。

更新的端點：
- `POST /message-requests` - 建立請求時填充 sender 和 recipient 的 profile 資料
- `GET /message-requests/inbox` - 收件匣中的所有請求都包含完整 profile 資料
- `GET /message-requests/sent` - 已送出請求中包含完整 profile 資料
- `POST /message-requests/{id}/accept` - 接受請求時回傳的 request 和 thread 都包含 profile 資料
- `POST /message-requests/{id}/decline` - 拒絕請求時回傳包含 profile 資料

#### threads_router.py
新增輔助函數 `_get_user_profile_data()` 來取得使用者的 nickname 和 avatar_url。

更新的端點：
- `GET /threads` - 所有 thread 都包含 user_a 和 user_b 的 profile 資料
- `GET /threads/{thread_id}/messages` - 所有訊息都包含 sender 的 profile 資料
- `POST /threads/{thread_id}/messages` - 送出訊息時回傳包含 sender 的 profile 資料

#### chat_router.py
更新的端點：
- `GET /chats` - 聊天室的 participants 現在會從 ProfileRepositoryImpl 取得實際的 nickname 和 avatar_url

## Web Frontend 修改

### 1. 新增元件

#### UserAvatar (`components/ui/user-avatar.tsx`)
可重複使用的頭像元件，功能：
- 優先顯示 avatar_url（使用 Next.js Image 組件）
- 無頭像時顯示 nickname 或 userId 的首字母
- 支援三種尺寸：sm, md, lg
- 完全符合 Biome linting 規範

### 2. 更新元件

#### MessageRequestsList.tsx
- 引入 `UserAvatar` 組件
- 顯示 `sender_nickname`（有 nickname 時）或 fallback 到 `使用者 ${sender_id.slice(0, 8)}`
- 使用 `UserAvatar` 顯示發送者頭像

#### SentRequestsList.tsx
- 引入 `UserAvatar` 組件
- 顯示 `recipient_nickname`（有 nickname 時）或 fallback 到 `使用者 ${recipient_id.slice(0, 8)}`
- 使用 `UserAvatar` 顯示接收者頭像

#### ThreadsList.tsx
- 引入 `UserAvatar` 組件
- 更新 `resolvePeerData()` 函數，同時回傳 peer 的 id, nickname, 和 avatar_url
- 顯示對方的 nickname（有 nickname 時）或 fallback 到 `使用者 ${peerId.slice(0, 8)}`
- 使用 `UserAvatar` 顯示對方頭像

#### MessageList.tsx
- 無需修改（此元件不顯示發送者資訊，只顯示訊息內容）

## SDK 和 Schema 更新

### OpenAPI Schema (`openapi/openapi.json`)
使用 `generate_openapi.py` 腳本重新生成，包含所有新的 schema 欄位。

### Web SDK (`apps/web/src/shared/api/generated/`)
使用 `@hey-api/openapi-ts` 重新生成，TypeScript 型別已更新為包含新欄位。

## 程式碼品質檢查

### Backend
- ✅ Python 語法檢查通過（所有修改的檔案）
- ✅ 使用 ProfileRepositoryImpl 正確取得使用者資料

### Frontend
- ✅ TypeScript 型別檢查通過
- ✅ Biome linting 通過（無警告）
- ✅ 使用 Next.js Image 組件優化圖片載入

## 測試建議

### Backend 測試
1. 測試各個端點是否正確回傳 nickname 和 avatar_url
2. 測試當使用者沒有 profile 時的 fallback 行為（應回傳 null）
3. 確認不會因為取得 profile 失敗而導致整個 API 失敗

### Frontend 測試
1. 在收件匣中接收新的訊息請求，確認顯示發送者 nickname 和 avatar
2. 查看已送出的請求，確認顯示接收者 nickname 和 avatar
3. 在 thread 列表中確認顯示對方的 nickname 和 avatar
4. 測試沒有 avatar_url 時的 fallback 顯示（應顯示首字母）
5. 測試沒有 nickname 時的 fallback 顯示（應顯示 `使用者 ${user_id.slice(0, 8)}`）

## 檔案變更清單

### Backend
- `apps/backend/app/modules/social/presentation/schemas/message_schemas.py`
- `apps/backend/app/modules/social/presentation/routers/message_requests_router.py`
- `apps/backend/app/modules/social/presentation/routers/threads_router.py`
- `apps/backend/app/modules/social/presentation/routers/chat_router.py`

### Frontend
- `apps/web/src/components/ui/user-avatar.tsx` (新增)
- `apps/web/src/features/inbox/components/MessageRequestsList.tsx`
- `apps/web/src/features/inbox/components/SentRequestsList.tsx`
- `apps/web/src/features/inbox/components/ThreadsList.tsx`

### Schema & SDK
- `openapi/openapi.json`
- `apps/web/src/shared/api/generated/types.gen.ts`
- `apps/web/package-lock.json`

## 注意事項

1. **效能考量**：每個 API 回應都會查詢 ProfileRepository 來取得 nickname 和 avatar_url，建議未來考慮：
   - 在 repository 層面加入快取
   - 使用 JOIN 查詢一次取得所有需要的 profile 資料

2. **向後相容性**：所有新增的欄位都是 Optional，因此不會破壞現有的 API 使用者。

3. **Mobile App**：本次修改只針對 Web 前端，Mobile App 可能也需要類似的更新。

4. **錯誤處理**：目前 profile 取得失敗會返回 None，不會影響 API 的主要功能。

5. **未來改進**：
   - 考慮在 entity 層面加入 profile 相關資料
   - 建立專門的 DTO 轉換層來處理 profile 資料的組裝
   - 加入單元測試和整合測試來確保 profile 資料正確填充
