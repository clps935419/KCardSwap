/**
 * Theme Tokens
 * 
 * Centralized theme configuration for KCardSwap mobile app.
 * Color palette inspired by Korean minimalist girl aesthetic:
 * - Soft lavender (primary)
 * - Blush pink (secondary)
 * - Dreamy mint (tertiary)
 * - Gentle pastels for feedback colors
 * 
 * Keywords: 韓系 (Korean style), 女孩 (girl), 卡片 (card), 簡約 (minimalist)
 * 
 * @see src/shared/ui/components/gluestack-ui-provider/config.ts for full configuration
 */

/**
 * Color Tokens
 * 
 * RGB format: 'R G B' (space-separated values)
 * Usage in Tailwind: text-[rgb(var(--color-primary-500))]
 * 
 * Design Philosophy:
 * - Primary: Soft lavender (#B984DF area) - Main brand color, feminine and calming
 * - Secondary: Blush pink (#FEC5E5, #FFB7C5) - Cherry blossom inspired, romantic
 * - Tertiary: Dreamy mint (#B8E4DC, #E4F1CB) - Fresh and clean, Korean aesthetic
 */
export const colors = {
  primary: {
    // Soft Lavender - Korean aesthetic inspired
    0: '252 248 255',      // Very light lavender
    50: '245 239 254',     // Ultra soft lavender
    100: '237 229 252',    // Light lavender
    200: '220 208 247',    // Soft lavender
    300: '201 185 240',    // Medium lavender
    400: '185 164 228',    // Floral lavender (#B984DF)
    500: '169 142 216',    // Main lavender
    600: '149 119 193',    // Deep lavender
    700: '128 95 169',     // Darker lavender
    800: '102 76 135',     // Very dark lavender
    900: '76 57 101',      // Deepest lavender
    950: '51 38 68',       // Almost black lavender
  },
  secondary: {
    // Blush Pink - Cherry blossom inspired
    0: '255 251 252',      // Almost white pink
    50: '255 247 249',     // Very light pink
    100: '255 237 242',    // Light blush (#FCEDF2)
    200: '255 220 230',    // Soft blush
    300: '255 197 213',    // Cherry blossom (#FFB7C5)
    400: '254 181 202',    // Medium blush
    500: '254 197 229',    // Blush pink (#FEC5E5)
    600: '255 156 184',    // Deep blush
    700: '240 131 161',    // Darker pink
    800: '214 106 136',    // Very dark pink
    900: '171 85 109',     // Deepest pink
    950: '114 57 73',      // Almost black pink
  },
  tertiary: {
    // Soft Mint - Fresh and clean Korean aesthetic
    0: '247 254 252',      // Almost white mint
    50: '236 252 247',     // Very light mint
    100: '224 249 241',    // Light mint (#E4F1CB)
    200: '201 241 228',    // Soft mint
    300: '184 228 220',    // Dreamy mint (#B8E4DC)
    400: '156 217 204',    // Medium mint
    500: '140 207 193',    // Main mint
    600: '115 186 172',    // Deep mint
    700: '92 158 146',     // Darker mint
    800: '74 131 121',     // Very dark mint
    900: '56 99 92',       // Deepest mint
    950: '37 66 61',       // Almost black mint
  },
  error: {
    // Soft Coral - Gentle error feedback
    0: '255 246 245',
    50: '255 237 235',
    100: '255 220 215',
    200: '255 194 186',
    300: '255 162 149',
    400: '251 134 119',
    500: '242 106 91',
    600: '224 84 73',
    700: '197 66 58',
    800: '165 54 48',
    900: '128 45 41',
    950: '85 30 27',
  },
  success: {
    // Soft Sage Green - Gentle success feedback
    0: '244 251 246',
    50: '233 247 237',
    100: '214 240 221',
    200: '186 229 198',
    300: '149 213 168',
    400: '116 196 141',
    500: '92 184 121',
    600: '72 161 102',
    700: '57 135 84',
    800: '46 109 69',
    900: '38 86 56',
    950: '25 57 37',
  },
  warning: {
    // Soft Peach - Gentle warning feedback
    0: '255 251 247',
    50: '255 246 237',
    100: '255 238 222',
    200: '255 221 189',
    300: '255 199 149',
    400: '255 176 112',
    500: '255 158 88',
    600: '242 135 63',
    700: '217 112 44',
    800: '179 91 36',
    900: '140 72 30',
    950: '92 47 20',
  },
  info: {
    // Soft Sky Blue - Gentle info feedback
    0: '245 251 255',
    50: '235 247 255',
    100: '220 241 255',
    200: '194 231 255',
    300: '156 217 252',
    400: '115 200 246',
    500: '82 186 240',
    600: '56 167 225',
    700: '41 141 196',
    800: '35 116 161',
    900: '33 92 126',
    950: '22 61 84',
  },
} as const;

/**
 * Spacing Tokens
 * 
 * Base unit: 4px
 * Scale: 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 24, 32, 40, 48, 56, 64
 */
export const spacing = {
  0: 0,
  0.5: 2,
  1: 4,
  1.5: 6,
  2: 8,
  2.5: 10,
  3: 12,
  3.5: 14,
  4: 16,
  5: 20,
  6: 24,
  7: 28,
  8: 32,
  9: 36,
  10: 40,
  11: 44,
  12: 48,
  16: 64,
  20: 80,
  24: 96,
  32: 128,
  40: 160,
  48: 192,
  56: 224,
  64: 256,
} as const;

/**
 * Typography Tokens
 * 
 * Font families and text sizes
 */
export const typography = {
  fontFamily: {
    heading: undefined, // Use system default
    body: undefined, // Use system default
    mono: 'Courier New, monospace',
  },
  fontSize: {
    '2xs': 10,
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48,
    '6xl': 60,
    '7xl': 72,
    '8xl': 96,
    '9xl': 128,
  },
  fontWeight: {
    hairline: '100',
    thin: '200',
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
    black: '900',
  },
  lineHeight: {
    '2xs': 16,
    xs: 18,
    sm: 20,
    md: 22,
    lg: 24,
    xl: 28,
    '2xl': 32,
    '3xl': 40,
    '4xl': 48,
    '5xl': 64,
    '6xl': 72,
    '7xl': 90,
    '8xl': 96,
    '9xl': 128,
  },
} as const;

/**
 * Border Radius Tokens
 */
export const borderRadius = {
  none: 0,
  xs: 2,
  sm: 4,
  md: 6,
  lg: 8,
  xl: 12,
  '2xl': 16,
  '3xl': 24,
  full: 9999,
} as const;

/**
 * Opacity Tokens
 */
export const opacity = {
  0: 0,
  5: 0.05,
  10: 0.1,
  20: 0.2,
  25: 0.25,
  30: 0.3,
  40: 0.4,
  50: 0.5,
  60: 0.6,
  70: 0.7,
  75: 0.75,
  80: 0.8,
  90: 0.9,
  95: 0.95,
  100: 1,
} as const;

/**
 * Export combined theme
 */
export const theme = {
  colors,
  spacing,
  typography,
  borderRadius,
  opacity,
} as const;

export default theme;
