# Phase 3.2: Idol Groups List API 實作總結

## 概述

實作了偶像團體列表 API，為 Onboarding 流程提供後端資料來源，避免前端硬編碼。

## API 端點

### GET /api/v1/idols/groups

獲取所有可用的偶像團體列表。

**特性**:
- 公開 API（無需驗證）
- 回傳 12 個偶像團體
- 資料與前端 mobile app 完全一致
- 按 sort_order 排序

**回應格式**:
```json
{
  "data": {
    "groups": [
      {
        "id": "newjeans",
        "name": "NewJeans",
        "emoji": "👖"
      },
      {
        "id": "ive",
        "name": "IVE",
        "emoji": "🦢"
      }
    ]
  },
  "meta": null,
  "error": null
}
```

## 實作檔案

### 後端 (Python/FastAPI)

1. **Schema 定義**: `apps/backend/app/modules/identity/presentation/schemas/idol_schemas.py`
2. **Router**: `apps/backend/app/modules/identity/presentation/routers/idols_router.py`
3. **靜態資料**: `apps/backend/app/modules/identity/infrastructure/data/idol_groups.py`
4. **主應用**: `apps/backend/app/main.py`

### 前端 (Mobile SDK)

生成的 SDK 檔案位於 `apps/mobile/src/shared/api/generated/`:
- `types.gen.ts`: TypeScript 類型定義
- `sdk.gen.ts`: API 客戶端函數
- `@tanstack/react-query.gen.ts`: React Query hooks

### 測試

1. **單元測試**: `tests/unit/identity/infrastructure/data/test_idol_groups.py`
2. **整合測試**: `tests/integration/modules/identity/test_idol_groups_flow.py`

## 前端使用方式

```typescript
import { getIdolGroupsApiV1IdolsGroupsGetOptions } from '@/src/shared/api/generated/@tanstack/react-query.gen';
import { useQuery } from '@tanstack/react-query';

function OnboardingScreen() {
  const { data, isLoading } = useQuery(
    getIdolGroupsApiV1IdolsGroupsGetOptions()
  );
  
  const groups = data?.data.groups || [];
  // 使用 groups 資料...
}
```

## 驗證結果

✅ API 端點正常運作  
✅ OpenAPI 規格已生成  
✅ Mobile SDK 已更新  
✅ 測試完整  
✅ 無安全問題（CodeQL 通過）  
✅ 資料與前端完全一致  
✅ **前端已串接新的 API** (commit: 5689fd3)

## 前端整合 (已完成)

已完成前端串接，OnboardingScreen 現在從 API 獲取偶像團體列表。

詳細說明請參考: `docs/frontend-integration-idol-groups.md`

### 變更檔案
- 新增: `apps/mobile/src/features/profile/hooks/useProfile.ts`
- 新增: `apps/mobile/src/features/profile/hooks/useIdolGroups.ts`
- 新增: `apps/mobile/src/features/profile/hooks/index.ts`
- 修改: `apps/mobile/src/features/profile/screens/OnboardingScreen.tsx`
