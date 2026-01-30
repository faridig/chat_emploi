import { render, screen, fireEvent } from '@testing-library/react';
import { ChatPanel } from './chat-panel';
import { useSessionStore } from '@/stores/session-store';
import React from 'react';

// Mock the store
vi.mock('@/stores/session-store');

describe('ChatPanel', () => {
  it('renders messages from the store', () => {
    (useSessionStore as any).mockReturnValue({
      messages: [
        { id: 1, role: 'agent', content: 'Hello Agent' },
        { id: 2, role: 'user', content: 'Hello User' },
      ],
      isLoading: false,
    });

    render(<ChatPanel />);

    expect(screen.getByText('Hello Agent')).toBeInTheDocument();
    expect(screen.getByText('Hello User')).toBeInTheDocument();
  });

  it('shows quick action buttons', () => {
    (useSessionStore as any).mockReturnValue({ messages: [], isLoading: false });
    render(<ChatPanel />);

    expect(screen.getByRole('button', { name: /je suis en reconversion/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /je cherche mon premier emploi/i })).toBeInTheDocument();
  });

  it('calls addMessage when sending a message', () => {
    const addMessage = vi.fn();
    (useSessionStore as any).mockReturnValue({ messages: [], isLoading: false, addMessage });

    render(<ChatPanel />);

    const input = screen.getByPlaceholderText(/je recherche un poste de.../i);
    fireEvent.change(input, { target: { value: 'New Message' } });
    fireEvent.click(screen.getByRole('button', { name: /envoyer/i }));

    expect(addMessage).toHaveBeenCalledWith('user', 'New Message');
  });
});
