/**
 * 小卡Show! Color Theme
 * 
 * 統一的色彩定義，與品牌識別一致
 */

export const colors = {
  // 主品牌色 - 粉紅色系
  primary: {
    50: 'bg-pink-50',
    100: 'bg-pink-100',
    200: 'bg-pink-200',
    300: 'bg-pink-300',
    400: 'bg-pink-400',
    500: 'bg-pink-500', // 主要品牌色
    600: 'bg-pink-600',
    700: 'bg-pink-700',
    800: 'bg-pink-800',
    900: 'bg-pink-900',
  },

  // 輔助色 - 玫瑰色系
  secondary: {
    50: 'bg-rose-50',
    100: 'bg-rose-100',
    200: 'bg-rose-200',
    300: 'bg-rose-300',
    400: 'bg-rose-400', // 輔助品牌色
    500: 'bg-rose-500',
    600: 'bg-rose-600',
    700: 'bg-rose-700',
    800: 'bg-rose-800',
    900: 'bg-rose-900',
  },

  // 中性色 - 灰階
  neutral: {
    50: 'bg-slate-50',
    100: 'bg-slate-100',
    200: 'bg-slate-200',
    300: 'bg-slate-300',
    400: 'bg-slate-400',
    500: 'bg-slate-500',
    600: 'bg-slate-600',
    700: 'bg-slate-700',
    800: 'bg-slate-800',
    900: 'bg-slate-900',
  },

  // 文字色
  text: {
    primary: 'text-slate-900',
    secondary: 'text-slate-600',
    tertiary: 'text-slate-400',
    brand: 'text-pink-500',
    brandDark: 'text-pink-600',
    white: 'text-white',
  },

  // 背景色
  background: {
    primary: 'bg-white',
    secondary: 'bg-slate-50',
    brand: 'bg-pink-50',
  },

  // 邊框色
  border: {
    light: 'border-slate-200',
    medium: 'border-slate-300',
    brand: 'border-pink-200',
    brandStrong: 'border-pink-300',
  },
} as const;

/**
 * 漸層色定義
 */
export const gradients = {
  // 粉紅漸層（品牌）
  pinkLight: 'bg-gradient-to-r from-pink-50 to-rose-50',
  pinkMedium: 'bg-gradient-to-r from-pink-100 to-rose-100',
  pinkStrong: 'bg-gradient-to-r from-pink-500 to-rose-400',
  
  // 灰階漸層
  grayLight: 'bg-gradient-to-r from-slate-50 to-slate-100',
} as const;

export type ColorKey = keyof typeof colors;
export type GradientKey = keyof typeof gradients;
