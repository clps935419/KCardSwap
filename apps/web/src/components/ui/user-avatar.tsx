/**
 * UserAvatar Component
 *
 * Displays user avatar with fallback to initial
 */

import Image from 'next/image'
import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface UserAvatarProps {
  nickname?: string | null
  avatarUrl?: string | null
  userId?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
  fallback?: ReactNode
}

const sizeClasses = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
}

export function UserAvatar({
  nickname,
  avatarUrl,
  userId,
  size = 'md',
  className,
  fallback,
}: UserAvatarProps) {
  // Get first character for fallback
  const fallbackChar = nickname?.charAt(0).toUpperCase() || userId?.charAt(0).toUpperCase() || '?'
  const fallbackContent = fallback ?? <span>{fallbackChar}</span>
  
  return (
    <div
      className={cn(
        'rounded-full bg-primary-50 text-primary-500 flex items-center justify-center font-black overflow-hidden relative',
        sizeClasses[size],
        className
      )}
    >
      {avatarUrl ? (
        <Image
          src={avatarUrl}
          alt={nickname || 'User'}
          fill
          className="object-cover"
          sizes="40px"
          unoptimized
        />
      ) : (
        fallbackContent
      )}
    </div>
  )
}
