# 未覆蓋的 API 端點清單

## 📊 總覽

**總 API 端點數**: ~44 個  
**已測試路由器**: 3 個 (idols_router, subscription_router, friends_router部分)  
**未測試路由器**: 11 個  
**預估未覆蓋端點**: ~35-40 個

---

## 🔴 完全未覆蓋的路由器（0% 測試）

### 1. Identity Module

#### ✅ **auth_router.py** (238 行) - 已有部分整合測試
**API 端點**:
- `POST /auth/register` - 用戶註冊
- `POST /auth/login` - 用戶登入
- `POST /auth/logout` - 用戶登出
- `POST /auth/refresh` - 刷新 token

**狀態**: 整合測試已覆蓋，但缺少單元測試

#### 🔴 **profile_router.py** (135 行) - 0% 測試
**API 端點**:
- `GET /profile/me` - 獲取當前用戶資料
- `PUT /profile/me` - 更新用戶資料

**優先級**: ⭐⭐⭐ 高（核心功能）

### 2. Social Module

#### 🔴 **cards_router.py** (377 行，最大文件) - 0% 測試
**API 端點**:
- `POST /cards/upload-url` - 獲取卡片上傳 URL
- `GET /cards/my-cards` - 獲取我的卡片
- `DELETE /cards/{card_id}` - 刪除卡片
- `GET /cards/quota` - 檢查上傳配額
- `POST /cards/{card_id}/confirm` - 確認卡片上傳

**優先級**: ⭐⭐⭐⭐ 最高（最大文件，核心社交功能）

#### 🔴 **chat_router.py** (393 行，第二大文件) - 0% 測試
**API 端點**:
- `GET /chat/rooms` - 獲取聊天室列表
- `GET /chat/rooms/{room_id}/messages` - 獲取聊天室訊息
- `POST /chat/rooms/{room_id}/messages` - 發送訊息
- `POST /chat/rooms/{room_id}/mark-read` - 標記訊息已讀

**優先級**: ⭐⭐⭐⭐ 最高（最大文件，核心聊天功能）

#### 🟡 **friends_router.py** (119 行) - ~15% 測試
**API 端點**:
- `POST /friends/send-request` - 發送好友請求
- `POST /friends/{user_id}/unblock` - 解除封鎖（✅ 已測試）
- 其他端點未測試

**優先級**: ⭐⭐⭐ 高

#### 🔴 **gallery_router.py** (268 行) - 0% 測試
**API 端點**:
- `GET /gallery` - 獲取畫廊列表
- `GET /gallery/{user_id}` - 獲取特定用戶畫廊
- `POST /gallery/reorder` - 重新排序畫廊
- `DELETE /gallery/{card_id}` - 從畫廊刪除卡片
- `PUT /gallery/{card_id}` - 更新畫廊卡片

**優先級**: ⭐⭐⭐ 高

#### 🔴 **message_requests_router.py** (226 行) - 0% 測試
**API 端點**:
- `POST /message-requests` - 創建訊息請求
- `GET /message-requests/inbox` - 獲取收件箱
- `POST /message-requests/{request_id}/accept` - 接受請求
- `POST /message-requests/{request_id}/decline` - 拒絕請求

**優先級**: ⭐⭐⭐ 高

#### 🔴 **threads_router.py** (152 行) - 0% 測試
**API 端點**:
- `GET /threads` - 獲取對話串列表
- `GET /threads/{thread_id}/messages` - 獲取對話串訊息
- `POST /threads/{thread_id}/messages` - 發送對話串訊息

**優先級**: ⭐⭐⭐ 高

#### 🔴 **report_router.py** (165 行) - 0% 測試
**API 端點**:
- `POST /reports` - 創建檢舉
- `GET /reports` - 獲取檢舉列表

**優先級**: ⭐⭐ 中

### 3. Posts Module

#### 🔴 **posts_router.py** (321 行) - 0% 測試
**API 端點**:
- `POST /posts` - 創建貼文
- `GET /posts` - 獲取貼文列表
- `POST /posts/{post_id}/like` - 按讚
- `POST /posts/{post_id}/comment` - 評論

**優先級**: ⭐⭐⭐⭐ 最高（核心功能）

### 4. Media Module

