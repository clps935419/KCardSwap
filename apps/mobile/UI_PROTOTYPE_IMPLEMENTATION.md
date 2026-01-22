# UI Prototype Implementation Guide

本文件說明根據 `ui_prototype.html` 實作的 UI 更新。

## 實作內容

### 1. Tab 導航結構（5-Tab Design）

**更新前：**
- 4 個 Tab: Home | My Cards | Nearby | Profile

**更新後：**
- 5 個 Tab: 城市看板 | 附近 | 上傳 | 聊天 | 個人
- 對應原型: Home | Nearby | Upload | Chat | Profile

**檔案位置：**
- `app/(tabs)/_layout.tsx` - Tab 結構定義
- `app/(tabs)/index.tsx` - Home Tab (城市看板)
- `app/(tabs)/nearby.tsx` - Nearby Tab
- `app/(tabs)/upload.tsx` - Upload Tab (新增)
- `app/(tabs)/chat.tsx` - Chat Tab (新增)
- `app/(tabs)/profile.tsx` - Profile Tab

### 2. Onboarding 流程

**功能：** 新用戶首次登入後選擇偏好的偶像團體

**實作內容：**
- 12 個預設 K-pop 團體選項（NewJeans, IVE, aespa, LE SSERAFIM 等）
- 多選設計，可選擇多個團體
- 儲存到 `Profile.preferences.favorite_idol_groups`
- 標記 `onboarding_completed: true`

**檔案位置：**
- `app/onboarding.tsx` - Onboarding 路由
- `src/features/profile/screens/OnboardingScreen.tsx` - 主畫面
- `src/features/profile/constants/idolGroups.ts` - 團體列表定義

**使用方式：**
```typescript
router.push('/onboarding'); // 導航到 Onboarding
```

### 3. 主色調更新（Indigo Theme）

