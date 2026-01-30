import { render, screen } from '@testing-library/react';
import HomePage from '@/app/page';

// Mock the DndZone component to isolate the page layout test
vi.mock('@/components/feature/dnd-zone', () => ({
  DndZone: vi.fn(() => <div data-testid="dnd-zone"></div>),
}));

describe('HomePage', () => {
  it('renders all elements described in DESIGN.md', () => {
    render(<HomePage />);

    // Header
    expect(screen.getByText('Chat Emploi')).toBeInTheDocument();
    expect(screen.getByText('Votre coach emploi empathique')).toBeInTheDocument();

    // Main Content
    expect(screen.getByRole('heading', { name: /Bienvenue ! Prêt à transformer votre recherche ?/i })).toBeInTheDocument();
    expect(screen.getByText('Importez votre CV pour commencer')).toBeInTheDocument();

    // DndZone (mocked)
    expect(screen.getByTestId('dnd-zone')).toBeInTheDocument();

    // Informations
    expect(screen.getByText('Confidentialité totale')).toBeInTheDocument();
    expect(screen.getByText('Vos données restent sur votre ordinateur')).toBeInTheDocument();

    // Footer
    expect(screen.getByRole('button', { name: /mode démo \(sans cv\)/i })).toBeInTheDocument();
  });
});
