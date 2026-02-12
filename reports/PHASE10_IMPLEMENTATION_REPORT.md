# Phase 10 實作報告：查看他人個人詳細頁（Instagram 風格）

**實作日期**: 2026-02-12  
**優先級**: P2  
**狀態**: ✅ 完成

## 概述

本階段實作了 Instagram 風格的使用者個人檔案頁面，允許使用者查看其他用戶的個人資訊和相簿小卡集合。此功能增強了社交互動性，讓使用者可以更好地了解交易對象。

## 實作內容

### Backend 實作

#### 1. 新增 API Endpoint (T206)

**檔案**: `apps/backend/app/modules/identity/presentation/routers/profile_router.py`

新增 `GET /api/v1/profile/{user_id}` endpoint：
- 允許已認證使用者查看其他使用者的公開個人檔案
- 重用現有的 `GetProfileUseCase` 以保持程式碼簡潔
- 返回標準化的 `ProfileResponseWrapper` 格式
- 包含完整的錯誤處理（404, 401）

```python
@router.get(
    "/{user_id}",
    response_model=ProfileResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Retrieve another user's profile information",
)
async def get_user_profile(
    user_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user)],
    use_case: Annotated[GetProfileUseCase, Depends(get_get_profile_use_case)],
) -> ProfileResponseWrapper:
    ...
```

#### 2. OpenAPI 規格更新 (T207)

**檔案**: `openapi/openapi.json`

執行 `generate_openapi.py` 腳本更新 API 文檔：
- 新增 `get_user_profile_api_v1_profile__user_id__get` operation
- 包含完整的請求/回應 schema
- 自動驗證參數類型（UUID）
- 標準化錯誤回應格式

總 endpoints 數量：55 個

#### 3. 整合測試 (T208)

**檔案**: `apps/backend/tests/integration/modules/identity/test_profile_router_e2e.py`

新增 3 個測試案例：

1. **test_get_user_profile_success**: 測試成功獲取使用者資料
   - 驗證返回的資料完整性
   - 確認 user_id 匹配

2. **test_get_user_profile_not_found**: 測試不存在的使用者
   - 返回 404 狀態碼
   - 包含適當的錯誤訊息

3. **test_get_user_profile_unauthorized**: 測試未認證訪問
   - 返回 401 狀態碼
   - 確保安全性

### Mobile Frontend 實作

#### 1. SDK 重新生成 (M106)

執行步驟：
```bash
cd apps/mobile
npm run sdk:clean
npm run sdk:generate
```

結果：
- 生成 `getUserProfileApiV1ProfileUserIdGetOptions` query function
- 生成 `getUserProfileApiV1ProfileUserIdGetQueryKey` 
- 完整的 TypeScript 類型定義

#### 2. ProfileHeader 元件 (M107)

**檔案**: `apps/mobile/src/features/profile/components/ProfileHeader.tsx`

Instagram 風格的個人資訊卡片元件：

**功能**：
- 顯示使用者頭像（圓形，24x24）
- 顯示暱稱（Heading size="xl"）
- 顯示個人簡介（bio）
- 顯示地區（帶 📍 圖標）
- 統計資訊區域（小卡數、交易數、朋友數）- 預留未來擴展

**設計原則**：
- 使用 Gluestack UI 元件（Box, Text, Heading）
- Tailwind CSS className 樣式
- 響應式設計，適配不同螢幕尺寸

```typescript
interface ProfileHeaderProps {
  profile: ProfileResponse;
  isOwnProfile?: boolean;
}
```

#### 3. CardGrid 元件 (M108)

**檔案**: `apps/mobile/src/features/profile/components/CardGrid.tsx`

Instagram 風格的相簿網格：

**功能**：
- 3 列網格佈局
- 自動計算卡片尺寸（基於螢幕寬度）
- 支援點擊事件處理
- Loading 狀態顯示
- 空狀態處理（顯示 📦 圖標和提示）
- 底部顯示總數統計