**原型配色：**
- Primary: Indigo-600 (#4F46E5)
- Secondary: Pink-500 (#EC4899)
- Background: Slate-50 (#F8FAFC)

**實作位置：**
- `src/shared/ui/theme/colors.ts` - 主題顏色定義
- Tab Bar 活躍顏色: Indigo-600
- Tab Bar 非活躍顏色: Slate-400

**使用範例：**
```tsx
import { COLORS } from '@/src/shared/ui/theme/colors';

<Box style={{ backgroundColor: COLORS.primary }}>
  <Text style={{ color: COLORS.textOnPrimary }}>按鈕</Text>
</Box>
```

### 4. 城市看板（BoardPostsScreen）

**更新內容：**
- 使用 Indigo 主色調
- 圓角卡片設計 (rounded-3xl)
- 相對時間顯示（10m, 1h, 2d 格式）
- 圖片預留位置（灰色方塊）
- 簡化的城市選擇器（pill 樣式）
- 移除篩選器輸入框，改為點擊標籤篩選

**原型對應：**
```javascript
// 原型中的 mock 資料
feeds: [
  { user: 'HanniFan_TW', time: '10m', title: '【求換】Hanni 藍版 換 Minji', tag: 'NewJeans' },
  ...
]
```

### 5. Upload Tab

**設計風格：** Bottom Sheet Modal

**特點：**
- 半透明黑色遮罩背景
- 圓角頂部（rounded-t-[2rem]）
- Handle bar（拖曳指示器）
- 兩種上傳選項：
  1. 📷 上傳小卡照片 → `/cards/upload`
  2. 📝 發布交換貼文 → `/posts/create`

**原型對應：**
```javascript
// 原型中的 upload modal
<div class="bg-white rounded-t-[2rem] p-6 h-[85%] animate-slide-up">
  <div class="w-12 h-1.5 bg-slate-200 rounded-full mx-auto mb-8"></div>
  ...
</div>
```

## 資料流程

### Onboarding 偏好儲存

```typescript
// 1. 用戶選擇偶像團體
const selectedGroups = ['newjeans', 'ive', 'aespa'];

// 2. 儲存到 Profile.preferences
await updateProfile.mutateAsync({
  preferences: {
    favorite_idol_groups: selectedGroups,
    onboarding_completed: true,
  },
});

// 3. 導航到主應用
router.replace('/(tabs)');
```

### 讀取用戶偏好

```typescript
const { data: profileData } = useQuery(getMyProfileOptions());
const profile = profileData?.data;

// 取得偏好的團體
const favoriteGroups = profile?.preferences?.favorite_idol_groups || [];
const hasCompletedOnboarding = profile?.preferences?.onboarding_completed || false;
```

## API 對應檢查

✅ **所有 API 都已對應：**

| 原型 API | 實際 API | 狀態 |
|---------|---------|------|
| `POST /api/v1/trades` | Trade feature | ✅ 已實作 |
| Posts API | `GET /api/v1/posts/board/{city_code}` | ✅ 已實作 |
| Nearby API | `GET /api/v1/nearby` | ✅ 已實作 |
| Chat API | `GET /api/v1/chat/rooms` | ✅ 已實作 |
| Profile API | `GET/PUT /api/v1/profiles/me` | ✅ 已實作 |

## 導航路徑

```
/(tabs)/
  ├── index           → 城市看板 (BoardPostsScreen)
  ├── nearby          → 附近搜尋 (NearbySearchScreen)
  ├── upload          → 上傳選項 (UploadScreen)
  ├── chat            → 聊天列表 (ChatRoomsScreen)
  ├── profile         → 個人檔案 (ProfileScreen)
  └── cards/          → 小卡管理（隱藏，不在 tab bar）
      ├── index       → 我的小卡列表
      └── upload      → 上傳小卡

/onboarding           → Onboarding 引導
/posts/
  ├── index           → 貼文列表（備用路由）
  ├── create          → 建立貼文
  └── [id]            → 貼文詳情
/chat/
  └── [roomId]        → 聊天室
```

## 測試檢查清單

- [ ] Tab 導航切換正常
- [ ] Onboarding 畫面顯示正確
- [ ] 偶像團體選擇可以多選
- [ ] 偏好儲存到 Profile.preferences
- [ ] 城市看板顯示貼文列表
- [ ] 相對時間顯示正確（10m, 1h, 2d）
- [ ] Upload Tab 顯示兩種上傳選項
- [ ] Chat Tab 顯示聊天列表
- [ ] Profile Tab 顯示用戶資料
- [ ] Indigo 主色調套用正確

## 未來優化方向

1. **動畫效果**
   - Tab 切換動畫
   - Upload Modal 滑入動畫
   - 卡片展開動畫

2. **Onboarding 整合**
   - 首次登入自動導航到 Onboarding
   - 跳過 Onboarding 的提示

3. **圖片功能**
   - 城市看板顯示實際貼文圖片
   - 圖片預覽與放大

4. **篩選功能**
   - 根據偏好團體智能推薦
   - 標籤點擊篩選

## 技術決策記錄

### Q: 偶像團體資料從哪裡來？

**決策：** 採用前端預設列表 + Profile.preferences 儲存

**理由：**
1. 快速實作，不需要修改後端 schema
2. 使用現有的 `preferences` JSON 欄位
3. 未來可擴展為後端管理的主檔

**替代方案：**
- 方案 1: Profile 新增專屬欄位（需要 migration）
- 方案 3: 後端新增 idol_groups 資料表（需要完整 CRUD）

### Q: Upload 為什麼是獨立 Tab 而非 Modal？

**決策：** 先實作為 Tab，使用 Bottom Sheet 視覺風格

**理由：**
1. Expo Router 的 Tab 結構限制
2. 視覺上模擬 Modal 效果（半透明背景 + 圓角）
3. 保持導航一致性

**未來可優化：**
- 使用真正的 Modal（react-native-modal）
- 點擊遮罩關閉
- 滑動手勢關閉

## 相關文件

- [TECH_STACK.md](../TECH_STACK.md) - 技術棧說明
- [ROUTING_GUIDE.md](../ROUTING_GUIDE.md) - 路由架構
- [ui_prototype.html](../ui_prototype.html) - 原始 UI 原型
