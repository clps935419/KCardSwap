/**
 * Media API Hooks
 *
 * SDK-based methods for media operations.
 */

'use client'

import { useMutation } from '@tanstack/react-query'

import type { CreateUploadUrlRequestSchema } from '../generated'
import {
  attachMediaToGalleryCardApiV1MediaGalleryCardsCardIdAttachPost,
  attachMediaToPostApiV1MediaPostsPostIdAttachPost,
  confirmUploadApiV1MediaMediaIdConfirmPost,
  createUploadUrlApiV1MediaUploadUrlPost,
} from '../generated'

/**
 * Get presigned upload URL for media
 */
export async function createUploadUrl(data: CreateUploadUrlRequestSchema) {
  const response = await createUploadUrlApiV1MediaUploadUrlPost({
    body: data,
    throwOnError: true,
  })
  return response.data
}

/**
 * Confirm media upload (applies quota)
 */
export async function confirmUpload(mediaId: string) {
  const response = await confirmUploadApiV1MediaMediaIdConfirmPost({
    path: {
      media_id: mediaId,
    },
    throwOnError: true,
  })
  return response.data
}

export interface AttachMediaToPostInput {
  postId: string
  mediaId: string
}

export interface AttachMediaToGalleryCardInput {
  cardId: string
  mediaId: string
}

export interface UploadFlowOptions {
  file: File
  onProgress?: (progress: number) => void
}

export async function runUploadFlow(options: UploadFlowOptions): Promise<string> {
  const { file, onProgress } = options

  onProgress?.(10)

  const presignResponse = await createUploadUrl({
    content_type: file.type,
    file_size_bytes: file.size,
    filename: file.name,
  })

  const { media_id, upload_url } = presignResponse

  onProgress?.(30)

  await uploadToGcs(upload_url, file, progress => {
    const overallProgress = 30 + Math.floor(progress * 0.5)
    onProgress?.(overallProgress)
  })

  onProgress?.(80)

  await confirmUpload(media_id)

  onProgress?.(100)

  return media_id
}

/**
 * Upload flow mutation: presign -> upload -> confirm.
 */
export function useUploadFlowMutation() {
  return useMutation({
    mutationFn: runUploadFlow,
  })
}

/**
 * Attach confirmed media to a post
 */
export function useAttachMediaToPostMutation() {
  return useMutation({
    mutationFn: async ({ postId, mediaId }: AttachMediaToPostInput) => {
      return attachMediaToPost(postId, mediaId)
    },
  })
}

/**
 * Attach confirmed media to a gallery card
 */
export function useAttachMediaToGalleryCardMutation() {
  return useMutation({
    mutationFn: async ({ cardId, mediaId }: AttachMediaToGalleryCardInput) => {
      return attachMediaToGalleryCard(cardId, mediaId)
    },
  })
}

export async function attachMediaToPost(postId: string, mediaId: string) {
  const response = await attachMediaToPostApiV1MediaPostsPostIdAttachPost({
    path: {
      post_id: postId,
    },
    body: {
      media_id: mediaId,
    },
    throwOnError: true,
  })
  return response.data
}

export async function attachMediaToGalleryCard(cardId: string, mediaId: string) {
  const response = await attachMediaToGalleryCardApiV1MediaGalleryCardsCardIdAttachPost({
    path: {
      card_id: cardId,
    },
    body: {
      media_id: mediaId,
    },
    throwOnError: true,
  })
  return response.data
}

async function uploadToGcs(
  uploadUrl: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    if (onProgress) {
      xhr.upload.addEventListener('progress', event => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100
          onProgress(progress)
        }
      })
    }

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve()
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`))
      }
    })

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed due to network error'))
    })

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload was aborted'))
    })

    xhr.open('PUT', uploadUrl)
    xhr.setRequestHeader('Content-Type', file.type)
    xhr.send(file)
  })
}
