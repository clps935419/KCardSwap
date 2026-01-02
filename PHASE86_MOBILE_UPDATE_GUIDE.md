# Phase 8.6 - Mobile Update Guide

**Date**: 2026-01-02  
**Purpose**: 指導如何更新 Mobile 端以支援新的 envelope 回應格式  
**Status**: Ready for execution (需要 Node.js + Expo 環境)

## 概述

Phase 8.6 實作了統一的 API 回應格式。Mobile 端需要：
1. 重新生成 SDK (從新的 OpenAPI)
2. 更新所有 API hooks 提取 `response.data`
3. 更新錯誤處理解析 `response.error`
4. 更新分頁處理使用 `response.meta`

## 回應格式變更

### 舊格式 ❌
```typescript
// 直接回傳資料
{
  id: "uuid",
  nickname: "user",
  cards: [...]
}
```

### 新格式 ✅
```typescript
// Envelope 包裝
{
  data: {...} | [...],
  meta: {
    total?: number,
    page?: number,
    page_size?: number,
    total_pages?: number
  } | null,
  error: {
    code: string,
    message: string,
    details: Record<string, any>
  } | null
}
```

## Task T1410: 重新生成 Mobile SDK

### 前置條件

確保 OpenAPI snapshot 已更新：
```bash
# 檢查 OpenAPI 檔案
ls -la /path/to/KCardSwap/openapi/openapi.json

# 確認檔案日期為 2026-01-02 或之後
```

### 執行 SDK 生成

```bash
# 進入 mobile 目錄
cd apps/mobile

# 清除舊的生成檔案
npm run sdk:clean

# 重新生成 SDK
npm run sdk:generate

# 驗證生成成功
ls -la src/shared/api/generated/
```

### 驗證 SDK 生成

檢查生成的檔案：
```bash
apps/mobile/src/shared/api/generated/
├── index.ts
├── types.gen.ts
├── services.gen.ts
└── ...
```

檢查型別定義：
```typescript
// src/shared/api/generated/types.gen.ts

// 應該包含 envelope 型別
export interface ResponseEnvelope<T> {
  data: T | null;
  meta: PaginationMeta | null;
  error: ErrorDetail | null;
}

export interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details: Record<string, any>;
}
```

## Task T1411: 調整行動端 API 呼叫

### 更新模式

#### 模式 1: 單一資源 Hook

**舊 Hook** ❌:
```typescript
// apps/mobile/src/features/profile/hooks/useProfile.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/src/shared/api/client';

export function useProfile() {
  return useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await apiClient.get('/profile/me');
      return response.data; // ❌ 直接回傳
    },
  });
}

// 使用
const { data: profile } = useProfile();
// profile = { id, nickname, ... }
```

**新 Hook** ✅:
```typescript
// apps/mobile/src/features/profile/hooks/useProfile.ts
import { useQuery } from '@tanstack/react-query';
import { profileService } from '@/src/shared/api/generated';

export function useProfile() {
  return useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await profileService.getProfileMe();
      // ✅ SDK 已自動解析 envelope
      return response.data; // 從 envelope 提取
    },
  });
}

// 使用方式不變
const { data: profile } = useProfile();
// profile = { id, nickname, ... }
```

#### 模式 2: 分頁列表 Hook

**舊 Hook** ❌:
```typescript
// apps/mobile/src/features/cards/hooks/useMyCards.ts
export function useMyCards(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['cards', 'my', page, pageSize],
    queryFn: async () => {
      const response = await apiClient.get('/cards/me', {
        params: { page, page_size: pageSize }
      });
      return {
        cards: response.data.items,  // ❌
        total: response.data.total,  // ❌
      };
    },
  });
}

// 使用
const { data } = useMyCards(1, 20);
// data = { cards: [...], total: 100 }
```

**新 Hook** ✅:
```typescript
// apps/mobile/src/features/cards/hooks/useMyCards.ts
import { useQuery } from '@tanstack/react-query';
import { cardsService } from '@/src/shared/api/generated';

export function useMyCards(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['cards', 'my', page, pageSize],
    queryFn: async () => {
      const response = await cardsService.getCardsMe({
        query: { page, page_size: pageSize }
      });
      
      // ✅ 從 envelope 提取資料和 meta
      return {
        cards: response.data,      // data 是列表
        total: response.meta?.total ?? 0,
        page: response.meta?.page ?? 1,
        totalPages: response.meta?.total_pages ?? 0,
      };
    },
  });
}

// 使用
const { data } = useMyCards(1, 20);
// data = { cards: [...], total: 100, page: 1, totalPages: 5 }
```

