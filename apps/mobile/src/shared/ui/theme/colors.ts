/**
 * Theme Colors - Matching UI Prototype
 * Indigo-600 Primary, Pink-500 Secondary, Slate-50 Background
 */

export const THEME_COLORS = {
  // Primary Colors (Indigo)
  primary: {
    50: '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',
    600: '#4F46E5', // Main Primary
    700: '#4338CA',
    800: '#3730A3',
    900: '#312E81',
  },
  
  // Secondary Colors (Pink)
  secondary: {
    50: '#FDF2F8',
    100: '#FCE7F3',
    200: '#FBCFE8',
    300: '#F9A8D4',
    400: '#F472B6',
    500: '#EC4899', // Main Secondary
    600: '#DB2777',
    700: '#BE185D',
    800: '#9D174D',
    900: '#831843',
  },
  
  // Neutral Colors (Slate)
  neutral: {
    50: '#F8FAFC',  // Background
    100: '#F1F5F9',
    200: '#E2E8F0',
    300: '#CBD5E1',
    400: '#94A3B8', // Inactive
    500: '#64748B',
    600: '#475569',
    700: '#334155',
    800: '#1E293B',
    900: '#0F172A', // Dark Text
  },
  
  // Semantic Colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Special
  white: '#FFFFFF',
  black: '#000000',
  transparent: 'transparent',
} as const;

/**
 * Color Aliases for easier usage
 */
export const COLORS = {
  // Main App Colors
  primary: THEME_COLORS.primary[600],
  primaryLight: THEME_COLORS.primary[50],
  primaryDark: THEME_COLORS.primary[700],
  
  secondary: THEME_COLORS.secondary[500],
  secondaryLight: THEME_COLORS.secondary[50],
  
  background: THEME_COLORS.neutral[50],
  card: THEME_COLORS.white,
  
  // Text Colors
  textPrimary: THEME_COLORS.neutral[900],
  textSecondary: THEME_COLORS.neutral[600],
  textTertiary: THEME_COLORS.neutral[400],
  textOnPrimary: THEME_COLORS.white,
  
  // Border Colors
  border: THEME_COLORS.neutral[200],
  borderActive: THEME_COLORS.primary[600],
  
  // Status Colors
  success: THEME_COLORS.success,
  warning: THEME_COLORS.warning,
  error: THEME_COLORS.error,
  info: THEME_COLORS.info,
  
  // Tab Bar
  tabActive: THEME_COLORS.primary[600],
  tabInactive: THEME_COLORS.neutral[400],
} as const;

/**
 * Shadow Styles
 */
export const SHADOWS = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
} as const;

export type ThemeColor = keyof typeof COLORS;
