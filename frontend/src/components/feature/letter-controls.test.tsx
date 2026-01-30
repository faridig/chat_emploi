import { render, screen, fireEvent } from '@testing-library/react';
import { LetterControls } from './letter-controls';
import { useSessionStore } from '@/stores/session-store';

vi.mock('@/stores/session-store', () => ({
  useSessionStore: vi.fn(),
}));

describe('LetterControls', () => {
  const mockedUseSessionStore = useSessionStore as any;
  const setLetterOption = vi.fn();

  beforeEach(() => {
    mockedUseSessionStore.mockReturnValue({
      letterOptions: {
        tone: 'professional',
        pointsToHighlight: ['experience'],
      },
      setLetterOption,
    });
  });

  it('renders slider and checkboxes correctly', () => {
    render(<LetterControls />);
    expect(screen.getByText('Ton souhaité')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toBeInTheDocument();
    expect(screen.getByText('Points à mettre en avant')).toBeInTheDocument();
    expect(screen.getByLabelText('Expérience pertinente')).toBeInTheDocument();
  });
});