**技術細節**：
- 使用 FlatList 實現虛擬化渲染（效能優化）
- numColumns={3} 固定 3 列
- 間距：2px（minimalist 設計）
- 卡片為正方形（寬高相同）

```typescript
interface CardGridProps {
  cards: GalleryCardResponse[];
  onCardPress?: (card: GalleryCardResponse) => void;
  isLoading?: boolean;
}
```

#### 4. UserProfileScreen 畫面 (M109)

**檔案**: `apps/mobile/src/features/profile/screens/UserProfileScreen.tsx`

完整的使用者個人檔案畫面：

**結構**：
1. **頭部區域**：ProfileHeader 元件
2. **操作按鈕區域**：
   - 💬 發送訊息（導向聊天）
   - 🚫 封鎖使用者（確認對話框）
3. **相簿標題**：📸 相簿
4. **網格區域**：CardGrid 元件

**資料獲取**：
```typescript
// 使用 TanStack Query 並行獲取兩個資源
const { data: profileData, isLoading: isLoadingProfile } = useQuery({
  ...getUserProfileApiV1ProfileUserIdGetOptions({
    path: { user_id: userId },
  }),
  enabled: !!userId,
});

const { data: cardsData, isLoading: isLoadingCards } = useQuery({
  ...getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions({
    path: { user_id: userId },
  }),
  enabled: !!userId,
});
```

**錯誤處理**：
- 無效的使用者 ID
- Profile 載入失敗
- 未找到使用者

**互動功能**：
- 點擊小卡顯示詳情（Alert - 待未來實作）
- 發送訊息（Alert - 待 M402 實作）
- 封鎖使用者（整合現有 useBlockUser hook）

#### 5. 更新 FriendProfileScreen (M110)

**檔案**: `apps/mobile/src/features/friends/screens/FriendProfileScreen.tsx`

簡化為重導至新的 UserProfileScreen：

```typescript
import UserProfileScreen from '@/src/features/profile/screens/UserProfileScreen';
export default UserProfileScreen;
```

這種設計保持了路由一致性，同時避免程式碼重複。

## 技術亮點

### 1. 程式碼重用

- Backend 重用 `GetProfileUseCase`，無需建立新的 use case
- Mobile 建立可重用的 ProfileHeader 和 CardGrid 元件
- 兩個元件可在未來其他地方使用（例如：搜尋結果、推薦使用者）

### 2. 類型安全

- 所有新增程式碼通過 TypeScript strict mode 檢查
- 使用生成的 SDK types（ProfileResponse, GalleryCardResponse）
- 無隱式 any 類型

### 3. 效能優化

- FlatList 虛擬化渲染，處理大量小卡不卡頓
- TanStack Query 自動快取，避免重複請求
- 並行資料獲取（profile 和 cards 同時載入）

### 4. 使用者體驗

- Loading 狀態明確顯示
- 錯誤訊息友善易懂
- 空狀態設計吸引人
- IG 風格的設計語言一致

### 5. 測試覆蓋

- 3 個整合測試涵蓋主要場景
- 測試未認證、成功、失敗路徑
- 遵循 AAA 模式（Arrange-Act-Assert）

## 檔案變更清單

### Backend (3 files)
1. `apps/backend/app/modules/identity/presentation/routers/profile_router.py` - 新增 endpoint
2. `openapi/openapi.json` - 更新 API 規格
3. `apps/backend/tests/integration/modules/identity/test_profile_router_e2e.py` - 新增測試

### Mobile (7 files created/modified)
1. `apps/mobile/src/features/profile/components/ProfileHeader.tsx` - 新建
2. `apps/mobile/src/features/profile/components/CardGrid.tsx` - 新建
3. `apps/mobile/src/features/profile/components/index.ts` - 新建
4. `apps/mobile/src/features/profile/screens/UserProfileScreen.tsx` - 新建
5. `apps/mobile/src/features/profile/screens/index.ts` - 更新
6. `apps/mobile/src/features/friends/screens/FriendProfileScreen.tsx` - 更新
7. `apps/mobile/src/shared/api/generated/*` - SDK 重新生成

