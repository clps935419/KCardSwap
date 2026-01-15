/**
 * Shared Form Validation Schemas using Zod
 * 
 * 集中管理表單驗證規則
 */

import { z } from 'zod';

/**
 * Profile Form Schema
 */
export const profileFormSchema = z.object({
  nickname: z
    .string()
    .min(1, '暱稱不能為空')
    .max(50, '暱稱不能超過 50 個字元')
    .refine((val) => val.trim().length > 0, '暱稱不能只有空格'),
  bio: z
    .string()
    .max(500, 'Bio 不能超過 500 個字元')
    .optional()
    .or(z.literal('')),
  nearbyVisible: z.boolean(),
  showOnline: z.boolean(),
  allowStrangerChat: z.boolean(),
});

export type ProfileFormData = z.infer<typeof profileFormSchema>;

/**
 * Card Upload Form Schema
 */
export const cardUploadFormSchema = z.object({
  idol: z.string().optional().or(z.literal('')),
  idolGroup: z.string().optional().or(z.literal('')),
  album: z.string().optional().or(z.literal('')),
  version: z.string().optional().or(z.literal('')),
  rarity: z.enum(['common', 'rare', 'epic', 'legendary']),
});

export type CardUploadFormData = z.infer<typeof cardUploadFormSchema>;

/**
 * Create Post Form Schema
 */
export const createPostFormSchema = z.object({
  cityCode: z.string().min(1, '請選擇城市'),
  title: z
    .string()
    .min(1, '請輸入標題')
    .max(120, '標題不能超過 120 字元')
    .refine((val) => val.trim().length > 0, '標題不能只有空格'),
  content: z
    .string()
    .min(1, '請輸入內容')
    .refine((val) => val.trim().length > 0, '內容不能只有空格'),
  idol: z.string().optional().or(z.literal('')),
  idolGroup: z.string().optional().or(z.literal('')),
});

export type CreatePostFormData = z.infer<typeof createPostFormSchema>;
