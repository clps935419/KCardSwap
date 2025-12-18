import { useAuthStore } from '../src/shared/state/authStore';

// Simple test without rendering hooks
describe('useAuthStore', () => {
  beforeEach(() => {
    // Clear store state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it('should initialize with default state', () => {
    const state = useAuthStore.getState();

    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should set user correctly', () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      nickname: 'TestUser',
    };

    useAuthStore.getState().setUser(mockUser);
    const state = useAuthStore.getState();

    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });

  it('should clear error', () => {
    // Set error
    useAuthStore.setState({ error: 'Test error' });
    expect(useAuthStore.getState().error).toBe('Test error');

    // Clear error
    useAuthStore.getState().clearError();
    expect(useAuthStore.getState().error).toBeNull();
  });
});
