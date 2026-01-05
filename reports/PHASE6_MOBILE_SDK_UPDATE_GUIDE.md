# Phase 6 Backend Changes - Mobile SDK Update Guide

## 概述

根據 commit d0e73e2 的需求釐清，後端評分系統已更新以支援 FR-SOCIAL-003A。本文檔說明需要執行的 OpenAPI 與 Mobile SDK 更新流程。

## 現況分析

### ✅ 已完成的後端變更
1. **Rating Entity**: `trade_id` 改為 `Optional[str]`
2. **Rating Model**: `trade_id` 設為 `nullable=True`
3. **RateUserUseCase**: 新增好友與封鎖驗證邏輯
4. **Rating Router**: 更新 endpoint 描述（本次 commit）

### 📋 OpenAPI Schema 狀態
- **openapi.json**: 已在 commit d0e73e2 更新，`trade_id` 已為 optional
- **需要重新生成**: 因為後端 router 的 description 已更新，需反映到 OpenAPI spec

### 📱 Mobile SDK 狀態
- **當前 SDK**: 已生成並包含 `trade_id?: string | null`（正確）
- **需要重新生成**: 以反映最新的 API 描述與業務規則文檔

### 🚧 Mobile UI 實作狀態
- **Phase 6 Mobile Tasks (M401-M404)**: 尚未實作
  - M401: 好友功能 UI
  - M402: 聊天室 UI
  - M403: 輪詢策略
  - M404: 推播通知
- **結論**: 目前沒有需要修改的 mobile UI 程式碼

## 必須執行的步驟

### Step 1: 重新生成 OpenAPI Specification

**為什麼需要**:
- 後端 rating router 的 endpoint description 已更新
- 確保 OpenAPI spec 完全反映最新的業務規則文檔

**執行方式（擇一）**:

#### 方式 A: 使用 Make（推薦）
```bash
cd /home/runner/work/KCardSwap/KCardSwap
make generate-openapi
```

#### 方式 B: 使用 Poetry
```bash
cd apps/backend
poetry run python scripts/generate_openapi.py
```

#### 方式 C: 使用 Docker
```bash
cd /home/runner/work/KCardSwap/KCardSwap
make generate-openapi-docker
# 或
docker compose exec backend python scripts/generate_openapi.py
```

**預期輸出**:
```
✅ OpenAPI specification generated successfully!
📄 Output: /path/to/KCardSwap/openapi/openapi.json
📊 Endpoints: X
🔖 Version: X.X.X

Next steps:
  1. Review the generated openapi.json
  2. Regenerate mobile SDK:
     cd apps/mobile
     npm run sdk:clean
     npm run sdk:generate
```

### Step 2: 重新生成 Mobile SDK

**為什麼需要**:
- 從更新後的 openapi.json 生成最新的 TypeScript types 與 API 函數
- 確保 mobile 開發者使用最新的 API schema

**執行方式**:
```bash
cd apps/mobile

# 清除舊的生成檔案
npm run sdk:clean

# 從 openapi.json 生成新的 SDK
npm run sdk:generate
```

**預期變更**:
```
apps/mobile/src/shared/api/generated/
├── types.gen.ts        # RatingRequest type (已經正確，但會更新文檔註解)
├── sdk.gen.ts          # submitRating function (會更新 JSDoc)
└── @tanstack/
    └── react-query.gen.ts  # TanStack Query hooks
```

### Step 3: 驗證變更

#### 3.1 檢查 OpenAPI JSON
```bash
cd /home/runner/work/KCardSwap/KCardSwap

# 驗證 trade_id 為 optional
cat openapi/openapi.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
schema = data['components']['schemas']['RatingRequest']
required = schema.get('required', [])
print('✓ trade_id is optional' if 'trade_id' not in required else '✗ trade_id is required')
print(f'Required fields: {required}')
"

# 驗證 endpoint description
cat openapi/openapi.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
desc = data['paths']['/api/v1/ratings']['post']['description']
print(f'Description: {desc}')
"
```

**預期輸出**:
```
✓ trade_id is optional
Required fields: ['rated_user_id', 'score']
Description: Submit a rating for another user (based on friendship or completed trade)
```

#### 3.2 檢查 Mobile SDK Types
```bash
cd apps/mobile

# 驗證 RatingRequest type
grep -A 10 "export type RatingRequest" src/shared/api/generated/types.gen.ts
```

**預期輸出**:
```typescript
export type RatingRequest = {
  rated_user_id: string;
  trade_id?: string | null;  // ✓ Optional
  score: number;
  comment?: string | null;
};
```

### Step 4: Commit 變更

