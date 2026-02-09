/**
 * UserAvatar Component
 *
 * Displays user avatar with fallback to initial
 */

import { cn } from '@/lib/utils'

interface UserAvatarProps {
  nickname?: string | null
  avatarUrl?: string | null
  userId?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
}

export function UserAvatar({ nickname, avatarUrl, userId, size = 'md', className }: UserAvatarProps) {
  // Get first character for fallback
  const fallbackChar = nickname?.charAt(0).toUpperCase() || userId?.charAt(0).toUpperCase() || '?'

  return (
    <div
      className={cn(
        'rounded-full bg-primary-50 text-primary-500 flex items-center justify-center font-black overflow-hidden',
        sizeClasses[size],
        className
      )}
    >
      {avatarUrl ? (
        <img src={avatarUrl} alt={nickname || 'User'} className="w-full h-full object-cover" />
      ) : (
        <span>{fallbackChar}</span>
      )}
    </div>
  )
}
