import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Truncate user ID to first 8 characters for display
 * @param userId - The full user ID (UUID)
 * @returns Truncated user ID with ellipsis
 */
export function truncateUserId(userId: string): string {
  return `${userId.substring(0, 8)}...`
}
