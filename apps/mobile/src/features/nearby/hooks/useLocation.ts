/**
 * Location hooks for nearby search
 * M301: 定位權限與取得座標
 * 
 * 功能：
 * - 請求定位權限
 * - 取得當前座標
 * - 處理權限拒絕情況
 */

import { useState, useEffect } from 'react';
import * as Location from 'expo-location';

export interface LocationCoords {
  latitude: number;
  longitude: number;
}

export interface LocationError {
  code: 'PERMISSION_DENIED' | 'LOCATION_UNAVAILABLE' | 'TIMEOUT' | 'UNKNOWN';
  message: string;
}

export interface UseLocationResult {
  location: LocationCoords | null;
  error: LocationError | null;
  isLoading: boolean;
  requestLocation: () => Promise<void>;
  hasPermission: boolean | null;
}

/**
 * Hook for requesting and getting user's current location
 * 
 * @returns Location state and methods
 * 
 * @example
 * ```tsx
 * const { location, error, requestLocation, hasPermission } = useLocation();
 * 
 * if (!hasPermission) {
 *   return <PermissionDenied onRetry={requestLocation} />;
 * }
 * ```
 */
export function useLocation(): UseLocationResult {
  const [location, setLocation] = useState<LocationCoords | null>(null);
  const [error, setError] = useState<LocationError | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  const checkPermission = async (): Promise<boolean> => {
    try {
      const { status } = await Location.getForegroundPermissionsAsync();
      const granted = status === 'granted';
      setHasPermission(granted);
      return granted;
    } catch (err) {
      console.error('Failed to check location permission:', err);
      setHasPermission(false);
      return false;
    }
  };

  const requestPermission = async (): Promise<boolean> => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      const granted = status === 'granted';
      setHasPermission(granted);

      if (!granted) {
        setError({
          code: 'PERMISSION_DENIED',
          message: '需要定位權限才能使用附近搜尋功能',
        });
      }

      return granted;
    } catch (err) {
      console.error('Failed to request location permission:', err);
      setError({
        code: 'UNKNOWN',
        message: '無法請求定位權限',
      });
      setHasPermission(false);
      return false;
    }
  };

  const getCurrentLocation = async (): Promise<LocationCoords | null> => {
    try {
      const result = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
        timeInterval: 10000, // 10 seconds timeout
      });

      const coords: LocationCoords = {
        latitude: result.coords.latitude,
        longitude: result.coords.longitude,
      };

      return coords;
    } catch (err: any) {
      console.error('Failed to get current location:', err);
      
      // Map error codes
      if (err.code === 'E_LOCATION_SERVICES_DISABLED') {
        setError({
          code: 'LOCATION_UNAVAILABLE',
          message: '定位服務未開啟，請在設定中開啟定位服務',
        });
      } else if (err.code === 'E_LOCATION_TIMEOUT') {
        setError({
          code: 'TIMEOUT',
          message: '取得位置逾時，請稍後再試',
        });
      } else {
        setError({
          code: 'UNKNOWN',
          message: '無法取得目前位置',
        });
      }

      return null;
    }
  };

  const requestLocation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Check if we already have permission
      let granted = await checkPermission();

      // If not, request it
      if (!granted) {
        granted = await requestPermission();
      }

      // If permission granted, get location
      if (granted) {
        const coords = await getCurrentLocation();
        if (coords) {
          setLocation(coords);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Check permission on mount
  useEffect(() => {
    checkPermission();
  }, []);

  return {
    location,
    error,
    isLoading,
    requestLocation,
    hasPermission,
  };
}