#### 模式 3: Mutation Hook

**舊 Mutation** ❌:
```typescript
// apps/mobile/src/features/profile/hooks/useUpdateProfile.ts
export function useUpdateProfile() {
  return useMutation({
    mutationFn: async (data: UpdateProfileRequest) => {
      const response = await apiClient.put('/profile/me', data);
      return response.data;  // ❌
    },
  });
}
```

**新 Mutation** ✅:
```typescript
// apps/mobile/src/features/profile/hooks/useUpdateProfile.ts
import { useMutation } from '@tanstack/react-query';
import { profileService } from '@/src/shared/api/generated';

export function useUpdateProfile() {
  return useMutation({
    mutationFn: async (data: UpdateProfileRequest) => {
      const response = await profileService.updateProfileMe({
        body: data
      });
      return response.data;  // ✅ 從 envelope 提取
    },
  });
}
```

### 需要更新的 Hooks

#### Profile Feature
- [ ] `useProfile.ts` - GET profile
- [ ] `useUpdateProfile.ts` - PUT profile

#### Cards Feature
- [ ] `useMyCards.ts` - GET my cards (分頁)
- [ ] `useUploadCard.ts` - POST upload-url
- [ ] `useDeleteCard.ts` - DELETE card
- [ ] `useCardQuota.ts` - GET quota status
- [ ] `useConfirmUpload.ts` - POST confirm-upload

#### Friends Feature
- [ ] `useFriendRequest.ts` - POST request
- [ ] `useAcceptFriend.ts` - POST accept
- [ ] `useBlockUser.ts` - POST block
- [ ] `useUnblockUser.ts` - POST unblock
- [ ] `useFriends.ts` - GET friends list

#### Chat Feature
- [ ] `useChatRooms.ts` - GET chats
- [ ] `useChatMessages.ts` - GET messages (分頁)
- [ ] `useSendMessage.ts` - POST message

#### Trade Feature
- [ ] `useCreateTrade.ts` - POST trade
- [ ] `useAcceptTrade.ts` - POST accept
- [ ] `useCompleteTrade.ts` - POST complete
- [ ] `useTradeHistory.ts` - GET history (分頁)

#### Posts Feature
- [ ] `useBoardPosts.ts` - GET posts (分頁)
- [ ] `useCreatePost.ts` - POST post
- [ ] `usePostInterest.ts` - POST interest
- [ ] `usePostInterests.ts` - GET interests (分頁)

#### Nearby Feature
- [ ] `useNearbySearch.ts` - POST search
- [ ] `useUpdateLocation.ts` - PUT location

#### Rating Feature
- [ ] `useRateUser.ts` - POST rating
- [ ] `useUserRatings.ts` - GET ratings

#### Subscription Feature
- [ ] `useVerifyReceipt.ts` - POST verify-receipt
- [ ] `useSubscriptionStatus.ts` - GET status

## Task T1412: 更新行動端錯誤處理

### 錯誤映射更新

**舊錯誤處理** ❌:
```typescript
// apps/mobile/src/shared/api/errorMapper.ts

export function mapApiError(error: any): string {
  if (error.response) {
    const { status, data } = error.response;
    
    // ❌ 舊格式
    if (data.detail) {
      return data.detail;
    }
    
    switch (status) {
      case 401:
        return '請重新登入';
      case 404:
        return '找不到資源';
      default:
        return '發生錯誤';
    }
  }
  
  return '網路錯誤';
}
```

**新錯誤處理** ✅:
```typescript
// apps/mobile/src/shared/api/errorMapper.ts

interface ApiErrorResponse {
  data: null;
  meta: null;
  error: {
    code: string;
    message: string;
    details: Record<string, any>;
  };
}

export function mapApiError(error: any): {
  message: string;
  code?: string;
  details?: Record<string, any>;
} {
  if (error.response) {
    const { status, data } = error.response;
    
    // ✅ 檢查 envelope error
    if (data.error) {
      const apiError = data.error;
      return {
        message: getLocalizedMessage(apiError.code) || apiError.message,
        code: apiError.code,
        details: apiError.details,
      };
    }
  }
  
  // 網路錯誤
  return {
    message: '網路連線異常，請稍後再試',
  };
}

function getLocalizedMessage(code: string): string {
  const messages: Record<string, string> = {
    '401_UNAUTHORIZED': '請重新登入',
    '403_FORBIDDEN': '無權限執行此操作',
    '404_NOT_FOUND': '找不到資源',
    '422_LIMIT_EXCEEDED': '已超過使用限制',
    '429_RATE_LIMITED': '請求過於頻繁，請稍後再試',
    '409_CONFLICT': '資源衝突',
  };
  
  return messages[code] || '';
}
```

