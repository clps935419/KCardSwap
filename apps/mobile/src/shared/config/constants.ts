/**
 * Application-wide constants
 * 
 * Keep in sync with backend configuration:
 * - apps/backend/app/config.py
 */

/**
 * Search quota limits
 * These should match backend DAILY_SEARCH_LIMIT_FREE setting
 */
export const SEARCH_LIMITS = {
  FREE_USER_DAILY_LIMIT: 5,
  PREMIUM_USER_DAILY_LIMIT: Infinity,
  DEFAULT_RADIUS_KM: 10,
  MIN_RADIUS_KM: 0.1,
  MAX_RADIUS_KM: 100,
} as const;

/**
 * Upload quota limits
 * These should match backend configuration
 */
export const UPLOAD_LIMITS = {
  FREE_USER_DAILY_LIMIT: 2,
  PREMIUM_USER_DAILY_LIMIT: Infinity,
  MAX_FILE_SIZE_MB: 10,
  MAX_FILE_SIZE_BYTES: 10 * 1024 * 1024,
  TOTAL_STORAGE_GB: 1,
  TOTAL_STORAGE_BYTES: 1 * 1024 * 1024 * 1024,
} as const;

/**
 * Location settings
 */
export const LOCATION_SETTINGS = {
  DEFAULT_ACCURACY: 'high' as const,
  TIMEOUT_MS: 10000,
} as const;

/**
 * Cache settings
 */
export const CACHE_SETTINGS = {
  THUMBNAIL_MAX_AGE_DAYS: 30,
} as const;
