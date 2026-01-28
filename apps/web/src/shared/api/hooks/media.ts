/**
 * Media API Hooks
 *
 * SDK-based methods for media operations.
 */

import type { CreateUploadUrlApiV1MediaUploadUrlPostData } from '../generated'
import { MediaService } from '../generated'
import { getAxiosClient } from '../sdk-config'

/**
 * Get presigned upload URL for media
 */
export async function createUploadUrl(
  data: CreateUploadUrlApiV1MediaUploadUrlPostData['requestBody']
) {
  getAxiosClient()
  const response = await MediaService.createUploadUrlApiV1MediaUploadUrlPost({
    requestBody: data,
  })
  return response
}

/**
 * Confirm media upload (applies quota)
 */
export async function confirmUpload(mediaId: string) {
  getAxiosClient()
  const response = await MediaService.confirmUploadApiV1MediaMediaIdConfirmPost({
    mediaId,
  })
  return response
}

/**
 * Attach confirmed media to a post
 */
export async function attachMediaToPost(postId: string, mediaId: string) {
  getAxiosClient()
  const response = await MediaService.attachMediaToPostApiV1MediaPostsPostIdAttachPost({
    postId,
    requestBody: {
      media_id: mediaId,
    },
  })
  return response
}

/**
 * Attach confirmed media to a gallery card
 */
export async function attachMediaToGalleryCard(cardId: string, mediaId: string) {
  getAxiosClient()
  const response =
    await MediaService.attachMediaToGalleryCardApiV1MediaGalleryCardsCardIdAttachPost({
      cardId,
      requestBody: {
        media_id: mediaId,
      },
    })
  return response
}
