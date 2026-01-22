# Router Entry Point Fix

## 問題描述

之前的實作中，App 啟動後會停在 `App.tsx` 頁面，無法正確進入路由系統和登入流程。

### 根本原因

- `package.json` 的 `main` 欄位設定為 `index.ts`
- `index.ts` 直接呼叫 `registerRootComponent(App)` 渲染 `App.tsx`
- 這繞過了 Expo Router 和 `app/_layout.tsx` 的導頁邏輯

## 修正內容

### 1. 變更入口點 (package.json)

```diff
- "main": "index.ts",
+ "main": "expo-router/entry",
```

這是 Expo Router 的標準入口設定方式，參考：[Expo Router 官方文件](https://docs.expo.dev/router/installation/#setup-entry-point)

### 2. 移除舊的入口檔案

- **刪除 `index.ts`**: 不再需要手動註冊根元件
- **刪除 `App.tsx`**: 不再作為入口元件使用

這兩個檔案在 Expo Router 架構中不再需要，因為：
- Expo Router 自動處理應用程式入口
- `app/_layout.tsx` 成為實際的根佈局元件

## 預期行為

### 應用程式啟動流程

1. **應用程式啟動** → 讀取 `expo-router/entry`
2. **Expo Router 初始化** → 載入 `app/_layout.tsx`
3. **_layout.tsx 執行邏輯**:
   ```typescript
   // 初始化認證狀態
   useEffect(() => {
     initialize();
   }, []);

   // 根據認證狀態導航
   useEffect(() => {
     if (isLoading) return;

     const inAuthGroup = segments[0] === 'auth';

     if (!isAuthenticated && !inAuthGroup) {
       // 未登入 → 導向登入頁面
       router.replace('/auth/login');
     } else if (isAuthenticated && inAuthGroup) {
       // 已登入 → 導向主應用
       router.replace('/(tabs)');
     }
   }, [isAuthenticated, isLoading, segments]);
   ```

### 各種情境的預期畫面

| 情境 | 預期行為 | 顯示頁面 |
|------|---------|---------|
| 首次啟動（未登入） | 自動導向登入頁面 | `/auth/login` |
| 已登入（有 token） | 自動導向主頁面 | `/(tabs)` (首頁) |
| Token 過期 | 嘗試刷新，失敗則登出 | `/auth/login` |
| 手動登出 | 清除認證資料 | `/auth/login` |

## 驗證方式

### 1. 本地開發測試

```bash
cd apps/mobile

# 確保有 .env 檔案
cp .env.example .env

# 安裝依賴
npm install --legacy-peer-deps

# 啟動開發伺服器
npm start

# 在模擬器或實體裝置上執行
npm run android  # Android
npm run ios      # iOS (僅 macOS)
npm run web      # Web 瀏覽器
```

### 2. 檢查初始畫面

**未登入狀態**:
- ✅ 應該看到登入頁面 (Welcome to KCardSwap)
- ✅ 有 "Sign in with Google" 按鈕
- ❌ 不應該看到 "Open up App.tsx to start working"

**已登入狀態** (有儲存的 token):
- ✅ 應該看到主應用的 5-tab 導航
- ✅ 顯示首頁（城市看板）
- ❌ 不應該被導向登入頁面

### 3. TypeScript 編譯檢查

```bash
npm run type-check
```

應該只有測試檔案的型別錯誤（既存問題），主要程式碼應該正常編譯。

### 4. 路由檢查

使用 Expo Dev Tools 檢查路由：
- 在終端機輸入 `m` 開啟選單
- 選擇 "Dev menu" → "React Native DevTools"
- 檢查當前路由是否為 `/auth/login` (未登入) 或 `/(tabs)` (已登入)

## 技術細節

### Expo Router 入口機制

當使用 `expo-router/entry` 作為入口時：

1. Expo Router 自動偵測 `app/` 目錄
2. 載入 `app/_layout.tsx` 作為根佈局
3. 根據檔案系統自動生成路由
4. 處理深層連結和導航邏輯

### 認證流程整合

`app/_layout.tsx` 整合了：
- **Zustand Auth Store**: 管理認證狀態
- **TanStack Query**: 處理 API 請求
- **Gluestack UI Provider**: 提供 UI 元件主題
- **Expo Router**: 處理路由導航

## 相關檔案

- `apps/mobile/package.json` - 入口點設定
- `apps/mobile/app/_layout.tsx` - 根佈局和認證邏輯
- `apps/mobile/app/auth/login.tsx` - 登入頁面
- `apps/mobile/src/shared/state/authStore.ts` - 認證狀態管理
- `apps/mobile/src/shared/auth/session.ts` - Token 儲存邏輯

## 常見問題

### Q: 啟動後還是看到 "Open up App.tsx" 的訊息？

A: 清除 Metro bundler 快取：
```bash
npx expo start --clear
```

### Q: 出現 "Cannot find module 'expo-router/entry'" 錯誤？

A: 重新安裝依賴：
```bash
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Q: 應用程式閃退或白畫面？

A: 檢查以下項目：
1. `.env` 檔案是否存在並設定正確
2. 檢查終端機的錯誤訊息
3. 確認 `app/_layout.tsx` 中的 imports 都正確

### Q: 如何測試未登入狀態？

A: 可以在登入後手動清除認證資料：
```typescript
// 在 dev tools console 執行
import { useAuthStore } from '@/src/shared/state/authStore';
useAuthStore.getState().logout();
```

或直接刪除模擬器/裝置上的應用程式資料。

## 參考資料

- [Expo Router 官方文件](https://docs.expo.dev/router/introduction/)
- [Expo Router Installation](https://docs.expo.dev/router/installation/)
- [Expo Router Authentication](https://docs.expo.dev/router/reference/authentication/)
- [專案的 ROUTING_GUIDE.md](./ROUTING_GUIDE.md)
- [專案的 TECH_STACK.md](./TECH_STACK.md)
