/**
 * Theme Tokens
 * 
 * Centralized theme configuration extracted from Gluestack UI provider.
 * These tokens define the design system's colors, spacing, typography, etc.
 * 
 * @see components/ui/gluestack-ui-provider/config.ts for full configuration
 */

/**
 * Color Tokens
 * 
 * RGB format: 'R G B' (space-separated values)
 * Usage in Tailwind: text-[rgb(var(--color-primary-500))]
 */
export const colors = {
  primary: {
    0: '179 179 179',
    50: '153 153 153',
    100: '128 128 128',
    200: '115 115 115',
    300: '102 102 102',
    400: '82 82 82',
    500: '51 51 51',
    600: '41 41 41',
    700: '31 31 31',
    800: '13 13 13',
    900: '10 10 10',
    950: '8 8 8',
  },
  secondary: {
    0: '253 253 253',
    50: '251 251 251',
    100: '246 246 246',
    200: '242 242 242',
    300: '237 237 237',
    400: '230 230 231',
    500: '217 217 219',
    600: '198 199 199',
    700: '189 189 189',
    800: '177 177 177',
    900: '165 164 164',
    950: '157 157 157',
  },
  tertiary: {
    0: '255 250 245',
    50: '255 242 229',
    100: '255 233 213',
    200: '254 209 170',
    300: '253 180 116',
    400: '251 157 75',
    500: '231 129 40',
    600: '215 117 31',
    700: '180 98 26',
    800: '130 73 23',
    900: '108 61 19',
    950: '84 49 18',
  },
  error: {
    0: '254 233 233',
    50: '254 226 226',
    100: '254 202 202',
    200: '252 165 165',
    300: '248 113 113',
    400: '239 68 68',
    500: '220 38 38',
    600: '185 28 28',
    700: '153 27 27',
    800: '127 29 29',
    900: '69 10 10',
    950: '69 10 10',
  },
  success: {
    0: '220 252 231',
    50: '187 247 208',
    100: '134 239 172',
    200: '74 222 128',
    300: '34 197 94',
    400: '22 163 74',
    500: '21 128 61',
    600: '22 101 52',
    700: '20 83 45',
    800: '19 56 35',
    900: '5 46 22',
    950: '5 46 22',
  },
  warning: {
    0: '254 252 232',
    50: '254 249 195',
    100: '254 240 138',
    200: '253 224 71',
    300: '250 204 21',
    400: '234 179 8',
    500: '202 138 4',
    600: '161 98 7',
    700: '133 77 14',
    800: '113 63 18',
    900: '66 32 6',
    950: '66 32 6',
  },
  info: {
    0: '224 242 254',
    50: '186 230 253',
    100: '125 211 252',
    200: '56 189 248',
    300: '14 165 233',
    400: '2 132 199',
    500: '3 105 161',
    600: '7 89 133',
    700: '12 74 110',
    800: '30 58 138',
    900: '23 37 84',
    950: '23 37 84',
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
