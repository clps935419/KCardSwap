'use client'

import { Heart } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface LikeButtonProps {
  liked: boolean
  likeCount: number
  onToggle: () => void
  disabled?: boolean
}

export function LikeButton({
  liked,
  likeCount,
  onToggle,
  disabled = false,
}: LikeButtonProps) {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onToggle}
      disabled={disabled}
      className={cn(
        'flex items-center gap-1',
        liked && 'text-red-500 hover:text-red-600'
      )}
    >
      <Heart
        className={cn(
          'h-4 w-4',
          liked && 'fill-current'
        )}
      />
      <span className="text-sm">{likeCount}</span>
    </Button>
  )
}
