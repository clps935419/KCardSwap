/**
 * 小卡Show! Shadow Design System
 * 
 * 統一的陰影風格定義，確保整個 App 視覺一致性
 */

export const shadows = {
  // 無陰影
  none: '',
  
  // 輕微陰影 - 用於懸浮元素、卡片
  sm: 'shadow-sm',
  
  // 標準陰影 - 用於按鈕、輸入框等互動元素
  md: 'shadow-md',
  
  // 中等陰影 - 用於較重要的卡片、浮動面板
  lg: 'shadow-lg',
  
  // 強烈陰影 - 用於 Modal、Drawer 等覆蓋層
  xl: 'shadow-xl',
  
  // 超強陰影 - 用於強調的重點元素
  '2xl': 'shadow-2xl',
} as const;

/**
 * 粉紅主題陰影 - 用於品牌相關元素
 */
export const pinkShadows = {
  // 輕微粉紅陰影
  sm: 'shadow-sm shadow-pink-100',
  
  // 標準粉紅陰影
  md: 'shadow-md shadow-pink-200/50',
  
  // 強烈粉紅陰影
  lg: 'shadow-lg shadow-pink-200',
  
  // Logo 專用陰影
  logo: 'shadow-2xl shadow-pink-200',
} as const;

/**
 * 互動狀態陰影
 */
export const interactiveShadows = {
  // 按鈕預設狀態
  button: {
    default: shadows.md,
    hover: shadows.lg,
    active: shadows.sm,
  },
  
  // 卡片陰影
  card: {
    default: shadows.sm,
    hover: shadows.md,
  },
  
  // 輸入框陰影
  input: {
    default: shadows.sm,
    focus: shadows.md,
  },
} as const;

/**
 * 品牌元素陰影配置
 */
export const brandShadows = {
  // Logo 容器
  logo: pinkShadows.logo,
  
  // Google 按鈕
  googleButton: shadows.md,
  
  // Google G 圖示
  googleIcon: shadows.sm,
  
  // 開發者登入區塊
  devSection: shadows.sm,
  
  // 開發者登入按鈕
  devButton: shadows.md,
  
  // 輸入框
  input: shadows.sm,
} as const;

export type ShadowKey = keyof typeof shadows;
export type PinkShadowKey = keyof typeof pinkShadows;
export type BrandShadowKey = keyof typeof brandShadows;
