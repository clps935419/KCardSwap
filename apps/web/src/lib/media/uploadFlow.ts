/**
 * Media upload flow helper (T053)
 * 
 * Implements the presign → upload → confirm → attach flow for media uploads.
 * 
 * @module lib/media/uploadFlow
 */

import { axiosInstance } from '@/src/lib/api/axios';

export interface UploadFlowOptions {
  file: File;
  onProgress?: (progress: number) => void;
}

export interface UploadFlowResult {
  mediaId: string;
  uploadUrl: string;
}

/**
 * Execute the complete media upload flow
 * 
 * Flow: presign → upload to GCS → confirm
 * 
 * @param options Upload options
 * @returns Media ID for subsequent attach operations
 * @throws Error if any step fails
 */
export async function executeUploadFlow(
  options: UploadFlowOptions
): Promise<string> {
  const { file, onProgress } = options;

  // Step 1: Get presigned upload URL
  onProgress?.(10);
  
  const presignResponse = await axiosInstance.post('/api/v1/media/upload-url', {
    content_type: file.type,
    file_size_bytes: file.size,
    filename: file.name,
  });

  const { media_id, upload_url } = presignResponse.data;

  // Step 2: Upload file to GCS using presigned URL
  onProgress?.(30);
  
  await uploadToGCS(upload_url, file, (progress) => {
    // Map GCS upload progress (30-80%) to overall progress
    const overallProgress = 30 + Math.floor(progress * 0.5);
    onProgress?.(overallProgress);
  });

  // Step 3: Confirm upload (applies quota)
  onProgress?.(80);
  
  await axiosInstance.post(`/api/v1/media/${media_id}/confirm`);

  onProgress?.(100);

  return media_id;
}

/**
 * Upload file to GCS using presigned URL
 */
async function uploadToGCS(
  uploadUrl: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          onProgress(progress);
        }
      });
    }

    // Handle completion
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`));
      }
    });

    // Handle errors
    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed due to network error'));
    });

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload was aborted'));
    });

    // Execute PUT request to GCS
    xhr.open('PUT', uploadUrl);
    xhr.setRequestHeader('Content-Type', file.type);
    xhr.send(file);
  });
}

/**
 * Attach confirmed media to a post
 * 
 * @param mediaId Media ID (must be confirmed)
 * @param postId Post ID to attach to
 */
export async function attachMediaToPost(
  mediaId: string,
  postId: string
): Promise<void> {
  await axiosInstance.post(`/api/v1/media/posts/${postId}/attach`, {
    media_id: mediaId,
  });
}

/**
 * Attach confirmed media to a gallery card
 * 
 * @param mediaId Media ID (must be confirmed)
 * @param cardId Gallery card ID to attach to
 */
export async function attachMediaToGalleryCard(
  mediaId: string,
  cardId: string
): Promise<void> {
  await axiosInstance.post(`/api/v1/media/gallery/cards/${cardId}/attach`, {
    media_id: mediaId,
  });
}
