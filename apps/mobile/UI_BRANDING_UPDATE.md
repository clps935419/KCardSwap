# UI 原型更新實作總結

## 概述

根據 UI 原型（`ui_prototype.html`）的設計規格，完成以下更新：

1. **品牌識別更新**：從 "KCardSwap" 更名為 "小卡Show!"
2. **開發模式登入**：新增帳號密碼登入功能（僅在開發模式下顯示）
3. **中文化**：確保所有用戶可見文案使用中文

## 變更詳情

### 1. 品牌識別更新

#### 登入畫面（`app/auth/login.tsx`）
- ✨ **Logo 圖示**：粉紅色漸層圓角方框 + ✨ emoji
  - 漸層：`from-pink-500 to-rose-400`
  - 圓角：`rounded-3xl`
  - 尺寸：`w-20 h-20`
  - 陰影：`shadow-2xl`

- 🎯 **應用名稱**：「小卡Show!」
  - 字體：`font-black text-slate-900`
  - 大小：`size="2xl"`

- 📝 **副標題**：「Find Your Bias」（保持英文，符合原型）
  - 樣式：`text-slate-400 uppercase tracking-widest`

#### 應用設定（`app.json`）
```json
{
  "name": "小卡Show!"
}
```

#### 配置檔案（`src/shared/config.ts`）
```typescript
appName: process.env.EXPO_PUBLIC_APP_NAME || '小卡Show!'
```

### 2. 開發模式登入

#### 環境變數（`.env.example`）
新增：
```env
# Enable development mode login (email/password login)
# Set to 'true' for development, 'false' for production
EXPO_PUBLIC_ENABLE_DEV_LOGIN=true
```

#### 配置檔案更新（`src/shared/config.ts`）
新增：
```typescript
enableDevLogin: process.env.EXPO_PUBLIC_ENABLE_DEV_LOGIN === 'true'
export const isDevLoginEnabled = config.enableDevLogin;
```

#### 登入頁面功能（`app/auth/login.tsx`）

**開發模式下顯示：**
- 電子信箱輸入欄位
- 密碼輸入欄位（`secureTextEntry`）
- 「開發者登入」按鈕
- 灰色背景區塊（`bg-slate-50`）與「開發者模式」標籤

**登入流程：**
1. 使用 `adminLoginApiV1AuthAdminLoginPost` API
2. 驗證帳號密碼
3. 儲存 tokens 到 Zustand store
4. 導航至主應用 `/(tabs)`

**錯誤處理：**
- 401：「帳號或密碼錯誤」
- 404：「找不到此帳號」
- 其他：「登入失敗，請檢查帳號密碼是否正確。」

**生產模式：**
- 不顯示帳號密碼欄位
- 只保留 Google 登入按鈕

### 3. 中文化更新

#### 登入頁面（`app/auth/login.tsx`）
- ✅ 錯誤訊息全部中文化
- ✅ 按鈕文字：「使用 Google 帳號登入」
- ✅ 服務條款文字：「登入即表示您同意本平台的服務條款與隱私協議。」
- ✅ 載入提示：「正在連接帳號...」

#### AuthStore（`src/shared/state/authStore.ts`）
- ✅ 「儲存驗證資料失敗」
- ✅ 「登入失敗，請再試一次。」
- ✅ 「登出失敗，請再試一次。」

#### Tab 導航（`app/(tabs)/_layout.tsx`）
已確認為中文：
- 城市看板
- 附近
- 上傳
- 聊天
- 個人

### 4. Git 配置更新

#### `.gitignore`
新增：
```
.env
```

確保 `.env` 檔案不會被提交到版本控制。

## 使用方式

### 開發模式（顯示帳號密碼登入）

建立 `.env` 檔案：
```bash
cp .env.example .env
```

確保包含：
```env
EXPO_PUBLIC_ENABLE_DEV_LOGIN=true
```

### 生產模式（僅 Google 登入）

修改 `.env`：
```env
EXPO_PUBLIC_ENABLE_DEV_LOGIN=false
```

或修改 `EXPO_PUBLIC_ENV=production`

## UI 預覽

### 開發模式登入畫面
```
┌─────────────────────┐
│                     │
│       ┌────┐        │  ← Logo (粉紅漸層)
│       │ ✨ │        │
│       └────┘        │
│                     │
│     小卡Show!       │  ← 應用名稱
│   Find Your Bias    │  ← 副標題
│                     │
├─────────────────────┤
│   [開發者模式]      │  ← 灰色區塊
│                     │
│  ┌─────────────┐    │
│  │ 電子信箱    │    │  ← Email 輸入
│  └─────────────┘    │
│                     │
│  ┌─────────────┐    │
│  │ ●●●●●●●●   │    │  ← 密碼輸入
│  └─────────────┘    │
│                     │
│  [開發者登入]       │  ← 登入按鈕
│                     │
├─────────────────────┤
│                     │
│  [ G ] 使用 Google  │  ← Google 登入
│        帳號登入     │
│                     │
│  登入即表示您同意...│  ← 服務條款
└─────────────────────┘
```

### 生產模式登入畫面
```
┌─────────────────────┐
│                     │
│       ┌────┐        │
│       │ ✨ │        │
│       └────┘        │
│                     │
│     小卡Show!       │
│   Find Your Bias    │
│                     │
│                     │
│  [ G ] 使用 Google  │  ← 只有 Google 登入
│        帳號登入     │
│                     │
│  登入即表示您同意...│
└─────────────────────┘
```

## 技術細節

### API 整合
- 使用 hey-api 生成的 SDK：`adminLoginApiV1AuthAdminLoginPost`
- Request Body：
  ```typescript
  {
    email: string;
    password: string;
  }
  ```
- Response：與 Google OAuth 相同格式
  ```typescript
  {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    user_id: string;
    email: string;
  }
  ```

### 狀態管理
使用 Zustand 的 `useAuthStore`：
```typescript
await login(
  {
    accessToken: result.access_token,
    refreshToken: result.refresh_token,
    expiresAt: Date.now() + result.expires_in * 1000,
  },
  {
    id: result.user_id,
    email: result.email,
  }
);
```

## 測試檢查清單

- [ ] 開發模式下可看到帳號密碼登入欄位
- [ ] 可使用帳號密碼成功登入
- [ ] 錯誤訊息正確顯示（中文）
- [ ] 生產模式下只顯示 Google 登入
- [ ] Logo 與品牌名稱正確顯示
- [ ] 所有文案為中文（除副標題）

## 參考文件

- UI 原型：`apps/mobile/ui_prototype.html`
- 技術規範：`apps/mobile/TECH_STACK.md`
- 路由指南：`apps/mobile/ROUTING_GUIDE.md`
