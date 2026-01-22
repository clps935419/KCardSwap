/**
 * Idol Groups Constants
 * 偶像團體常數列表
 * 
 * 用於 Onboarding 和其他需要偶像團體選項的地方
 */

export interface IdolGroup {
  id: string;
  name: string;
  emoji: string;
}

/**
 * 預設的 K-pop 偶像團體列表
 * 根據 UI 原型中的團體
 */
export const DEFAULT_IDOL_GROUPS: IdolGroup[] = [
  { id: 'newjeans', name: 'NewJeans', emoji: '👖' },
  { id: 'ive', name: 'IVE', emoji: '🦢' },
  { id: 'aespa', name: 'aespa', emoji: '🦋' },
  { id: 'le-sserafim', name: 'LE SSERAFIM', emoji: '🌸' },
  { id: 'blackpink', name: 'BLACKPINK', emoji: '💖' },
  { id: 'twice', name: 'TWICE', emoji: '🍭' },
  { id: 'seventeen', name: 'SEVENTEEN', emoji: '💎' },
  { id: 'bts', name: 'BTS', emoji: '💜' },
  { id: 'stray-kids', name: 'Stray Kids', emoji: '🐺' },
  { id: 'enhypen', name: 'ENHYPEN', emoji: '🔥' },
  { id: 'txt', name: 'TXT', emoji: '⭐' },
  { id: 'itzy', name: 'ITZY', emoji: '✨' },
];
