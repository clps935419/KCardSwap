import { Card, CardContent } from '@/components/ui/card'
import { UserAvatar } from '@/components/ui/user-avatar'
import type { ProfileResponse } from '@/shared/api/generated/types.gen'

interface ProfileHeaderProps {
  profile: ProfileResponse
}

export function ProfileHeader({ profile }: ProfileHeaderProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex flex-col items-center space-y-4">
          {/* Avatar */}
          <UserAvatar
            src={profile.avatar_url || undefined}
            alt={profile.nickname || 'User'}
            className="h-24 w-24"
          />

          {/* Nickname */}
          <div className="text-center space-y-1">
            <h2 className="text-2xl font-bold">{profile.nickname || 'Anonymous'}</h2>
            <p className="text-sm text-muted-foreground">
              ID: {profile.user_id.substring(0, 8)}...
            </p>
          </div>

          {/* Bio */}
          {profile.bio && (
            <p className="text-center text-muted-foreground max-w-md px-4">{profile.bio}</p>
          )}

          {/* Region */}
          {profile.region && (
            <div className="flex items-center text-sm text-muted-foreground">
              <span className="mr-1">📍</span>
              <span>{profile.region}</span>
            </div>
          )}

          {/* Stats - placeholder for future implementation */}
          <div className="flex justify-around w-full max-w-md pt-4 border-t">
            <div className="text-center">
              <div className="text-2xl font-bold">0</div>
              <div className="text-xs text-muted-foreground">小卡</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">0</div>
              <div className="text-xs text-muted-foreground">交易</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">0</div>
              <div className="text-xs text-muted-foreground">朋友</div>
            </div>
          </div>
          {/*
            TODO: Replace hardcoded values with actual data:
            - 小卡 count: Get from gallery cards total
            - 交易 count: Implement trade count API endpoint
            - 朋友 count: Implement friends count API endpoint
          */}
        </div>
      </CardContent>
    </Card>
  )
}
