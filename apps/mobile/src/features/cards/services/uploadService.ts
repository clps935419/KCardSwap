/**
 * Upload to Signed URL Service
 * M203: 直接上傳圖片到 GCS Signed URL
 * 
 * 不使用 API client（避免自動注入 Authorization header）
 * 支援錯誤處理與重試
 */

/**
 * 上傳選項
 */
interface UploadOptions {
  uri: string;
  uploadUrl: string;
  method: 'PUT' | 'POST';
  headers: Record<string, string>;
  onProgress?: (progress: number) => void;
}

/**
 * 上傳錯誤
 */
export class UploadError extends Error {
  constructor(
    message: string,
    public readonly statusCode?: number,
    public readonly retryable: boolean = false
  ) {
    super(message);
    this.name = 'UploadError';
  }
}

/**
 * 判斷錯誤是否可重試
 */
function isRetryableError(statusCode: number): boolean {
  // 5xx 伺服器錯誤、408 請求逾時、429 請求過多 - 可重試
  return statusCode >= 500 || statusCode === 408 || statusCode === 429;
}

/**
 * 延遲函數（用於重試）
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 讀取圖片為 Blob
 * React Native 環境下需要使用 fetch 讀取本機檔案
 */
async function uriToBlob(uri: string): Promise<Blob> {
  const response = await fetch(uri);
  if (!response.ok) {
    throw new Error(`無法讀取圖片：${response.statusText}`);
  }
  return await response.blob();
}

/**
 * 上傳圖片到 Signed URL
 * M203: 核心上傳邏輯
 */
export async function uploadToSignedUrl(options: UploadOptions): Promise<void> {
  const { uri, uploadUrl, method, headers, onProgress } = options;

  try {
    // 讀取圖片
    const blob = await uriToBlob(uri);

    // 使用 XMLHttpRequest 以支援進度追蹤
    return new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // 進度監聽
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100;
            onProgress(progress);
          }
        });
      }

      // 完成監聽
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve();
        } else {
          const retryable = isRetryableError(xhr.status);
          reject(
            new UploadError(
              `上傳失敗：HTTP ${xhr.status} ${xhr.statusText}`,
              xhr.status,
              retryable
            )
          );
        }
      });

      // 錯誤監聽
      xhr.addEventListener('error', () => {
        reject(new UploadError('網路錯誤，請檢查網路連線', undefined, true));
      });

      // 逾時監聽
      xhr.addEventListener('timeout', () => {
        reject(new UploadError('上傳逾時，請稍後再試', 408, true));
      });

      // 設定請求
      xhr.open(method, uploadUrl);
      xhr.timeout = 60000; // 60 秒逾時

      // 設定必要的 headers
      Object.entries(headers).forEach(([key, value]) => {
        xhr.setRequestHeader(key, value);
      });

      // 發送請求
      xhr.send(blob);
    });
  } catch (error) {
    if (error instanceof UploadError) {
      throw error;
    }
    throw new UploadError(`上傳準備失敗：${(error as Error).message}`, undefined, false);
  }
}

/**
 * 上傳圖片（含重試邏輯）
 * M203: 有限次重試
 */
export async function uploadWithRetry(
  options: UploadOptions,
  maxRetries: number = 3
): Promise<void> {
  let lastError: UploadError | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      await uploadToSignedUrl(options);
      return; // 成功，直接返回
    } catch (error) {
      lastError = error as UploadError;

      // 如果不可重試或已達最大重試次數，直接拋出錯誤
      if (!lastError.retryable || attempt === maxRetries) {
        throw lastError;
      }

      // 指數退避重試：2^attempt * 1000ms
      const backoffMs = Math.pow(2, attempt) * 1000;
      await delay(backoffMs);
    }
  }

  // 理論上不會執行到這裡，但為了型別安全
  throw lastError || new UploadError('上傳失敗', undefined, false);
}

/**
 * 檢查 Signed URL 是否過期
 */
export function isSignedUrlExpired(expiresAt: string): boolean {
  const expiryTime = new Date(expiresAt).getTime();
  const now = Date.now();
  return now >= expiryTime;
}
