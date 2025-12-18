# Phase 3 (US1) 手動驗證指南 (T065)

**日期**: 2025-12-18  
**目的**: 手動驗證 Phase 3 (User Story 1) 的所有功能是否正常運作

## 前置條件

### 1. 啟動後端服務

```bash
# 方式 1: 使用 Docker Compose (推薦)
cd /path/to/KCardSwap
docker compose up -d

# 方式 2: 本地啟動
cd apps/backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 確認服務狀態

```bash
# 檢查 API 文件
curl http://localhost:8000/docs

# 檢查健康狀態
curl http://localhost:8000/health
```

### 3. 準備測試工具

- **Postman**: 下載並導入 API collection
- **curl**: 命令行工具
- **HTTPie**: 更友好的 HTTP 客戶端 (可選)

---

## 驗收標準

根據 Phase 3 (US1) 的定義，需要驗證以下功能：

- ✓ 使用者可以成功使用 Google 登入並取得 JWT Token
- ✓ 使用者可以查看和更新個人檔案（nickname, bio, avatar）
- ✓ 登入狀態可以通過 JWT 驗證
- ✓ Refresh Token 機制正常運作

---

## 測試流程

### Test 1: Google OAuth Callback (PKCE Flow)

#### 1.1 模擬 PKCE Authorization Code Exchange

**目的**: 驗證後端可以接收 authorization code 和 code_verifier，並與 Google 交換 tokens

**注意**: 此測試需要真實的 Google OAuth code，需要先在前端或測試頁面完成 OAuth 流程

```bash
# 使用 curl
curl -X POST http://localhost:8000/api/v1/auth/google-callback \
  -H "Content-Type: application/json" \
  -d '{
    "code": "4/0AY0e-g7XXXXXXXXXXX",
    "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
    "redirect_uri": "exp://192.168.1.1:19000"
  }'
```

**預期結果**:
```json
{
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  },
  "error": null
}
```

**狀態碼**: 200 OK

#### 1.2 測試驗證錯誤 - 缺少 code

```bash
curl -X POST http://localhost:8000/api/v1/auth/google-callback \
  -H "Content-Type: application/json" \
  -d '{
    "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
  }'
```

**預期結果**: 422 Validation Error

#### 1.3 測試驗證錯誤 - code_verifier 太短

```bash
curl -X POST http://localhost:8000/api/v1/auth/google-callback \
  -H "Content-Type: application/json" \
  -d '{
    "code": "4/0AY0e-g7XXXXXXXXXXX",
    "code_verifier": "short"
  }'
```

**預期結果**: 422 Validation Error (PKCE 規範要求 43-128 字元)

---

### Test 2: Profile 查詢 (GET /profile/me)

#### 2.1 無認證存取 (預期失敗)

```bash
curl -X GET http://localhost:8000/api/v1/profile/me
```

**預期結果**: 401 Unauthorized 或 403 Forbidden

#### 2.2 使用有效 Token 查詢

```bash
# 使用從 Test 1 獲得的 access_token
ACCESS_TOKEN="eyJhbGc..."

curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**預期結果**:
```json
{
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "nickname": null,
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "bio": null,
    "region": null,
    "preferences": {},
    "privacy_flags": {
      "nearby_visible": true,
      "show_online": true,
      "allow_stranger_chat": true
    },
    "created_at": "2025-12-18T08:00:00Z",
    "updated_at": "2025-12-18T08:00:00Z"
  },
  "error": null
}
```

**狀態碼**: 200 OK

---

### Test 3: Profile 更新 (PUT /profile/me)

#### 3.1 完整更新所有欄位

```bash
ACCESS_TOKEN="eyJhbGc..."

curl -X PUT http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "KCardMaster",
    "bio": "熱愛收集卡片的玩家",
    "avatar_url": "https://example.com/my-avatar.jpg",
    "region": "TW-TPE",
    "preferences": {
      "theme": "dark",
      "language": "zh-TW",
      "notifications_enabled": true
    },
    "privacy_flags": {
      "nearby_visible": false,
      "show_online": true,
      "allow_stranger_chat": false
    }
  }'
```

**預期結果**:
```json
{
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "nickname": "KCardMaster",
    "bio": "熱愛收集卡片的玩家",
    "avatar_url": "https://example.com/my-avatar.jpg",
    "region": "TW-TPE",
    "preferences": {
      "theme": "dark",
      "language": "zh-TW",
      "notifications_enabled": true
    },
    "privacy_flags": {
      "nearby_visible": false,
      "show_online": true,
      "allow_stranger_chat": false
    },
    "created_at": "2025-12-18T08:00:00Z",
    "updated_at": "2025-12-18T08:30:00Z"
  },
  "error": null
}
```

