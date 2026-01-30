import { useSessionStore, SessionState } from './session-store';
import { act } from '@testing-library/react';

// Reset store before each test
beforeEach(() => {
  act(() => {
    useSessionStore.setState({
      messages: [],
      isLoading: false,
      currentStepId: 'profile',
      addMessage: (role, content) => {
        useSessionStore.setState(state => ({
          messages: [...state.messages, { role, content, id: state.messages.length + 1 }]
        }))
      },
      setIsLoading: (loading) => {
        useSessionStore.setState({ isLoading: loading });
      }
    });
  });
});

describe('useSessionStore', () => {
  it('should have initial state', () => {
    const state = useSessionStore.getState();
    expect(state.messages).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.currentStepId).toBe('profile');
  });

  it('should add a message', () => {
    act(() => {
      useSessionStore.getState().addMessage('user', 'Hello');
    });
    const state = useSessionStore.getState();
    expect(state.messages).toHaveLength(1);
    expect(state.messages[0]).toEqual({ role: 'user', content: 'Hello', id: 1 });
  });

  it('should set loading state', () => {
    act(() => {
      useSessionStore.getState().setIsLoading(true);
    });
    const state = useSessionStore.getState();
    expect(state.isLoading).toBe(true);
  });
});
