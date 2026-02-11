import imageCompression from 'browser-image-compression'

const MAX_UPLOAD_BYTES_FREE = 2 * 1024 * 1024
const MAX_IMAGE_DIMENSION = 1600
const INITIAL_QUALITY = 0.85
const MAX_ITERATION = 10

const formatSizeMb = (bytes: number) => (bytes / (1024 * 1024)).toFixed(1)

const replaceFileExtension = (filename: string, extension: string) => {
  const trimmedExtension = extension.startsWith('.') ? extension : `.${extension}`
  const lastDotIndex = filename.lastIndexOf('.')
  if (lastDotIndex === -1) {
    return `${filename}${trimmedExtension}`
  }
  return `${filename.slice(0, lastDotIndex)}${trimmedExtension}`
}

const ensureFile = (blob: Blob, filename: string) =>
  blob instanceof File ? blob : new File([blob], filename, { type: blob.type || 'image/jpeg' })

export async function prepareUploadFile(file: File, maxBytes = MAX_UPLOAD_BYTES_FREE): Promise<File> {
  if (file.size <= maxBytes) {
    return file
  }

  const targetName = replaceFileExtension(file.name || 'upload', 'jpg')
  const maxSizeMb = maxBytes / (1024 * 1024)

  try {
    const compressed = await imageCompression(file, {
      maxSizeMB: maxSizeMb,
      maxWidthOrHeight: MAX_IMAGE_DIMENSION,
      useWebWorker: true,
      maxIteration: MAX_ITERATION,
      fileType: 'image/jpeg',
      initialQuality: INITIAL_QUALITY,
    })

    const outputFile = ensureFile(compressed, targetName)
    if (outputFile.size > maxBytes) {
      throw new Error(`圖片壓縮後仍超過 ${formatSizeMb(maxBytes)}MB，請更換圖片`)
    }

    return outputFile
  } catch (error) {
    const message = error instanceof Error ? error.message : '圖片壓縮失敗，請稍後再試'
    throw new Error(message)
  }
}

export const MAX_UPLOAD_BYTES_FREE_LIMIT = MAX_UPLOAD_BYTES_FREE
