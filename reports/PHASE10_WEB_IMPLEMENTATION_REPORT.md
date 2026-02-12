# Phase 10 實作報告：查看他人個人詳細頁（Instagram 風格 - Web 端）

**實作日期**: 2026-02-12  
**優先級**: P2  
**狀態**: ✅ 完成

## 概述

本階段實作了 Instagram 風格的使用者個人檔案頁面（Web 端），允許使用者查看其他用戶的個人資訊和相簿小卡集合。此功能增強了社交互動性，讓使用者可以更好地了解交易對象。

## 實作內容

### Backend 實作（已完成）

#### 1. 新增 API Endpoint (T206)

**檔案**: `apps/backend/app/modules/identity/presentation/routers/profile_router.py`

新增 `GET /api/v1/profile/{user_id}` endpoint：
- 允許已認證使用者查看其他使用者的公開個人檔案
- 重用現有的 `GetProfileUseCase` 以保持程式碼簡潔
- 返回標準化的 `ProfileResponseWrapper` 格式
- 包含完整的錯誤處理（404, 401）

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
2. **test_get_user_profile_not_found**: 測試不存在的使用者（404）
3. **test_get_user_profile_unauthorized**: 測試未認證訪問（401）

### Web Frontend 實作

#### 1. SDK 重新生成 (W101)

**執行**:
```bash
cd apps/web
npm run sdk:generate
```

**結果**：
- 生成 `getUserProfileApiV1ProfileUserIdGetOptions` query function
- 生成 `getUserProfileApiV1ProfileUserIdGetQueryKey`
- 完整的 TypeScript 類型定義
- 更新至 `src/shared/api/generated/`

#### 2. useUserProfile Hook (W102)

**檔案**: `apps/web/src/shared/api/hooks/profile.ts`

新增自訂 hook 封裝 API 呼叫：

```typescript
export function useUserProfile(userId: string) {
  return useQuery({
    ...getUserProfileApiV1ProfileUserIdGetOptions({
      path: { user_id: userId },
    }),
    staleTime: 1000 * 60 * 5, // 5 分鐘 cache
  })
}
```

**特點**：
- 使用 TanStack Query 管理資料狀態
- 自動處理 loading、error、success 狀態
- 5 分鐘 staleTime 減少不必要的請求

#### 3. ProfileHeader 元件 (W103)

**檔案**: `apps/web/src/features/profile/components/ProfileHeader.tsx`

Instagram 風格的個人資訊卡片元件：

**功能**：
- 顯示使用者頭像（使用 UserAvatar 元件）
- 顯示暱稱（Heading size="2xl"）
- 顯示個人簡介（bio）
- 顯示地區（帶 📍 圖標）
- 統計資訊區域（小卡數、交易數、朋友數）- 預留未來擴展

**設計原則**：
- 使用 shadcn/ui Card 元件
- Tailwind CSS 樣式
- 響應式設計，適配不同螢幕尺寸
- 中心對齊的佈局

```typescript
interface ProfileHeaderProps {
  profile: ProfileResponse
}

export function ProfileHeader({ profile }: ProfileHeaderProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex flex-col items-center space-y-4">
          <UserAvatar
            src={profile.avatar_url || undefined}
            alt={profile.nickname || 'User'}
            className="h-24 w-24"
          />
          {/* ... nickname, bio, region, stats */}
        </div>
      </CardContent>
    </Card>
  )
}
```

#### 4. UserProfilePageClient 更新 (W104)

**檔案**: `apps/web/src/features/gallery/components/UserProfilePageClient.tsx`

完整的使用者個人檔案頁面：

**結構**：
1. **Profile Header 區域**：ProfileHeader 元件
2. **Gallery Cards 區域**：GalleryGrid 元件

**資料獲取**：
```typescript
// 使用兩個 hooks 並行獲取資料
const { data: profileData, isLoading: isLoadingProfile, error: profileError } = 
  useUserProfile(userId)
const { data: galleryData, isLoading: isLoadingGallery, error: galleryError } = 
  useUserGalleryCards(userId)
```

**狀態處理**：
- Loading 狀態：顯示 Skeleton 載入動畫
- Error 狀態：顯示友善的錯誤訊息
- Success 狀態：渲染完整的 profile 和 gallery

#### 5. SSR 預取優化 (W105)

**檔案**: `apps/web/src/app/(app)/users/[userId]/page.tsx`

Server Component 實作 SSR 預取：

```typescript
export default async function UserProfilePage({ params }: UserProfilePageProps) {
  const resolvedParams = await params
  const userId = resolvedParams.userId
  const queryClient = createServerQueryClient()

  // Prefetch profile data
  await queryClient.prefetchQuery({
    ...getUserProfileApiV1ProfileUserIdGetOptions({
      path: { user_id: userId },
    }),
  })

  // Prefetch gallery cards
  await queryClient.prefetchQuery({
    ...getUserGalleryCardsApiV1UsersUserIdGalleryCardsGetOptions({
      path: { user_id: userId },
    }),
  })

  const dehydratedState = dehydrate(queryClient)

  return (
    <HydrationBoundary state={dehydratedState}>
      <UserProfilePageClient userId={userId} />
    </HydrationBoundary>
  )
}
```

**優點**：
- 伺服器端預取資料，首屏渲染速度快
- SEO 友善（內容已在 HTML 中）
- 使用 HydrationBoundary 實現平滑的 hydration
- Client Component 可直接使用預取的資料

## 技術亮點

### 1. 程式碼重用

- Backend 重用 `GetProfileUseCase`，無需建立新的 use case
- Web 建立可重用的 ProfileHeader 元件
- 元件可在未來其他地方使用（例如：搜尋結果、推薦使用者）

