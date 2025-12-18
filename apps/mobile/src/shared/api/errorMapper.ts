// API Error types
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  statusCode: number;
}

// Backend error codes mapping to user-friendly messages
export const ERROR_MESSAGES: Record<string, string> = {
  // Authentication errors (401)
  '401_INVALID_TOKEN': 'Invalid or expired token. Please login again.',
  '401_TOKEN_EXPIRED': 'Your session has expired. Please login again.',
  '401_UNAUTHORIZED': 'Unauthorized access. Please login.',

  // Forbidden errors (403)
  '403_FORBIDDEN': 'You do not have permission to perform this action.',
  '403_INSUFFICIENT_PERMISSIONS': 'Insufficient permissions.',

  // Not found errors (404)
  '404_NOT_FOUND': 'Resource not found.',
  '404_USER_NOT_FOUND': 'User not found.',

  // Validation errors (422)
  '422_VALIDATION_ERROR': 'Invalid input. Please check your data.',
  '422_LIMIT_EXCEEDED': 'You have exceeded your limit.',
  '422_DAILY_UPLOAD_LIMIT': 'Daily upload limit reached.',
  '422_STORAGE_LIMIT': 'Storage limit exceeded.',
  '422_FILE_TOO_LARGE': 'File size too large.',

  // Rate limiting (429)
  '429_RATE_LIMIT_EXCEEDED': 'Too many requests. Please try again later.',
  '429_DAILY_SEARCH_LIMIT':
    'Daily search limit reached. Upgrade to premium for unlimited searches.',

  // Server errors (500)
  '500_INTERNAL_ERROR': 'An unexpected error occurred. Please try again.',

  // Network errors
  NETWORK_ERROR: 'Network connection error. Please check your internet connection.',
  TIMEOUT_ERROR: 'Request timeout. Please try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred.',
};

/**
 * Maps backend error response to user-friendly error message
 */
export function mapApiError(error: unknown): ApiError {
  // Axios error
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as {
      response?: {
        status: number;
        data?: {
          error?: {
            code?: string;
            message?: string;
            details?: Record<string, unknown>;
          };
        };
      };
      code?: string;
      message?: string;
    };

    const statusCode = axiosError.response?.status || 500;
    const errorData = axiosError.response?.data?.error;
    const errorCode = errorData?.code || `${statusCode}_ERROR`;

    return {
      code: errorCode,
      message: ERROR_MESSAGES[errorCode] || errorData?.message || ERROR_MESSAGES.UNKNOWN_ERROR,
      details: errorData?.details,
      statusCode,
    };
  }

  // Network error
  if (error && typeof error === 'object' && 'code' in error) {
    const networkError = error as { code?: string; message?: string };
    if (networkError.code === 'ECONNABORTED') {
      return {
        code: 'TIMEOUT_ERROR',
        message: ERROR_MESSAGES.TIMEOUT_ERROR,
        statusCode: 0,
      };
    }
    return {
      code: 'NETWORK_ERROR',
      message: ERROR_MESSAGES.NETWORK_ERROR,
      statusCode: 0,
    };
  }

  // Generic error
  return {
    code: 'UNKNOWN_ERROR',
    message: ERROR_MESSAGES.UNKNOWN_ERROR,
    statusCode: 500,
  };
}
