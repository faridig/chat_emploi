import { render, screen } from '@testing-library/react';
import SessionPage from './page';

// Mock child components
vi.mock('@/components/feature/chat-panel', () => ({
  ChatPanel: () => <div data-testid="chat-panel"></div>,
}));

vi.mock('@/components/feature/context-panel', () => ({
  ContextPanel: () => <div data-testid="context-panel"></div>,
}));

describe('SessionPage', () => {
  it('renders the main layout with ChatPanel and ContextPanel', () => {
    render(<SessionPage />);

    expect(screen.getByTestId('chat-panel')).toBeInTheDocument();
    expect(screen.getByTestId('context-panel')).toBeInTheDocument();
  });
});
