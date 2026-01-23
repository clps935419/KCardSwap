# UI 更新對比：從 KCardSwap 到 小卡Show!

## 視覺對比

### 登入畫面

#### Before (KCardSwap)
```
┌─────────────────────────────┐
│                             │
│                             │
│        KCardSwap            │  ← 紫色文字 (rgb(169,142,216))
│      Find Your Bias         │
│                             │
│                             │
│  ┌─────────────────────┐    │
│  │  G  使用 Google     │    │  ← 單一登入選項
│  │     帳號登入        │    │
│  └─────────────────────┘    │
│                             │
│  登入即表示您同意...        │
│                             │
└─────────────────────────────┘
```

#### After (小卡Show!)
```
┌─────────────────────────────┐
│                             │
│        ┌────────┐           │
│        │   ✨   │           │  ← NEW: 粉紅色漸層 Logo
│        └────────┘           │      (Pink-500 → Rose-400)
│                             │
│       小卡Show!             │  ← NEW: 黑色粗體
│     Find Your Bias          │      (與 UI 原型一致)
│                             │
├─ 開發模式 ──────────────────┤  ← NEW: 僅開發模式顯示
│  ┌─────────────────────┐    │
│  │  電子信箱           │    │  ← NEW: Email 輸入
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │  ●●●●●●●●●●        │    │  ← NEW: 密碼輸入
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │   開發者登入        │    │  ← NEW: 登入按鈕
│  └─────────────────────┘    │
├─────────────────────────────┤
│  ┌─────────────────────┐    │
│  │  G  使用 Google     │    │  ← Google 登入保留
│  │     帳號登入        │    │
│  └─────────────────────┘    │
│                             │
│  登入即表示您同意...        │
│                             │
└─────────────────────────────┘
```

## 變更清單

### 1. 品牌識別

| 項目 | Before | After |
|------|--------|-------|
| 應用名稱 | KCardSwap | 小卡Show! |
| Logo | 無 | ✨ 粉紅色漸層方框 |
| 主色調 | 紫色 (Indigo) | 粉紅色 (Pink-Rose) |
| 字體樣式 | text-[rgb(169,142,216)] | text-slate-900 font-black |
| Logo 尺寸 | - | w-20 h-20 rounded-3xl |
| Logo 漸層 | - | from-pink-500 to-rose-400 |

### 2. 登入功能

| 功能 | Before | After |
|------|--------|-------|
| Google 登入 | ✅ | ✅ |
| 帳號密碼登入 | ❌ | ✅ (開發模式) |
| 模式切換 | - | 環境變數控制 |
| 錯誤訊息語言 | 英文 | 中文 |

### 3. 開發體驗

| 項目 | Before | After |
|------|--------|-------|
| 測試帳號登入 | 需要 Google OAuth | 可用帳號密碼 |
| 環境切換 | - | EXPO_PUBLIC_ENABLE_DEV_LOGIN |
| 生產模式 | - | 自動隱藏開發登入 |

## 技術實作對比

### Config 配置

#### Before
```typescript
// src/shared/config.ts
export const config = {
  appName: process.env.EXPO_PUBLIC_APP_NAME || 'KCardSwap',
  // ...
};
```

#### After
```typescript
// src/shared/config.ts
export const config = {
  appName: process.env.EXPO_PUBLIC_APP_NAME || '小卡Show!',
  enableDevLogin: process.env.EXPO_PUBLIC_ENABLE_DEV_LOGIN === 'true',
  // ...
};

export const isDevLoginEnabled = config.enableDevLogin;
```

### 登入組件

#### Before - 單一 Google 登入
```tsx
<Button onPress={handleGoogleLogin}>
  <ButtonText>使用 Google 帳號登入</ButtonText>
</Button>
```

#### After - 條件式雙登入
```tsx
{isDevLoginEnabled && (
  <Box>
    <Input>
      <InputField placeholder="電子信箱" />
    </Input>
    <Input>
      <InputField placeholder="密碼" secureTextEntry />
    </Input>
    <Button onPress={handleDevLogin}>
      <ButtonText>開發者登入</ButtonText>
    </Button>
  </Box>
)}

<Button onPress={handleGoogleLogin}>
  <ButtonText>使用 Google 帳號登入</ButtonText>
</Button>
```

## UI 原型符合度

### Logo 設計 ✅

根據 `ui_prototype.html` 第 156 行：
```html
<h3 class="text-xl font-black text-slate-900">小卡Show!</h3>
```

我們的實作：
```tsx
<Heading size="2xl" className="font-black text-slate-900">
  小卡Show!
</Heading>
```

### Logo 圖示 ✅

根據 UI 原型第 399 行：
```html
<div class="w-20 h-20 bg-gradient-to-br from-pink-500 to-rose-400 
     rounded-3xl flex items-center justify-center">
  ✨
</div>
```

我們的實作：
```tsx
<Box className="w-20 h-20 bg-gradient-to-br from-pink-500 to-rose-400 
              rounded-3xl items-center justify-center">
  <Text size="3xl">✨</Text>
</Box>
```

### 按鈕樣式 ✅

根據 UI 原型第 406 行：
```html
<button class="w-full h-16 bg-white border border-slate-200 
               rounded-2xl shadow-sm">
  使用 Google 帳號登入
</button>
```

我們的實作：
```tsx
<Button className="w-full h-16 bg-white border border-slate-200 
                   rounded-2xl shadow-sm">
  <ButtonText>使用 Google 帳號登入</ButtonText>
</Button>
```

## 測試場景

### Scenario 1: 開發環境測試
```bash
# .env
EXPO_PUBLIC_ENABLE_DEV_LOGIN=true
```

**預期結果：**
- ✅ 顯示「小卡Show!」+ ✨ Logo
- ✅ 顯示「開發者模式」區塊
- ✅ 可輸入帳號密碼
- ✅ 可點擊「開發者登入」
- ✅ 顯示 Google 登入按鈕

### Scenario 2: 生產環境
```bash
# .env
EXPO_PUBLIC_ENABLE_DEV_LOGIN=false
```

**預期結果：**
- ✅ 顯示「小卡Show!」+ ✨ Logo
- ✅ 不顯示「開發者模式」區塊
- ✅ 只顯示 Google 登入按鈕

### Scenario 3: 帳號密碼登入流程
```
1. 輸入 email: admin@example.com
2. 輸入 password: ********
3. 點擊「開發者登入」
4. API 呼叫: POST /api/v1/auth/admin-login
5. 成功 → 儲存 tokens → 導航至 /(tabs)
6. 失敗 → 顯示中文錯誤訊息
```

## 文件更新

### 新增文件
- ✅ `UI_BRANDING_UPDATE.md` - 完整實作說明
- ✅ `verify-branding-update.js` - 驗證腳本

### 更新文件
- ✅ `.env.example` - 新增開發模式變數
- ✅ `app.json` - 應用名稱更新
- ✅ `.gitignore` - 排除 .env

## 檢查清單

### 品牌更新 ✅
- [x] Logo 為粉紅色漸層 + ✨
- [x] 應用名稱為「小卡Show!」
- [x] 副標題為「Find Your Bias」
- [x] 配色符合 UI 原型

### 開發模式 ✅
- [x] 環境變數控制顯示
- [x] 帳號密碼輸入欄位
- [x] 登入 API 整合
- [x] 錯誤處理中文化

### 測試 ✅
- [x] 驗證腳本通過
- [x] 開發模式切換正常
- [x] 生產模式切換正常

### 文件 ✅
- [x] 實作文件完整
- [x] 使用說明清楚
- [x] 對比圖表完善