### UI 錯誤顯示更新

**舊錯誤顯示** ❌:
```typescript
// Feature component
const { data, error, isLoading } = useMyCards();

if (error) {
  return (
    <View>
      <Text>{error.message}</Text>  {/* ❌ 簡單訊息 */}
    </View>
  );
}
```

**新錯誤顯示** ✅:
```typescript
// Feature component
import { mapApiError } from '@/src/shared/api/errorMapper';

const { data, error, isLoading } = useMyCards();

if (error) {
  const errorInfo = mapApiError(error);
  
  return (
    <Box className="p-4">
      <Text className="text-red-600 font-bold">
        {errorInfo.message}
      </Text>
      
      {/* 顯示錯誤碼（開發用） */}
      {__DEV__ && errorInfo.code && (
        <Text className="text-sm text-gray-500 mt-2">
          Error Code: {errorInfo.code}
        </Text>
      )}
      
      {/* 顯示詳細資訊（如配額超限） */}
      {errorInfo.code === '422_LIMIT_EXCEEDED' && errorInfo.details && (
        <Text className="mt-2">
          已使用: {errorInfo.details.current}/{errorInfo.details.max}
        </Text>
      )}
      
      {/* 重試按鈕 */}
      <Button onPress={() => refetch()} className="mt-4">
        <ButtonText>重試</ButtonText>
      </Button>
    </Box>
  );
}
```

### 錯誤處理範例：配額超限

```typescript
// apps/mobile/src/features/cards/screens/UploadCardScreen.tsx

const uploadMutation = useUploadCard();

const handleUpload = async () => {
  try {
    await uploadMutation.mutateAsync(cardData);
    // 成功處理
  } catch (error) {
    const errorInfo = mapApiError(error);
    
    if (errorInfo.code === '422_LIMIT_EXCEEDED') {
      // 特殊處理配額超限
      const { limit_type, current, max } = errorInfo.details;
      
      Alert.alert(
        '上傳限制',
        `您已達到${getLimitTypeName(limit_type)}限制 (${current}/${max})`,
        [
          { text: '了解更多', onPress: () => navigation.navigate('Subscription') },
          { text: '確定', style: 'cancel' },
        ]
      );
    } else {
      // 一般錯誤
      Alert.alert('上傳失敗', errorInfo.message);
    }
  }
};
```

## Task T1413: 行動端驗證與測試

### 型別檢查

```bash
cd apps/mobile

# 執行 TypeScript 型別檢查
npm run type-check

# 預期結果: No errors
```

### 單元測試

```bash
# 執行測試
npm run test

# 執行特定測試
npm run test -- hooks/useProfile.test.ts
```

### 手動測試清單

#### 1. Profile Feature
- [ ] 登入後查看個人檔案
- [ ] 更新 nickname
- [ ] 更新 avatar
- [ ] 確認資料正確顯示

#### 2. Cards Feature
- [ ] 瀏覽我的卡冊列表
- [ ] 測試分頁功能（上下滑動載入更多）
- [ ] 上傳新卡片
- [ ] 刪除卡片
- [ ] 查看配額狀態
- [ ] 測試配額超限錯誤

#### 3. Friends Feature
- [ ] 送出好友邀請
- [ ] 接受好友邀請
- [ ] 查看好友列表
- [ ] 封鎖用戶
- [ ] 解除封鎖

#### 4. Chat Feature
- [ ] 查看聊天室列表
- [ ] 進入聊天室
- [ ] 發送訊息
- [ ] 接收訊息（輪詢）
- [ ] 分頁載入歷史訊息

#### 5. Trade Feature
- [ ] 建立交換提案
- [ ] 查看交換歷史（分頁）
- [ ] 接受交換
- [ ] 完成交換
- [ ] 查看交換詳情

#### 6. Posts Feature
- [ ] 瀏覽城市看板（分頁）
- [ ] 建立貼文
- [ ] 表達興趣
- [ ] 查看興趣列表（分頁）
- [ ] 接受/拒絕興趣

#### 7. Nearby Feature
- [ ] 附近搜尋
- [ ] 更新位置
- [ ] 測試搜尋次數限制

