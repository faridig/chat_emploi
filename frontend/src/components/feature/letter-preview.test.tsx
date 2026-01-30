import { render, screen } from '@testing-library/react';
import { LetterPreview } from './letter-preview';

describe('LetterPreview', () => {
  it('renders letter content and word count', () => {
    const mockContent = "Ceci est un test.".repeat(20); // 4 * 20 = 80 words approx
    render(<LetterPreview content={mockContent} />);

    expect(screen.getByText(/c'est un bon début/i)).toBeInTheDocument();
    expect(screen.getByText(/mots/i)).toBeInTheDocument();
  });
});
