/**
 * ProfileHeader Component
 * Reusable profile header showing user info (IG-style)
 */

import React from 'react';
import { Box, Text, Heading } from '@/src/shared/ui/components';
import type { ProfileResponse } from '@/src/shared/api/sdk';

interface ProfileHeaderProps {
  profile: ProfileResponse;
  isOwnProfile?: boolean;
}

export function ProfileHeader({ profile, isOwnProfile = false }: ProfileHeaderProps) {
  return (
    <Box className="items-center py-6 px-4 bg-white border-b border-gray-200">
      {/* Avatar */}
      <Box className="w-24 h-24 rounded-full bg-gray-300 items-center justify-center mb-4">
        <Text size="3xl">
          {profile.avatar_url ? '🖼️' : '👤'}
        </Text>
      </Box>

      {/* Nickname */}
      <Heading size="xl" className="mb-2">
        {profile.nickname || 'Anonymous'}
      </Heading>

      {/* User ID (truncated) */}
      <Text size="sm" className="text-gray-500 mb-3">
        ID: {profile.user_id.substring(0, 8)}...
      </Text>

      {/* Bio */}
      {profile.bio && (
        <Text size="md" className="text-gray-700 text-center px-4 mb-3">
          {profile.bio}
        </Text>
      )}

      {/* Region */}
      {profile.region && (
        <Box className="flex-row items-center mb-2">
          <Text size="sm" className="text-gray-600">
            📍 {profile.region}
          </Text>
        </Box>
      )}

      {/* Stats placeholder for future enhancement */}
      <Box className="flex-row justify-around w-full mt-4 pt-4 border-t border-gray-100">
        <Box className="items-center">
          <Text size="lg" className="font-bold">0</Text>
          <Text size="sm" className="text-gray-600">小卡</Text>
        </Box>
        <Box className="items-center">
          <Text size="lg" className="font-bold">0</Text>
          <Text size="sm" className="text-gray-600">交易</Text>
        </Box>
        <Box className="items-center">
          <Text size="lg" className="font-bold">0</Text>
          <Text size="sm" className="text-gray-600">朋友</Text>
        </Box>
      </Box>
    </Box>
  );
}