### Documentation (1 file)
1. `specs/001-kcardswap-complete-spec/tasks.md` - 新增 Phase 10 章節

## 未來改進建議

### 短期（下個 Sprint）
1. **統計數字實作**：
   - 實際計算小卡數量（從 cardsData.total 獲取）
   - 新增交易數量 API
   - 新增朋友數量 API

2. **圖片顯示優化**：
   - 整合 media asset 服務顯示真實圖片
   - 實作縮圖快取（參考 CardItem.tsx 的實作）
   - 支援圖片預覽放大

3. **小卡詳情頁**：
   - 實作點擊小卡後的詳情展示
   - 顯示小卡完整資訊（標題、偶像、專輯、稀有度）
   - 支援放大查看高清圖

### 中期（2-3 個 Sprints）
1. **社交功能增強**：
   - 實作關注/取消關注功能
   - 顯示互相關注狀態
   - 支援查看粉絲和追蹤列表

2. **隱私設定**：
   - 尊重使用者的 privacy_flags
   - 支援設定個人檔案可見性
   - 實作黑名單功能

3. **進階篩選**：
   - 小卡相簿支援篩選（偶像、團體、專輯）
   - 排序選項（時間、稀有度）
   - 搜尋功能

### 長期（未來版本）
1. **個人化推薦**：
   - 根據小卡收藏推薦相似使用者
   - 推薦可能感興趣的交易對象
   - AI 驅動的配對建議

2. **社群功能**：
   - 支援留言/評論
   - 點讚收藏功能
   - 分享到社群媒體

3. **進階分析**：
   - 個人收藏統計圖表
   - 交易歷史分析
   - 活躍度趨勢

## 遵循的開發規範

### Backend
- ✅ Clean Architecture (Domain-Driven Design)
- ✅ 依賴注入（Dependency Injection）
- ✅ 標準化回應格式（ProfileResponseWrapper）
- ✅ RESTful API 設計原則
- ✅ 完整的錯誤處理

### Mobile
- ✅ Gluestack UI 元件系統
- ✅ Tailwind CSS className 樣式
- ✅ `@/` 路徑別名（禁止相對路徑）
- ✅ TanStack Query 資料管理
- ✅ TypeScript strict mode
- ✅ 參考現有 feature 的程式碼風格

### 測試
- ✅ 整合測試涵蓋主要場景
- ✅ Test fixtures 重用
- ✅ 遵循 AAA 模式

## 驗證步驟

### Backend 驗證（需要 Docker 環境）
```bash
# 在專案根目錄執行
make test-integration-docker

# 或針對特定測試
docker compose exec backend python -m pytest \
  tests/integration/modules/identity/test_profile_router_e2e.py::TestProfileRouterE2E::test_get_user_profile_success -v
```

### Mobile 驗證
```bash
cd apps/mobile

# TypeScript 類型檢查
npm run type-check

# ESLint 檢查
npm run lint

# 格式檢查
npm run format:check
```

### 手動測試（需要模擬器/實機）
1. 啟動 Expo 開發伺服器：`npm start`
2. 導航至 Friends 標籤
3. 點擊任一使用者
4. 驗證：
   - ✅ 個人資訊正確顯示
   - ✅ 小卡網格正確渲染
   - ✅ 操作按鈕可點擊
   - ✅ Loading 狀態正常
   - ✅ 錯誤處理正確

## 結論

Phase 10 成功實作了 Instagram 風格的使用者個人檔案頁面，為 KCardSwap 增添了重要的社交功能。實作過程中遵循了專案的所有開發規範，建立了可重用的元件，並確保了程式碼品質和類型安全。

**關鍵成果**：
- ✅ 8 個任務全部完成（3 Backend + 5 Mobile）
- ✅ 新增 1 個 API endpoint
- ✅ 新增 4 個 React 元件
- ✅ 新增 3 個整合測試
- ✅ 0 個 TypeScript 錯誤
- ✅ 完整的文件更新

此功能為後續的社交互動功能（如關注、留言、推薦）奠定了堅實的基礎。
