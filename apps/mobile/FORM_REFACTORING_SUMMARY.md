# 前端表單與狀態管理改進總結

## 執行日期
2026-01-15

## 問題分析

### 1. 表單狀態管理問題
- **問題**: 使用多個獨立的 `useState` 管理表單欄位
- **影響**: 程式碼冗長、難以維護、缺乏統一驗證機制
- **範例**: `profile.tsx` 使用 6 個 useState，每個欄位需要手動管理

### 2. 驗證邏輯分散
- **問題**: 驗證邏輯分散在各個檔案中 (validateNickname, validateBio)
- **影響**: 重複程式碼、不一致的驗證規則、難以測試

### 3. 狀態寫法不一致
- **觀察**: 各頁面狀態管理方式不同
  - 有些使用 TanStack Query (good)
  - 有些手動管理 API 狀態
  - 表單狀態管理混亂

## 解決方案

### 1. 導入 React Hook Form + Zod

**技術選型理由:**
- **React Hook Form**: 主流 React 表單庫，性能優異，API 簡潔
- **Zod**: TypeScript-first 驗證庫，與 React Hook Form 完美整合
- **社群支援**: 2024-2025 最推薦的表單管理方案

**安裝套件:**
```bash
npm install react-hook-form zod @hookform/resolvers
```

### 2. 建立集中式表單 Schemas

建立 `/src/shared/forms/schemas.ts` 集中管理所有表單驗證規則:

```typescript
// Profile Form Schema
export const profileFormSchema = z.object({
  nickname: z.string().min(1).max(50)...
  bio: z.string().max(500).optional()
  ...
});

// Card Upload Form Schema
export const cardUploadFormSchema = z.object({
  idol: z.string().optional()
  ...
});
```

**優點:**
- 集中管理所有驗證規則
- 自動生成 TypeScript 類型
- 可重複使用驗證邏輯
- 易於測試

### 3. 頁面重構

#### Profile.tsx 改進

**Before (舊寫法):**
```typescript
// 6 個獨立的 useState
const [nickname, setNickname] = useState('');
const [bio, setBio] = useState('');
const [nearbyVisible, setNearbyVisible] = useState(true);
const [showOnline, setShowOnline] = useState(true);
const [allowStrangerChat, setAllowStrangerChat] = useState(true);
const [isEditing, setIsEditing] = useState(false);

// 手動驗證
const handleSave = async () => {
  const nicknameError = validateNickname(nickname);
  if (nicknameError) {
    Alert.alert('Validation Error', nicknameError);
    return;
  }
  ...
};
```

**After (新寫法):**
```typescript
// 使用 React Hook Form
const {
  control,
  handleSubmit,
  reset,
  watch,
  formState: { errors, isDirty },
} = useForm<ProfileFormData>({
  resolver: zodResolver(profileFormSchema),
  defaultValues: { ... },
});

// 自動驗證
const onSubmit = async (data: ProfileFormData) => {
  // data 已通過 Zod 驗證
  await updateProfile.mutateAsync({ body: { ... } });
};
```

**改進點:**
- ✅ 減少 6 個 useState 為 1 個 useForm
- ✅ 自動表單驗證
- ✅ 自動錯誤提示
- ✅ 自動髒值追蹤 (isDirty)
- ✅ 簡化重置邏輯
- ✅ 更好的 TypeScript 類型安全

#### UploadCardScreen 改進

**Before:**
```typescript
const [idol, setIdol] = useState('');
const [idolGroup, setIdolGroup] = useState('');
const [album, setAlbum] = useState('');
const [version, setVersion] = useState('');
const [rarity, setRarity] = useState<CardRarity>('common');
```

**After:**
```typescript
const {
  control,
  getValues,
  watch,
} = useForm<CardUploadFormData>({
  resolver: zodResolver(cardUploadFormSchema),
  defaultValues: { ... },
});
```

**改進點:**
- ✅ 減少 5 個 useState 為 1 個 useForm
- ✅ 使用 Controller 包裝表單欄位
- ✅ 更好的程式碼結構

### 4. UI 框架使用檢查

**檢查結果:**
- ✅ profile.tsx: 正確使用 Gluestack UI 元件
- ✅ UploadCardScreen: 正確使用 Gluestack UI 元件
- ✅ FriendsListScreen: 正確使用 Gluestack UI 元件
- ✅ HomeScreen: 正確使用 Gluestack UI 元件
- ⚠️ CreatePostScreen: 使用不存在的 Textarea、Select 元件 (需要添加)

**修正:**
- 將 Input 的 `disabled` 屬性改為 `isDisabled` (Gluestack UI 正確屬性)

## 待完成工作

### 1. 添加缺少的 Gluestack UI 元件

```bash
npx gluestack-ui@latest add textarea
npx gluestack-ui@latest add select
```

### 2. 完成 CreatePostScreen 重構

目前已部分重構，但需要等待 Textarea 和 Select 元件添加後才能完成。

### 3. 其他頁面檢查

建議檢查以下頁面是否可以使用 React Hook Form:
- SendRequestScreen (好友請求)
- TradeDetailScreen (交易表單)
- ChatRoomScreen (聊天輸入)

## 效益總結

### 程式碼品質提升

1. **程式碼行數減少**
   - profile.tsx: ~40 行減少
   - UploadCardScreen: ~30 行減少

2. **可維護性提升**
   - 集中式驗證規則
   - 統一的表單處理邏輯
   - 更好的類型安全

3. **使用者體驗改進**
   - 即時表單驗證
   - 更好的錯誤提示
   - 自動髒值追蹤 (未修改時禁用儲存按鈕)

### 技術債務減少

- ❌ 移除分散的驗證函式
- ❌ 移除重複的表單邏輯
- ✅ 引入業界標準的表單管理方案
- ✅ 提升程式碼一致性

## 最佳實踐建議

### 1. 表單狀態管理原則

- **使用 React Hook Form** 處理所有表單
- **使用 Zod** 定義驗證規則
- **使用 Controller** 包裝自定義 UI 元件
- **避免使用多個 useState** 管理表單欄位

### 2. 伺服器狀態管理原則

- **使用 TanStack Query** 處理所有 API 呼叫
- **避免手動管理** loading/error 狀態
- **使用 mutation** 處理資料變更
- **使用 queryClient.invalidateQueries** 更新快取

### 3. UI 元件使用原則

- **優先使用 Gluestack UI** 元件
- **使用 className** 而非 StyleSheet
- **使用 @/ 路徑別名** 而非相對路徑
- **遵循專案的 UI 元件結構**

## 參考資源

- [React Hook Form 官方文檔](https://react-hook-form.com/)
- [Zod 官方文檔](https://zod.dev/)
- [TanStack Query 官方文檔](https://tanstack.com/query)
- [Gluestack UI 官方文檔](https://gluestack.io/ui/docs)

## 結論

本次改進成功導入了業界標準的表單管理方案，大幅提升了程式碼品質和可維護性。建議後續:

1. 添加 Textarea 和 Select 元件完成 CreatePostScreen 重構
2. 檢查其他頁面是否可以使用相同方案
3. 建立表單處理的開發指南文件
4. 進行完整的測試驗證
