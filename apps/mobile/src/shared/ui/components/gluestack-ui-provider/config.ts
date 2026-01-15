'use client';
import { vars } from 'nativewind';

export const config = {
  light: vars({
    /* Primary - Soft Lavender (Korean aesthetic) */
    '--color-primary-0': '252 248 255',      // Very light lavender
    '--color-primary-50': '245 239 254',     // Ultra soft lavender
    '--color-primary-100': '237 229 252',    // Light lavender
    '--color-primary-200': '220 208 247',    // Soft lavender
    '--color-primary-300': '201 185 240',    // Medium lavender
    '--color-primary-400': '185 164 228',    // Floral lavender (#B984DF area)
    '--color-primary-500': '169 142 216',    // Main lavender
    '--color-primary-600': '149 119 193',    // Deep lavender
    '--color-primary-700': '128 95 169',     // Darker lavender
    '--color-primary-800': '102 76 135',     // Very dark lavender
    '--color-primary-900': '76 57 101',      // Deepest lavender
    '--color-primary-950': '51 38 68',       // Almost black lavender

    /* Secondary - Blush Pink (Korean aesthetic) */
    '--color-secondary-0': '255 251 252',    // Almost white pink
    '--color-secondary-50': '255 247 249',   // Very light pink
    '--color-secondary-100': '255 237 242',  // Light blush (#FCEDF2 area)
    '--color-secondary-200': '255 220 230',  // Soft blush
    '--color-secondary-300': '255 197 213',  // Cherry blossom (#FFB7C5 area)
    '--color-secondary-400': '254 181 202',  // Medium blush
    '--color-secondary-500': '254 197 229',  // Blush pink (#FEC5E5 area)
    '--color-secondary-600': '255 156 184',  // Deep blush
    '--color-secondary-700': '240 131 161',  // Darker pink
    '--color-secondary-800': '214 106 136',  // Very dark pink
    '--color-secondary-900': '171 85 109',   // Deepest pink
    '--color-secondary-950': '114 57 73',    // Almost black pink

    /* Tertiary - Soft Mint (Korean aesthetic) */
    '--color-tertiary-0': '247 254 252',     // Almost white mint
    '--color-tertiary-50': '236 252 247',    // Very light mint
    '--color-tertiary-100': '224 249 241',   // Light mint (#E4F1CB area)
    '--color-tertiary-200': '201 241 228',   // Soft mint
    '--color-tertiary-300': '184 228 220',   // Dreamy mint (#B8E4DC area)
    '--color-tertiary-400': '156 217 204',   // Medium mint
    '--color-tertiary-500': '140 207 193',   // Main mint
    '--color-tertiary-600': '115 186 172',   // Deep mint
    '--color-tertiary-700': '92 158 146',    // Darker mint
    '--color-tertiary-800': '74 131 121',    // Very dark mint
    '--color-tertiary-900': '56 99 92',      // Deepest mint
    '--color-tertiary-950': '37 66 61',      // Almost black mint

    /* Error - Soft Coral (gentle error) */
    '--color-error-0': '255 246 245',
    '--color-error-50': '255 237 235',
    '--color-error-100': '255 220 215',
    '--color-error-200': '255 194 186',
    '--color-error-300': '255 162 149',
    '--color-error-400': '251 134 119',
    '--color-error-500': '242 106 91',
    '--color-error-600': '224 84 73',
    '--color-error-700': '197 66 58',
    '--color-error-800': '165 54 48',
    '--color-error-900': '128 45 41',
    '--color-error-950': '85 30 27',

    /* Success - Soft Sage Green (gentle success) */
    '--color-success-0': '244 251 246',
    '--color-success-50': '233 247 237',
    '--color-success-100': '214 240 221',
    '--color-success-200': '186 229 198',
    '--color-success-300': '149 213 168',
    '--color-success-400': '116 196 141',
    '--color-success-500': '92 184 121',
    '--color-success-600': '72 161 102',
    '--color-success-700': '57 135 84',
    '--color-success-800': '46 109 69',
    '--color-success-900': '38 86 56',
    '--color-success-950': '25 57 37',

    /* Warning - Soft Peach (gentle warning) */
    '--color-warning-0': '255 251 247',
    '--color-warning-50': '255 246 237',
    '--color-warning-100': '255 238 222',
    '--color-warning-200': '255 221 189',
    '--color-warning-300': '255 199 149',
    '--color-warning-400': '255 176 112',
    '--color-warning-500': '255 158 88',
    '--color-warning-600': '242 135 63',
    '--color-warning-700': '217 112 44',
    '--color-warning-800': '179 91 36',
    '--color-warning-900': '140 72 30',
    '--color-warning-950': '92 47 20',

    /* Info - Soft Sky Blue (gentle info) */
    '--color-info-0': '245 251 255',
    '--color-info-50': '235 247 255',
    '--color-info-100': '220 241 255',
    '--color-info-200': '194 231 255',
    '--color-info-300': '156 217 252',
    '--color-info-400': '115 200 246',
    '--color-info-500': '82 186 240',
    '--color-info-600': '56 167 225',
    '--color-info-700': '41 141 196',
    '--color-info-800': '35 116 161',
    '--color-info-900': '33 92 126',
    '--color-info-950': '22 61 84',

    /* Typography - Soft grays for Korean minimalist aesthetic */
    '--color-typography-0': '255 253 250',    // Warm white
    '--color-typography-50': '250 248 245',   // Very soft beige
    '--color-typography-100': '242 240 237',  // Light beige
    '--color-typography-200': '224 221 218',  // Soft gray-beige
    '--color-typography-300': '199 196 193',  // Medium gray
    '--color-typography-400': '168 165 162',  // Medium-dark gray
    '--color-typography-500': '133 130 127',  // Balanced gray
    '--color-typography-600': '102 99 96',    // Dark gray
    '--color-typography-700': '77 74 71',     // Darker gray
    '--color-typography-800': '56 53 50',     // Very dark gray
    '--color-typography-900': '38 35 32',     // Almost black
    '--color-typography-950': '23 20 17',     // Black

    /* Outline - Soft borders for cards and inputs */
    '--color-outline-0': '255 253 250',       // Warm white
    '--color-outline-50': '248 245 242',      // Very light
    '--color-outline-100': '240 237 234',     // Light outline
    '--color-outline-200': '230 227 224',     // Soft outline
    '--color-outline-300': '215 212 209',     // Medium outline
    '--color-outline-400': '190 187 184',     // Medium-dark outline
    '--color-outline-500': '165 162 159',     // Balanced outline
    '--color-outline-600': '135 132 129',     // Dark outline
    '--color-outline-700': '105 102 99',      // Darker outline
    '--color-outline-800': '75 72 69',        // Very dark outline
    '--color-outline-900': '50 47 44',        // Almost black outline
    '--color-outline-950': '30 27 24',        // Black outline

    /* Background - Warm neutrals inspired by Korean minimalism */
    '--color-background-0': '255 255 255',    // Pure white
    '--color-background-50': '252 251 249',   // Creamy white (#FCFEDB area)
    '--color-background-100': '248 246 244',  // Very light cream
    '--color-background-200': '242 240 238',  // Light cream
    '--color-background-300': '232 230 228',  // Soft beige
    '--color-background-400': '210 208 206',  // Medium beige
    '--color-background-500': '180 178 176',  // Balanced beige-gray
    '--color-background-600': '145 143 141',  // Medium-dark gray
    '--color-background-700': '110 108 106',  // Dark gray
    '--color-background-800': '75 73 71',     // Very dark gray
    '--color-background-900': '45 43 41',     // Almost black
    '--color-background-950': '25 23 21',     // Black

    /* Background Special - Tinted backgrounds for states */
    '--color-background-error': '255 244 246',      // Very soft coral tint
    '--color-background-warning': '255 249 244',    // Very soft peach tint
    '--color-background-success': '245 252 248',    // Very soft sage tint
    '--color-background-muted': '250 248 246',      // Warm muted background
    '--color-background-info': '245 250 255',       // Very soft sky tint

    /* Focus Ring Indicator - Korean aesthetic accents */
    '--color-indicator-primary': '169 142 216',     // Lavender
    '--color-indicator-info': '82 186 240',         // Sky blue
    '--color-indicator-error': '242 106 91',        // Soft coral
  }),
  dark: vars({
    '--color-primary-0': '166 166 166',
    '--color-primary-50': '175 175 175',
    '--color-primary-100': '186 186 186',
    '--color-primary-200': '197 197 197',
    '--color-primary-300': '212 212 212',
    '--color-primary-400': '221 221 221',
    '--color-primary-500': '230 230 230',
    '--color-primary-600': '240 240 240',
    '--color-primary-700': '250 250 250',
    '--color-primary-800': '253 253 253',
    '--color-primary-900': '254 249 249',
    '--color-primary-950': '253 252 252',

    /* Secondary  */
    '--color-secondary-0': '20 20 20',
    '--color-secondary-50': '23 23 23',
    '--color-secondary-100': '31 31 31',
    '--color-secondary-200': '39 39 39',
    '--color-secondary-300': '44 44 44',
    '--color-secondary-400': '56 57 57',
    '--color-secondary-500': '63 64 64',
    '--color-secondary-600': '86 86 86',
    '--color-secondary-700': '110 110 110',
    '--color-secondary-800': '135 135 135',
    '--color-secondary-900': '150 150 150',
    '--color-secondary-950': '164 164 164',

    /* Tertiary */
    '--color-tertiary-0': '84 49 18',
    '--color-tertiary-50': '108 61 19',
    '--color-tertiary-100': '130 73 23',
    '--color-tertiary-200': '180 98 26',
    '--color-tertiary-300': '215 117 31',
    '--color-tertiary-400': '231 129 40',
    '--color-tertiary-500': '251 157 75',
    '--color-tertiary-600': '253 180 116',
    '--color-tertiary-700': '254 209 170',
    '--color-tertiary-800': '255 233 213',
    '--color-tertiary-900': '255 242 229',
    '--color-tertiary-950': '255 250 245',

    /* Error */
    '--color-error-0': '83 19 19',
    '--color-error-50': '127 29 29',
    '--color-error-100': '153 27 27',
    '--color-error-200': '185 28 28',
    '--color-error-300': '220 38 38',
    '--color-error-400': '230 53 53',
    '--color-error-500': '239 68 68',
    '--color-error-600': '249 97 96',
    '--color-error-700': '229 91 90',
    '--color-error-800': '254 202 202',
    '--color-error-900': '254 226 226',
    '--color-error-950': '254 233 233',

    /* Success */
    '--color-success-0': '27 50 36',
    '--color-success-50': '20 83 45',
    '--color-success-100': '22 101 52',
    '--color-success-200': '32 111 62',
    '--color-success-300': '42 121 72',
    '--color-success-400': '52 131 82',
    '--color-success-500': '72 151 102',
    '--color-success-600': '102 181 132',
    '--color-success-700': '132 211 162',
    '--color-success-800': '162 241 192',
    '--color-success-900': '202 255 232',
    '--color-success-950': '228 255 244',

    /* Warning */
    '--color-warning-0': '84 45 18',
    '--color-warning-50': '108 56 19',
    '--color-warning-100': '130 68 23',
    '--color-warning-200': '180 90 26',
    '--color-warning-300': '215 108 31',
    '--color-warning-400': '231 120 40',
    '--color-warning-500': '251 149 75',
    '--color-warning-600': '253 173 116',
    '--color-warning-700': '254 205 170',
    '--color-warning-800': '255 231 213',
    '--color-warning-900': '255 244 237',
    '--color-warning-950': '255 249 245',

    /* Info */
    '--color-info-0': '3 38 56',
    '--color-info-50': '5 64 93',
    '--color-info-100': '7 90 131',
    '--color-info-200': '9 115 168',
    '--color-info-300': '11 141 205',
    '--color-info-400': '13 166 242',
    '--color-info-500': '50 180 244',
    '--color-info-600': '87 194 246',
    '--color-info-700': '124 207 248',
    '--color-info-800': '162 221 250',
    '--color-info-900': '199 235 252',
    '--color-info-950': '236 248 254',

    /* Typography */
    '--color-typography-0': '23 23 23',
    '--color-typography-50': '38 38 39',
    '--color-typography-100': '64 64 64',
    '--color-typography-200': '82 82 82',
    '--color-typography-300': '115 115 115',
    '--color-typography-400': '140 140 140',
    '--color-typography-500': '163 163 163',
    '--color-typography-600': '212 212 212',
    '--color-typography-700': '219 219 220',
    '--color-typography-800': '229 229 229',
    '--color-typography-900': '245 245 245',
    '--color-typography-950': '254 254 255',

    /* Outline */
    '--color-outline-0': '26 23 23',
    '--color-outline-50': '39 38 36',
    '--color-outline-100': '65 65 65',
    '--color-outline-200': '83 82 82',
    '--color-outline-300': '115 116 116',
    '--color-outline-400': '140 141 141',
    '--color-outline-500': '165 163 163',
    '--color-outline-600': '211 211 211',
    '--color-outline-700': '221 220 219',
    '--color-outline-800': '230 230 230',
    '--color-outline-900': '243 243 243',
    '--color-outline-950': '253 254 254',

    /* Background */
    '--color-background-0': '18 18 18',
    '--color-background-50': '39 38 37',
    '--color-background-100': '65 64 64',
    '--color-background-200': '83 82 82',
    '--color-background-300': '116 116 116',
    '--color-background-400': '142 142 142',
    '--color-background-500': '162 163 163',
    '--color-background-600': '213 212 212',
    '--color-background-700': '229 228 228',
    '--color-background-800': '242 241 241',
    '--color-background-900': '246 246 246',
    '--color-background-950': '255 255 255',

    /* Background Special */
    '--color-background-error': '66 43 43',
    '--color-background-warning': '65 47 35',
    '--color-background-success': '28 43 33',
    '--color-background-muted': '51 51 51',
    '--color-background-info': '26 40 46',

    /* Focus Ring Indicator  */
    '--color-indicator-primary': '247 247 247',
    '--color-indicator-info': '161 199 245',
    '--color-indicator-error': '232 70 69',
  }),
};
