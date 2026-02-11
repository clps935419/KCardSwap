export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
  statusCode: number
}

const ERROR_MESSAGES: Record<string, string> = {
  // Authentication errors (401)
  '401_INVALID_TOKEN': '登入已失效，請重新登入',
  '401_TOKEN_EXPIRED': '登入已過期，請重新登入',
  '401_UNAUTHORIZED': '尚未登入，請先登入',

  // Forbidden errors (403)
  '403_FORBIDDEN': '沒有權限執行此操作',
  '403_INSUFFICIENT_PERMISSIONS': '權限不足',

  // Not found errors (404)
  '404_NOT_FOUND': '找不到資源',
  '404_USER_NOT_FOUND': '找不到使用者',

  // Validation errors (422)
  '422_VALIDATION_ERROR': '資料驗證失敗，請檢查欄位是否正確',
  '422_LIMIT_EXCEEDED': '已達配額上限',
  '422_DAILY_UPLOAD_LIMIT': '已達每日上傳上限',
  '422_STORAGE_LIMIT': '已達儲存空間上限',
  '422_FILE_TOO_LARGE': '檔案過大',

  // Rate limiting (429)
  '429_RATE_LIMIT_EXCEEDED': '請求過於頻繁，請稍後再試',
  '429_DAILY_SEARCH_LIMIT': '已達每日搜尋上限，升級方案可解除限制',

  // Server errors (500)
  '500_INTERNAL_ERROR': '系統發生錯誤，請稍後再試',

  // Network errors
  NETWORK_ERROR: '網路連線異常，請檢查網路後再試',
  TIMEOUT_ERROR: '連線逾時，請稍後再試',
  UNKNOWN_ERROR: '發生未知錯誤，請稍後再試',
}

const formatLimitExceededMessage = (details?: Record<string, unknown>): string | null => {
  if (!details) {
    return null
  }

  const limitKey = details.limit_key
  const limitValue = details.limit_value
  const currentValue = details.current_value
  const resetAt = details.reset_at

  if (!limitKey || limitValue === undefined || limitValue === null) {
    return null
  }

  const resetText =
    typeof resetAt === 'string' ? `重置時間：${new Date(resetAt).toLocaleString('zh-TW')}` : ''

  const currentText =
    currentValue === undefined || currentValue === null ? '' : `，目前：${currentValue}`

  return `已達配額上限：${String(limitKey)}（上限：${String(limitValue)}${currentText}）。${resetText}`.trim()
}

const getErrorEnvelope = (data: unknown) => {
  if (!data || typeof data !== 'object') {
    return null
  }

  const payload = data as {
    error?: {
      code?: string
      message?: string
      details?: Record<string, unknown>
    }
    detail?: unknown
    message?: string
  }

  if (payload.error) {
    return payload.error
  }

  if (payload.detail) {
    if (typeof payload.detail === 'string') {
      return {
        message: payload.detail,
      }
    }

    if (typeof payload.detail === 'object') {
      const detail = payload.detail as Record<string, unknown>
      return {
        code: typeof detail.error_code === 'string' ? detail.error_code : undefined,
        message: typeof detail.message === 'string' ? detail.message : payload.message,
        details: detail,
      }
    }
  }

  if (payload.message) {
    return {
      message: payload.message,
    }
  }

  return null
}

export const mapApiError = (error: unknown): ApiError => {
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as {
      response?: {
        status?: number
        data?: unknown
      }
      code?: string
      message?: string
    }

    const statusCode = axiosError.response?.status || 500
    const envelope = getErrorEnvelope(axiosError.response?.data)
    const errorCode = envelope?.code || `${statusCode}_ERROR`
    const details = envelope?.details

    const limitMessage =
      errorCode === '422_LIMIT_EXCEEDED' ? formatLimitExceededMessage(details) : null

    return {
      code: errorCode,
      message:
        limitMessage ||
        ERROR_MESSAGES[errorCode] ||
        envelope?.message ||
        ERROR_MESSAGES.UNKNOWN_ERROR,
      details,
      statusCode,
    }
  }

  if (error && typeof error === 'object' && 'code' in error) {
    const networkError = error as { code?: string; message?: string }
    if (networkError.code === 'ECONNABORTED') {
      return {
        code: 'TIMEOUT_ERROR',
        message: ERROR_MESSAGES.TIMEOUT_ERROR,
        statusCode: 0,
      }
    }

    return {
      code: 'NETWORK_ERROR',
      message: ERROR_MESSAGES.NETWORK_ERROR,
      statusCode: 0,
    }
  }

  if (error instanceof Error) {
    return {
      code: 'CLIENT_ERROR',
      message: error.message || ERROR_MESSAGES.UNKNOWN_ERROR,
      statusCode: 0,
    }
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: ERROR_MESSAGES.UNKNOWN_ERROR,
    statusCode: 500,
  }
}