#### 8. Subscription Feature
- [ ] 查看訂閱狀態
- [ ] 購買訂閱（測試環境）
- [ ] 驗證收據
- [ ] 恢復購買

### 錯誤場景測試

- [ ] 網路斷線 - 顯示正確錯誤訊息
- [ ] Token 過期 - 自動 refresh 或導向登入
- [ ] 404 錯誤 - 顯示「找不到資源」
- [ ] 配額超限 - 顯示限制詳情與升級入口
- [ ] 429 頻率限制 - 顯示「請稍後再試」
- [ ] 伺服器錯誤 (500) - 顯示通用錯誤訊息

### 效能測試

- [ ] 列表滾動流暢度
- [ ] 分頁載入速度
- [ ] 圖片載入與快取
- [ ] Memory leaks 檢查

## 常見問題

### Q1: SDK 生成失敗
**A**: 確認 OpenAPI 檔案存在且格式正確
```bash
# 驗證 OpenAPI 檔案
cat openapi/openapi.json | jq .
```

### Q2: 型別錯誤
**A**: 清除 TypeScript 快取並重新檢查
```bash
npm run type-check --force
```

### Q3: 舊 API client 殘留
**A**: 全域搜尋並移除
```bash
# 搜尋 legacy client 使用
grep -r "from '@/src/shared/api/client'" apps/mobile/src/features/
```

### Q4: 分頁沒有 meta 資訊
**A**: 確認後端已正確實作分頁回應，檢查 OpenAPI snapshot

## 檔案清單

### 需要更新的檔案 (~40-50 files)

```
apps/mobile/src/
├── features/
│   ├── profile/
│   │   └── hooks/
│   │       ├── useProfile.ts
│   │       └── useUpdateProfile.ts
│   ├── cards/
│   │   ├── hooks/
│   │   │   ├── useMyCards.ts
│   │   │   ├── useUploadCard.ts
│   │   │   ├── useDeleteCard.ts
│   │   │   ├── useCardQuota.ts
│   │   │   └── useConfirmUpload.ts
│   │   └── screens/
│   │       ├── MyCardsScreen.tsx
│   │       └── UploadCardScreen.tsx
│   ├── friends/
│   │   ├── hooks/ (5 files)
│   │   └── screens/ (3 files)
│   ├── chat/
│   │   ├── hooks/ (3 files)
│   │   └── screens/ (2 files)
│   ├── trade/
│   │   ├── hooks/ (4 files)
│   │   └── screens/ (3 files)
│   ├── posts/
│   │   ├── hooks/ (4 files)
│   │   └── screens/ (4 files)
│   ├── nearby/
│   │   ├── hooks/ (2 files)
│   │   └── screens/ (1 file)
│   ├── rating/
│   │   └── hooks/ (2 files)
│   └── subscription/
│       ├── hooks/ (2 files)
│       └── screens/ (2 files)
└── shared/
    └── api/
        └── errorMapper.ts
```

## 執行時間預估

- **T1410**: SDK 生成 - 30 分鐘
- **T1411**: API hooks 更新 - 8-10 小時
- **T1412**: 錯誤處理更新 - 8-10 小時
- **T1413**: 測試與驗證 - 3-5 小時

**總計**: 19-25 小時 (約 3-4 個工作天)

## 完成標準

Mobile 更新完成的標準：

1. ✅ Mobile SDK 重新生成成功
2. ✅ 所有 API hooks 已更新使用新 SDK
3. ✅ 錯誤映射已更新處理 envelope error
4. ✅ 所有畫面正確提取 `response.data`
5. ✅ 分頁功能正確使用 `response.meta`
6. ✅ `npm run type-check` 無錯誤
7. ✅ `npm run test` 測試通過
8. ✅ 手動測試清單全數完成
9. ✅ 錯誤場景測試通過
10. ✅ 無效能問題

## 相關文件

- [Response Format Specification](../../specs/001-kcardswap-complete-spec/response-format.md)
- [API Documentation](../../apps/backend/docs/api/README.md)
- [Mobile TECH_STACK.md](apps/mobile/TECH_STACK.md)
- [Mobile README.md](apps/mobile/README.md)
- [OpenAPI SDK Guide](apps/mobile/OPENAPI_SDK_GUIDE.md)

---

**狀態**: Ready for execution  
**預估時間**: 19-25 hours (3-4 working days)  
**需求**: Node.js + Expo Development Build  
**優先順序**: High (blocking deployment)  
**前置條件**: T1408 (Integration tests) 完成