**狀態碼**: 200 OK

#### 3.2 部分更新 (只更新 nickname 和 bio)

```bash
curl -X PUT http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "NewNickname",
    "bio": "Updated bio"
  }'
```

**預期結果**: 200 OK，只有 nickname 和 bio 改變，其他欄位保持不變

#### 3.3 驗證更新是否持久化

```bash
# 再次查詢 profile，確認更新已保存
curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**預期結果**: 應該看到 Test 3.1 或 3.2 更新的值

---

### Test 4: Refresh Token 機制

#### 4.1 使用 Refresh Token 取得新的 Access Token

```bash
REFRESH_TOKEN="eyJhbGc..."

curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "'"$REFRESH_TOKEN"'"
  }'
```

**預期結果**:
```json
{
  "data": {
    "access_token": "eyJhbGc... (new token)",
    "token_type": "bearer",
    "expires_in": 900
  },
  "error": null
}
```

**狀態碼**: 200 OK

#### 4.2 使用新的 Access Token 存取 API

```bash
NEW_ACCESS_TOKEN="eyJhbGc..."

curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN"
```

**預期結果**: 200 OK，成功取得 profile

#### 4.3 測試過期的 Refresh Token

```bash
# 使用已過期或無效的 refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "invalid_or_expired_token"
  }'
```

**預期結果**: 401 Unauthorized

---

### Test 5: JWT Token 驗證

#### 5.1 使用無效 Token 存取受保護端點

```bash
curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer invalid_token"
```

**預期結果**: 401 Unauthorized

#### 5.2 使用過期 Token 存取

```bash
# 等待 Access Token 過期 (預設 15 分鐘)
# 或使用已知過期的 token
EXPIRED_TOKEN="eyJhbGc..."

curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $EXPIRED_TOKEN"
```

**預期結果**: 401 Unauthorized

#### 5.3 驗證 Token Payload

使用 [jwt.io](https://jwt.io/) 解碼 Access Token，驗證包含:

- `sub`: User ID (UUID)
- `email`: User email
- `exp`: 過期時間
- `iat`: 發行時間

---

### Test 6: 完整用戶流程 E2E

**目的**: 模擬完整的使用者旅程

```bash
# Step 1: Google 登入 (PKCE)
# (需要真實的 OAuth code)
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/google-callback \
  -H "Content-Type: application/json" \
  -d '{
    "code": "REAL_CODE_HERE",
    "code_verifier": "REAL_VERIFIER_HERE"
  }')

# 提取 tokens
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.data.access_token')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.data.refresh_token')
USER_ID=$(echo $RESPONSE | jq -r '.data.user_id')

echo "User ID: $USER_ID"
echo "Access Token: ${ACCESS_TOKEN:0:20}..."

# Step 2: 查詢初始 profile (應該是預設值)
echo "\n=== Initial Profile ==="
curl -s -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# Step 3: 更新 profile
echo "\n=== Updating Profile ==="
curl -s -X PUT http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "TestUser",
    "bio": "This is a test user"
  }' | jq

# Step 4: 驗證更新
echo "\n=== Verifying Update ==="
curl -s -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# Step 5: Refresh token
echo "\n=== Refreshing Token ==="
NEW_TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

NEW_ACCESS_TOKEN=$(echo $NEW_TOKEN_RESPONSE | jq -r '.data.access_token')
echo "New Access Token: ${NEW_ACCESS_TOKEN:0:20}..."

