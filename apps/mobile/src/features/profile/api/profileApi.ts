/**
 * Profile API Service (M103)
 * 
 * API calls for profile management:
 * - GET /profile/me - Get current user's profile
 * - PUT /profile/me - Update current user's profile
 */

import { apiClient } from '../../../shared/api/client';

/**
 * Profile data structure matching backend contract
 */
export interface Profile {
  id: string;
  user_id: string;
  nickname: string | null;
  avatar_url: string | null;
  bio: string | null;
  region: string | null;
  preferences: Record<string, any>;
  privacy_flags: {
    nearby_visible: boolean;
    show_online: boolean;
    allow_stranger_chat: boolean;
  };
  created_at: string;
  updated_at: string;
}

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
 * API response wrapper
 */
interface ApiResponse<T> {
  data: T | null;
  error: {
    code: string;
    message: string;
  } | null;
}

/**
 * Get current user's profile
 * 
 * @returns Promise<Profile>
 * @throws Error if request fails
 */
export async function getMyProfile(): Promise<Profile> {
  try {
    const response = await apiClient.get<ApiResponse<Profile>>('/profile/me');

    if (!response.data || !response.data.data) {
      throw new Error('Invalid response from server');
    }

    if (response.data.error) {
      throw new Error(response.data.error.message);
    }

    return response.data.data;
  } catch (error: any) {
    console.error('Get profile error:', error);

    if (error.response?.status === 404) {
      throw new Error('Profile not found');
    } else if (error.response?.status === 401) {
      throw new Error('Please login again');
    }

    throw new Error(error.message || 'Failed to load profile');
  }
}

/**
 * Update current user's profile
 * 
 * @param updates - Partial profile data to update
 * @returns Promise<Profile> - Updated profile
 * @throws Error if request fails
 */
export async function updateMyProfile(updates: ProfileUpdateRequest): Promise<Profile> {
  try {
    console.log('Updating profile with:', updates);

    const response = await apiClient.put<ApiResponse<Profile>>('/profile/me', updates);

    if (!response.data || !response.data.data) {
      throw new Error('Invalid response from server');
    }

    if (response.data.error) {
      throw new Error(response.data.error.message);
    }

    return response.data.data;
  } catch (error: any) {
    console.error('Update profile error:', error);

    if (error.response?.status === 400 || error.response?.status === 422) {
      // Validation error
      const errorDetail = error.response?.data?.detail;
      if (errorDetail && typeof errorDetail === 'object') {
        // Extract validation errors
        const messages = errorDetail.map((err: any) => err.msg || err.message).join(', ');
        throw new Error(`Validation error: ${messages}`);
      }
      throw new Error('Invalid profile data');
    } else if (error.response?.status === 401) {
      throw new Error('Please login again');
    }

    throw new Error(error.message || 'Failed to update profile');
  }
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
