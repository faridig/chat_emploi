import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import LetterPage from './page';

vi.mock('@/components/feature/letter-preview', () => ({
  LetterPreview: () => <div data-testid="letter-preview"></div>,
}));

vi.mock('@/components/feature/letter-controls', () => ({
  LetterControls: () => <div data-testid="letter-controls"></div>,
}));

describe('LetterPage', () => {
  it('renders the two-column layout and action buttons', () => {
    render(<LetterPage />);
    expect(screen.getByTestId('letter-preview')).toBeInTheDocument();
    expect(screen.getByTestId('letter-controls')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /télécharger pdf/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /copier le texte/i })).toBeInTheDocument();
  });
});