# Step 6: 使用新 token 存取
echo "\n=== Using New Token ==="
curl -s -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" | jq
```

---

## 驗收檢查清單

完成以上測試後，確認以下項目：

- [ ] **Test 1**: Google OAuth PKCE flow 正常運作
  - [ ] 1.1: 成功交換 tokens ✅
  - [ ] 1.2: 驗證錯誤正確處理 ✅
  - [ ] 1.3: PKCE 規範驗證正常 ✅

- [ ] **Test 2**: Profile 查詢功能正常
  - [ ] 2.1: 無認證存取被拒絕 ✅
  - [ ] 2.2: 有效 token 可以查詢 ✅

- [ ] **Test 3**: Profile 更新功能正常
  - [ ] 3.1: 完整更新成功 ✅
  - [ ] 3.2: 部分更新成功 ✅
  - [ ] 3.3: 更新持久化 ✅

- [ ] **Test 4**: Refresh Token 機制正常
  - [ ] 4.1: 可以換取新 access token ✅
  - [ ] 4.2: 新 token 可用 ✅
  - [ ] 4.3: 無效 token 被拒絕 ✅

- [ ] **Test 5**: JWT 驗證機制正常
  - [ ] 5.1: 無效 token 被拒絕 ✅
  - [ ] 5.2: 過期 token 被拒絕 ✅
  - [ ] 5.3: Token payload 正確 ✅

- [ ] **Test 6**: 完整流程 E2E 測試通過 ✅

---

## 測試數據記錄

### 測試環境資訊

- **Backend URL**: http://localhost:8000
- **測試日期**: ___________
- **測試人員**: ___________
- **環境版本**: ___________

### 測試結果

| 測試編號 | 測試項目 | 結果 | 備註 |
|---------|---------|------|------|
| Test 1.1 | PKCE code exchange | ⬜ | |
| Test 1.2 | 驗證錯誤 - 缺少 code | ⬜ | |
| Test 1.3 | 驗證錯誤 - code_verifier 太短 | ⬜ | |
| Test 2.1 | Profile 查詢 - 無認證 | ⬜ | |
| Test 2.2 | Profile 查詢 - 有認證 | ⬜ | |
| Test 3.1 | Profile 完整更新 | ⬜ | |
| Test 3.2 | Profile 部分更新 | ⬜ | |
| Test 3.3 | 更新持久化驗證 | ⬜ | |
| Test 4.1 | Refresh token 換取新 token | ⬜ | |
| Test 4.2 | 新 token 可用性 | ⬜ | |
| Test 4.3 | 無效 refresh token | ⬜ | |
| Test 5.1 | 無效 JWT token | ⬜ | |
| Test 5.2 | 過期 JWT token | ⬜ | |
| Test 5.3 | Token payload 驗證 | ⬜ | |
| Test 6 | 完整流程 E2E | ⬜ | |

**整體結果**: ⬜ 通過 / ⬜ 部分通過 / ⬜ 失敗

---

## 問題記錄

如發現任何問題，請記錄以下資訊：

### 問題 #1
- **測試項目**: ___________
- **現象**: ___________
- **預期行為**: ___________
- **實際行為**: ___________
- **錯誤訊息**: ___________
- **重現步驟**: ___________

---

## Postman Collection

可以將以上測試匯出為 Postman Collection 以便重複執行。

### 匯出步驟

1. 在 Postman 中建立新 Collection: "KCardSwap - Phase 3 (US1)"
2. 新增 Environment 變數:
   - `base_url`: http://localhost:8000
   - `access_token`: (從登入取得)
   - `refresh_token`: (從登入取得)
3. 新增所有測試端點
4. 匯出 Collection JSON

---

## 自動化測試腳本

可以使用以下腳本自動執行所有測試：

```bash
#!/bin/bash
# test-phase3.sh - Phase 3 (US1) 自動化測試腳本

BASE_URL="http://localhost:8000"
RESULTS_FILE="test-results-$(date +%Y%m%d-%H%M%S).txt"

echo "Phase 3 (US1) 手動驗證測試" > $RESULTS_FILE
echo "============================" >> $RESULTS_FILE
echo "測試時間: $(date)" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

# Test 1: Health Check
echo "[Test 0] Health Check"
curl -s $BASE_URL/health && echo "✅ Health check passed" || echo "❌ Health check failed"

# Test 2: Profile without auth
echo "[Test 2.1] Profile without auth"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/profile/me)
if [ "$STATUS" == "401" ] || [ "$STATUS" == "403" ]; then
    echo "✅ Correctly rejected (Status: $STATUS)"
else
    echo "❌ Unexpected status: $STATUS"
fi

# 更多測試...

echo "\n測試完成！結果已保存至: $RESULTS_FILE"
```

---

## 相關文件

- [Phase 3 測試實作報告](phase-3-test-implementation-complete.md)
- [Phase 3.1 PKCE 完成報告](phase-3.1-complete.md)
- [API 文件](apps/backend/docs/api/identity-module.md)
- [認證文件](apps/backend/docs/authentication.md)

---

**建立日期**: 2025-12-18  
**狀態**: 準備就緒 - 等待環境啟動  
**預估執行時間**: 30-45 分鐘