```bash
cd /home/runner/work/KCardSwap/KCardSwap

# 檢查變更的檔案
git status

# 應該看到：
# modified:   openapi/openapi.json
# modified:   apps/backend/app/modules/social/presentation/routers/rating_router.py
# modified:   apps/mobile/src/shared/api/generated/types.gen.ts
# modified:   apps/mobile/src/shared/api/generated/sdk.gen.ts
# etc.

# Commit
git add openapi/openapi.json
git add apps/mobile/src/shared/api/generated/
git commit -m "chore: Regenerate OpenAPI spec and mobile SDK for Phase 6 rating changes

- Update rating endpoint description to reflect friendship-based ratings
- Regenerate mobile SDK to sync with backend API changes
- trade_id is now optional (can rate friends without trade context)"
```

## 技術細節

### OpenAPI Schema 變更重點

**RatingRequest Schema**:
```json
{
  "properties": {
    "rated_user_id": {"type": "string", "format": "uuid"},
    "trade_id": {
      "anyOf": [
        {"type": "string", "format": "uuid"},
        {"type": "null"}
      ],
      "description": "Associated trade ID (optional)"
    },
    "score": {"type": "integer", "minimum": 1, "maximum": 5},
    "comment": {
      "anyOf": [
        {"type": "string", "maxLength": 500},
        {"type": "null"}
      ]
    }
  },
  "required": ["rated_user_id", "score"]
}
```

**關鍵點**:
- `trade_id` 使用 `anyOf` 表示可為 UUID 或 null
- `required` 陣列不包含 `trade_id`
- `description` 明確標註 "(optional)"

### Mobile SDK 使用範例

**好友評分（無 trade_id）**:
```typescript
import { submitRatingApiV1RatingsPost } from '@/src/shared/api/generated';

// Rate a friend without trade context
const response = await submitRatingApiV1RatingsPost({
  body: {
    rated_user_id: friendUserId,
    score: 5,
    comment: "Great friend!",
    // trade_id: undefined  // ✓ Not required
  }
});
```

**交換評分（有 trade_id）**:
```typescript
// Rate based on a completed trade
const response = await submitRatingApiV1RatingsPost({
  body: {
    rated_user_id: tradingPartnerUserId,
    trade_id: completedTradeId,  // ✓ Optional but provided
    score: 5,
    comment: "Great trader!"
  }
});
```

## 常見問題

### Q1: 為什麼 openapi.json 已經有 optional trade_id 但還要重新生成？

**A**: commit d0e73e2 已經更新了 schema 結構，但最新的 commit 更新了 endpoint 的 description 文字（從 "after a trade" 改為 "based on friendship or completed trade"）。重新生成可確保：
1. API 文檔完全反映業務規則
2. Mobile SDK 的 JSDoc 註解是最新的
3. 未來開發者看到正確的 API 說明

### Q2: Mobile UI 需要修改嗎？

**A**: **不需要**。Phase 6 的 mobile tasks (M401-M404) 尚未實作，目前沒有任何 rating UI 程式碼。當未來實作 M401-M404 時，開發者會使用已更新的 SDK，自然就會正確處理 optional trade_id。

### Q3: 需要更新測試嗎？

**A**: 後端測試已經在之前的 commit 完成（T126G）。Mobile 端目前沒有 rating 相關的 UI 測試，因為 UI 尚未實作。

### Q4: 這次變更會破壞現有功能嗎？

**A**: **不會**。這是向後相容的變更：
- 舊的 API 呼叫（有 trade_id）依然有效
- 新的 API 呼叫（無 trade_id）現在也可以運作
- TypeScript type 已正確標記為 optional (`trade_id?: string | null`)

## 檢查清單

執行完成後，確認以下項目：

- [ ] `make generate-openapi` 成功執行
- [ ] `openapi/openapi.json` 已更新（git status 顯示 modified）
- [ ] Rating endpoint description 為 "based on friendship or completed trade"
- [ ] `npm run sdk:generate` 成功執行
- [ ] `apps/mobile/src/shared/api/generated/` 檔案已更新
- [ ] `RatingRequest` type 有 `trade_id?: string | null`
- [ ] Git commit 包含 openapi.json 和 generated/ 的變更
- [ ] CI/CD pipeline 通過（如果有設定）

## 相關文件

- 原始需求: commit d0e73e2 "doc: 更新交換提案與評分系統規範"
- 實作報告: `PHASE6_RATING_UPDATE_COMPLETION.md`
- Mobile SDK 指南: `apps/mobile/OPENAPI_SDK_GUIDE.md`
- Tasks 追蹤: `specs/001-kcardswap-complete-spec/tasks.md`

## 下一步

完成 OpenAPI 與 SDK 更新後：

1. **Phase 6 Backend**: ✅ 完成 (100%, 33/33 tasks)
2. **Phase 6 Mobile**: ⏳ 待實作 (M401-M404)
   - 實作時會使用更新後的 SDK
   - 自動獲得正確的 TypeScript types
   - API 呼叫自然支援 optional trade_id

---

**文件版本**: 1.0  
**最後更新**: 2025-12-22  
**作者**: GitHub Copilot
