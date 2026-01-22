import { useEffect, useState } from 'react';
import { Slot, useRouter, useSegments } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/src/shared/state/authStore';
import { GluestackUIProvider } from '@/src/shared/ui/components/gluestack-ui-provider';
import { useNotifications } from '@/src/features/notifications/hooks/useNotifications';
import { configureSDK } from '@/src/shared/api/sdk';
import '@/global.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export default function RootLayout() {
  const segments = useSegments();
  const router = useRouter();
  const { isAuthenticated, isLoading, initialize } = useAuthStore();
  const [sdkConfigured, setSdkConfigured] = useState(false);

  // Initialize push notifications (M404)
  useNotifications();

  // Configure SDK and initialize auth on app start
  useEffect(() => {
    // Configure SDK first
    configureSDK();
    setSdkConfigured(true);
    
    // Then initialize auth
    initialize();
  }, []);

  // Handle navigation based on auth state
  useEffect(() => {
    // Wait for SDK to be configured and auth to finish loading
    if (!sdkConfigured || isLoading) return;

    const inAuthGroup = segments[0] === 'auth';

    if (!isAuthenticated && !inAuthGroup) {
      // Redirect to login if not authenticated
      router.replace('/auth/login');
    } else if (isAuthenticated && inAuthGroup) {
      // Redirect to main app if authenticated
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, isLoading, segments, sdkConfigured]);

  return (
    <GluestackUIProvider mode="light">
      <QueryClientProvider client={queryClient}>
        <Slot />
      </QueryClientProvider>
    </GluestackUIProvider>
  );
}