### 2. 類型安全

- 所有新增程式碼通過 TypeScript strict mode 檢查
- 使用生成的 SDK types（ProfileResponse, GalleryCardResponse）
- Biome 代碼檢查通過

### 3. 效能優化

- SSR 預取資料，首屏載入快
- TanStack Query 自動快取，避免重複請求
- 並行資料獲取（profile 和 gallery 同時載入）
- 5 分鐘 staleTime 減少不必要的 API 呼叫

### 4. 使用者體驗

- Loading 狀態使用 Skeleton 動畫
- 錯誤訊息友善易懂
- 響應式設計（sm/md/lg breakpoints）
- Instagram 風格的設計語言一致

### 5. 遵循 Web 開發規範

- ✅ 使用 shadcn/ui 元件系統
- ✅ 使用 `@/` 路徑別名（禁止相對路徑）
- ✅ 使用生成的 TanStack Query hooks
- ✅ SSR + CSR Hydration 最佳實踐
- ✅ Biome linting 和 formatting

## 檔案變更清單

### Backend (保持不變)
1. `apps/backend/app/modules/identity/presentation/routers/profile_router.py` - 新增 endpoint
2. `openapi/openapi.json` - 更新 API 規格
3. `apps/backend/tests/integration/modules/identity/test_profile_router_e2e.py` - 新增測試

### Web (新增/修改)
1. `apps/web/src/shared/api/hooks/profile.ts` - 新增 useUserProfile hook
2. `apps/web/src/features/profile/components/ProfileHeader.tsx` - 新建元件
3. `apps/web/src/features/profile/components/index.ts` - 新建 export
4. `apps/web/src/features/gallery/components/UserProfilePageClient.tsx` - 更新
5. `apps/web/src/app/(app)/users/[userId]/page.tsx` - 更新 SSR 預取
6. `apps/web/src/shared/api/generated/*` - SDK 重新生成

### Mobile (已移除)
- 移除所有 Mobile 相關變更（M106-M110）
- 恢復原始狀態

### Documentation
1. `specs/001-kcardswap-complete-spec/tasks.md` - 更新為 Web 任務

## 未來改進建議

### 短期（下個 Sprint）
1. **統計數字實作**：
   - 實際計算小卡數量（從 galleryData.total 獲取）
   - 新增交易數量 API
   - 新增朋友數量 API

2. **社交互動按鈕**：
   - 新增「發送訊息」按鈕
   - 新增「封鎖使用者」按鈕
   - 新增「關注/取消關注」按鈕

3. **圖片優化**：
   - 實作圖片 lazy loading
   - 使用 Next.js Image 元件優化載入
   - 支援 WebP 格式

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

### Web
- ✅ Next.js App Router 架構
- ✅ shadcn/ui 元件系統
- ✅ Tailwind CSS 樣式
- ✅ `@/` 路徑別名（禁止相對路徑）
- ✅ TanStack Query 資料管理
- ✅ TypeScript strict mode
- ✅ SSR + CSR Hydration 最佳實踐
- ✅ Biome linting 和 formatting

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

### Web 驗證
```bash
cd apps/web

# Biome 檢查（lint + format）
npm run check

# TypeScript 類型檢查
npx tsc --noEmit

# 開發模式
npm run dev
```

### 手動測試
1. 啟動後端：`docker compose up -d`
2. 啟動 Web：`cd apps/web && npm run dev`
3. 瀏覽器開啟：`http://localhost:3000/users/{userId}`
4. 驗證：
   - ✅ 個人資訊正確顯示
   - ✅ 小卡網格正確渲染
   - ✅ Loading 狀態正常
   - ✅ 錯誤處理正確
   - ✅ SSR 預取生效（檢視原始 HTML）

## 結論

Phase 10 成功實作了 Instagram 風格的使用者個人檔案頁面（Web 端），為 KCardSwap 增添了重要的社交功能。實作過程中遵循了專案的所有開發規範，建立了可重用的元件，並確保了程式碼品質和類型安全。

**關鍵成果**：
- ✅ 8 個任務全部完成（3 Backend + 5 Web）
- ✅ 新增 1 個 API endpoint
- ✅ 新增 1 個 React hook
- ✅ 新增 1 個 React 元件
- ✅ 更新 2 個現有頁面
- ✅ 新增 3 個整合測試
- ✅ 0 個 TypeScript 錯誤
- ✅ Biome 代碼檢查通過
- ✅ 完整的文件更新

此功能為後續的社交互動功能（如關注、留言、推薦）奠定了堅實的基礎。

## 與 Mobile 端的差異

原本實作了 Mobile 端，但根據使用者要求已改為 Web 端實作：

**已移除的 Mobile 檔案**：
- `apps/mobile/src/features/profile/components/ProfileHeader.tsx`
- `apps/mobile/src/features/profile/components/CardGrid.tsx`
- `apps/mobile/src/features/profile/components/index.ts`
- `apps/mobile/src/features/profile/screens/UserProfileScreen.tsx`

**恢復的 Mobile 檔案**：
- `apps/mobile/src/features/friends/screens/FriendProfileScreen.tsx`（恢復原始狀態）
- `apps/mobile/src/features/profile/screens/index.ts`（恢復原始狀態）

**Web vs Mobile 差異**：
- Web 使用 shadcn/ui，Mobile 使用 Gluestack UI
- Web 有 SSR 預取優化，Mobile 是純 CSR
- Web 使用 Next.js App Router，Mobile 使用 Expo Router
- Web 支援響應式設計（sm/md/lg），Mobile 固定為手機螢幕
