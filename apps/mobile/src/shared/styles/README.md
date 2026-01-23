# 小卡Show! Design System

統一的設計系統，確保整個 App 視覺一致性。

## 🎨 色彩系統 (colors.ts)

### 主品牌色 - 粉紅色系
```typescript
import { colors } from '@/src/shared/styles';

// 使用主品牌色
<Box className={colors.primary[500]} /> // bg-pink-500
<Text className={colors.text.brand} />  // text-pink-500
```

### 漸層色
```typescript
import { gradients } from '@/src/shared/styles';

// Google 按鈕使用的漸層
<Button className={gradients.pinkLight} /> // from-pink-50 to-rose-50
```

## 🌓 陰影系統 (shadows.ts)

### 基礎陰影
```typescript
import { shadows } from '@/src/shared/styles';

// 標準陰影層級
shadows.sm   // 輕微陰影 - 卡片、懸浮元素
shadows.md   // 標準陰影 - 按鈕、互動元素
shadows.lg   // 中等陰影 - 重要卡片
shadows.xl   // 強烈陰影 - Modal、覆蓋層
shadows['2xl'] // 超強陰影 - Logo、強調元素
```

### 粉紅主題陰影
```typescript
import { pinkShadows } from '@/src/shared/styles';

// 品牌色陰影
pinkShadows.sm   // 輕微粉紅陰影
pinkShadows.md   // 標準粉紅陰影
pinkShadows.lg   // 強烈粉紅陰影
pinkShadows.logo // Logo 專用陰影
```

### 品牌元素陰影
```typescript
import { brandShadows } from '@/src/shared/styles';

// 預定義的品牌元素陰影
<Image className={brandShadows.logo} />           // Logo 容器
<Button className={brandShadows.googleButton} />  // Google 按鈕
<Box className={brandShadows.googleIcon} />       // Google G 圖示
<Box className={brandShadows.devSection} />       // 開發者區塊
<Button className={brandShadows.devButton} />     // 開發者按鈕
<Input className={brandShadows.input} />          // 輸入框
```

## 📐 使用範例

### 登入畫面按鈕
```tsx
import { brandShadows, gradients } from '@/src/shared/styles';

<Button 
  className={`w-full h-16 ${gradients.pinkLight} 
              border-2 border-pink-200 rounded-2xl 
              ${brandShadows.googleButton}`}
>
  <ButtonText>使用 Google 帳號登入</ButtonText>
</Button>
```

### 輸入框
```tsx
import { brandShadows } from '@/src/shared/styles';

<Input className={`bg-white ${brandShadows.input}`}>
  <InputField placeholder="電子信箱" />
</Input>
```

### 開發者登入區塊
```tsx
import { brandShadows } from '@/src/shared/styles';

<Box className={`p-4 bg-slate-50 rounded-2xl 
                border border-slate-200 
                ${brandShadows.devSection}`}>
  {/* 內容 */}
</Box>
```

## 🎯 設計原則

### 陰影使用規範

1. **層次分明**
   - 底層元素：`shadow-sm` 或無陰影
   - 中層元素：`shadow-md`（按鈕、卡片）
   - 頂層元素：`shadow-lg` 或 `shadow-xl`（Modal、重要彈窗）

2. **品牌一致性**
   - Logo 使用 `pinkShadows.logo`
   - 品牌按鈕使用 `brandShadows.googleButton`
   - 保持粉紅主題統一

3. **互動反饋**
   - 預設狀態：`shadow-md`
   - Hover 狀態：`shadow-lg`（可選）
   - Active 狀態：`shadow-sm`（可選）

### 色彩使用規範

1. **主品牌色（粉紅）**
   - 主要標題：`text-pink-500`
   - 主要按鈕背景：`bg-gradient-to-r from-pink-50 to-rose-50`
   - 邊框：`border-pink-200`

2. **中性色（灰階）**
   - 副標題：`text-slate-500`
   - 輸入框邊框：`border-slate-200`
   - 開發者區塊：`bg-slate-50`

3. **對比度**
   - 確保文字可讀性（WCAG AA 標準）
   - 粉紅色文字配白色或淺灰背景
   - 深色文字配白色背景

## 🔄 更新指南

如需新增或修改設計系統：

1. 在 `colors.ts` 或 `shadows.ts` 中定義新的樣式
2. 更新此 README 說明使用方式
3. 在相關元件中套用新樣式
4. 確保與整體設計一致

## 📚 相關文件

- [UI 品牌更新文件](../../../UI_BRANDING_UPDATE.md)
- [技術規範](../../../TECH_STACK.md)
- [Tailwind CSS 文件](https://tailwindcss.com/docs)
- [NativeWind 文件](https://www.nativewind.dev/)
