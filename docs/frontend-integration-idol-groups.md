# 前端整合：Idol Groups API

## 概述

已完成前端整合，OnboardingScreen 現在從後端 API 獲取偶像團體列表，不再使用硬編碼資料。

## 實作內容

### 1. 創建 Profile Hooks

#### `useProfile.ts`
- `useMyProfile()`: 查詢個人檔案
- `useUpdateProfile()`: 更新個人檔案

#### `useIdolGroups.ts`
- `useIdolGroups()`: 從 API 獲取偶像團體列表
- 資料快取：1 小時 (staleTime)
- 快取保留：24 小時 (gcTime)

### 2. 更新 OnboardingScreen

#### 變更內容
- **移除**: `import { DEFAULT_IDOL_GROUPS }`（硬編碼常數）
- **新增**: `import { useIdolGroups, useUpdateProfile }`
- **新增**: 載入狀態 UI (Spinner + 提示文字)
- **新增**: 錯誤狀態 UI (錯誤訊息 + 稍後再說按鈕)
- **更新**: 使用 `idolGroups` (從 API) 替代 `DEFAULT_IDOL_GROUPS`

#### UI 狀態流程
```
載入中 (isLoading)
    ↓
    ├─→ 成功: 顯示偶像團體網格
    └─→ 失敗: 顯示錯誤訊息 + 稍後再說按鈕
```

## 程式碼範例

### 使用 useIdolGroups Hook

```typescript
const { data: idolGroups, isLoading, error } = useIdolGroups();

// idolGroups: IdolGroupResponse[] = [
//   { id: "newjeans", name: "NewJeans", emoji: "👖" },
//   { id: "ive", name: "IVE", emoji: "🦢" },
//   ...
// ]
```

### 載入狀態

```tsx
{isLoading && (
  <Box className="items-center justify-center py-12">
    <Spinner size="large" />
    <Text className="text-sm text-gray-500 mt-4">載入偶像團體...</Text>
  </Box>
)}
```

### 錯誤狀態

```tsx
{error && (
  <Box className="items-center justify-center py-12">
    <Text className="text-sm text-red-500 mb-4">載入失敗，請稍後再試</Text>
    <Button size="sm" onPress={() => router.replace('/(tabs)')}>
      <ButtonText>稍後再說</ButtonText>
    </Button>
  </Box>
)}
```

## 技術特性

### 資料快取策略
- **staleTime**: 1 小時 - 偶像團體資料不常變更
- **gcTime**: 24 小時 - 長時間保留在快取中
- 使用者重新開啟 app 時不需要重新載入（快取有效期內）

### 錯誤處理
- 網路錯誤：顯示錯誤訊息，允許使用者跳過
- API 失敗：不阻塞使用者繼續流程
- 保留「稍後再說」選項作為後備

### 型別安全
- 使用 TypeScript 類型：`IdolGroupResponse`
- 從生成的 SDK 導入類型，確保與後端一致
- 完整的型別推斷和檢查

## 測試建議

### 手動測試場景
1. **正常流程**: API 正常回應，顯示 12 個偶像團體
2. **載入狀態**: 網路慢時顯示載入動畫
3. **錯誤處理**: 
   - 離線狀態測試
   - API 伺服器停止測試
4. **快取驗證**: 
   - 第一次載入後關閉 app
   - 重新開啟 app，應立即顯示（從快取）

### 預期結果
- ✅ 首次載入顯示 Spinner
- ✅ 載入成功後顯示 12 個偶像團體（與原本硬編碼相同）
- ✅ 選擇團體和儲存功能正常運作
- ✅ 快取生效，重新開啟不需重新載入

## 向後相容性

保留 `constants/idolGroups.ts` 檔案作為：
- 型別定義參考
- 後備資料（如需要）
- 文件說明

未來可以移除此檔案，完全依賴 API。

## 效益

1. ✅ **統一資料來源**: 後端控制偶像團體列表
2. ✅ **動態更新**: 新增團體不需更新 app
3. ✅ **型別安全**: SDK 自動生成，保證一致性
4. ✅ **良好 UX**: 載入和錯誤狀態友善
5. ✅ **效能優化**: 快取策略減少不必要的請求