#### 🔴 **media_router.py** (179 行) - 0% 測試
**API 端點**:
- `POST /media/upload-url` - 獲取媒體上傳 URL
- `POST /media/{media_id}/confirm` - 確認媒體上傳
- `POST /media/attach` - 附加媒體到實體
- `POST /media/{media_id}/delete` - 刪除媒體

**優先級**: ⭐⭐⭐ 高

### 5. Locations Module

#### 🔴 **location_router.py** (86 行) - 0% 測試
**API 端點**:
- `GET /locations/nearby` - 搜尋附近用戶

**優先級**: ⭐⭐ 中

---

## 📋 詳細未覆蓋清單（按優先級）

### 🔥 優先級 1：核心大型路由器（~1,090 行，估計需要 8-10h）

1. **cards_router.py** (377 行)
   - 5 個端點未測試
   - 卡片上傳與管理核心功能

2. **chat_router.py** (393 行)
   - 4 個端點未測試
   - 聊天核心功能

3. **posts_router.py** (321 行)
   - 4+ 個端點未測試
   - 貼文核心功能

**預估覆蓋率提升**: +5-7% → 78-80%

### ⚡ 優先級 2：中型重要路由器（~850 行，估計需要 5-7h）

4. **gallery_router.py** (268 行)
   - 5 個端點未測試

5. **message_requests_router.py** (226 行)
   - 4 個端點未測試

6. **media_router.py** (179 行)
   - 4 個端點未測試

7. **threads_router.py** (152 行)
   - 3 個端點未測試

**預估覆蓋率提升**: +4-5% → 82-85%

### 🎯 優先級 3：小型路由器（~505 行，估計需要 3-4h）

8. **profile_router.py** (135 行)
   - 2 個端點未測試

9. **friends_router.py** (119 行剩餘 ~100)
   - ~3 個端點未測試

10. **report_router.py** (165 行)
    - 2 個端點未測試

11. **location_router.py** (86 行)
    - 1 個端點未測試

**預估覆蓋率提升**: +2-3% → 87-88%

---

## 📈 覆蓋率提升路線圖

### 當前狀態: 73-75%

| 階段 | 目標路由器 | 預估工作量 | 覆蓋率目標 |
|------|-----------|-----------|-----------|
| **階段 5** | cards_router + chat_router + posts_router | 8-10h | 78-82% |
| **階段 6** | gallery + message_requests + media + threads | 5-7h | 82-87% |
| **階段 7** | profile + friends + report + location | 3-4h | 87-90% |

### 總計
- **剩餘路由器**: 11 個
- **剩餘端點**: ~35-40 個
- **預估工作量**: 16-21 小時
- **最終覆蓋率**: 87-90%（僅路由器）

---

## 🔧 其他未覆蓋組件

除了路由器外，還有：

### Use Case Dependencies
- `use_case_deps.py` (120 行) - 0% 測試

### External Services
- Google OAuth Service (~38% 覆蓋)
- FCM Service (~23% 覆蓋)
- GCS Operations (部分覆蓋)

### Repository Implementations
- Profile Repository (~33% 覆蓋)
- Thread Repository (~32% 覆蓋)
- Refresh Token Repository (~32% 覆蓋)

### Domain Services
- 各種低覆蓋的 domain services

**預估額外覆蓋率提升**: +8-10% → 95-100%

---

## 💡 建議策略

### 快速提升策略（3-4 週達到 90%）

**第 1 週**: 攻克 3 大路由器
- cards_router.py
- chat_router.py
- posts_router.py
- **目標**: 80%

**第 2 週**: 補齊中型路由器
- gallery_router.py
- message_requests_router.py
- media_router.py
- threads_router.py
- **目標**: 85%

**第 3 週**: 完成小型路由器 + dependencies
- 剩餘所有路由器
- use_case_deps.py
- **目標**: 90%

**第 4 週**: 補齊 services 和 repositories
- External services
- Repository implementations
- **目標**: 95%+

---

## 📝 測試模板建議

針對路由器測試，建議使用以下模式：

```python
from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient

class TestCardsRouter:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()
    
    def test_upload_url_endpoint(self, mock_use_case):
        # Arrange
        mock_use_case.execute.return_value = expected_result
        
        # Act
        response = client.post("/cards/upload-url", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response
```

---

**生成日期**: 2026-01-24  
**當前覆蓋率**: 73-75%  
**未覆蓋路由器**: 11 個  
**未覆蓋端點**: ~35-40 個  
**達到 90% 預估**: 16-21 小時
