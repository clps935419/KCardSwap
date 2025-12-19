/**
 * Profile API Service (M103)
 * 
 * Uses hey-api generated TanStack Query options/mutations for profile operations.
 * This file re-exports SDK functions and provides helper utilities.
 * 
 * **Standard Usage**:
 * ```typescript
 * import { useQuery, useMutation } from '@tanstack/react-query';
 * import { getMyProfileOptions, updateMyProfileMutation } from './profileApi';
 * 
 * function ProfileScreen() {
 *   const { data, isLoading } = useQuery(getMyProfileOptions());
 *   const updateProfile = useMutation(updateMyProfileMutation());
 *   
 *   const handleUpdate = async () => {
 *     await updateProfile.mutateAsync({ body: { nickname: 'New Name' } });
 *   };
 * }
 * ```
 */

import type {
  GetMyProfileResponse,
  UpdateMyProfileData,
  UpdateMyProfileResponse,
} from '@/src/shared/api/sdk';

// Re-export SDK TanStack Query options and mutations
export {
  getMyProfileOptions,
  getMyProfileQueryKey,
  updateMyProfileMutation,
} from '@/src/shared/api/sdk';

// Re-export types for convenience
export type { GetMyProfileResponse, UpdateMyProfileData, UpdateMyProfileResponse };

/**
 * Profile data structure (extracted from response type)
 */
export type Profile = NonNullable<GetMyProfileResponse['data']>;

/**
 * Profile update request (all fields optional)
 */
export interface ProfileUpdateRequest {
  nickname?: string;
  bio?: string;
  avatar_url?: string;
  region?: string;
  preferences?: Record<string, any>;
  privacy_flags?: {
    nearby_visible?: boolean;
    show_online?: boolean;
    allow_stranger_chat?: boolean;
  };
}

/**
 * Validate nickname (frontend validation)
 */
export function validateNickname(nickname: string): string | null {
  if (!nickname || nickname.trim().length === 0) {
    return 'Nickname cannot be empty';
  }
  
  if (nickname.length > 50) {
    return 'Nickname must be less than 50 characters';
  }

  return null;
}

/**
 * Validate bio (frontend validation)
 */
export function validateBio(bio: string): string | null {
  if (bio.length > 500) {
    return 'Bio must be less than 500 characters';
  }

  return null;
}

/**
 * Example usage in a component:
 * 
 * ```typescript
 * import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
 * import { 
 *   getMyProfileOptions,
 *   getMyProfileQueryKey, 
 *   updateMyProfileMutation,
 *   validateNickname 
 * } from './profileApi';
 * 
 * function EditProfileScreen() {
 *   const queryClient = useQueryClient();
 *   const { data, isLoading } = useQuery(getMyProfileOptions());
 *   const updateProfile = useMutation({
 *     ...updateMyProfileMutation(),
 *     onSuccess: () => {
 *       // Invalidate profile query to refetch
 *       queryClient.invalidateQueries({ queryKey: getMyProfileQueryKey() });
 *     },
 *   });
 *   
 *   const handleSubmit = async (nickname: string, bio: string) => {
 *     const nicknameError = validateNickname(nickname);
 *     if (nicknameError) {
 *       alert(nicknameError);
 *       return;
 *     }
 *     
 *     await updateProfile.mutateAsync({
 *       body: { nickname, bio },
 *     });
 *   };
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   const profile = data?.data;
 *   return <EditForm initialValues={profile} onSubmit={handleSubmit} />;
 * }
 * ```
 */
