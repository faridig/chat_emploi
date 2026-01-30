import { render, screen, fireEvent } from '@testing-library/react';
import { DndZone } from './dnd-zone';

describe('DndZone Component', () => {
  it('renders initial state correctly', () => {
    render(<DndZone onFileDrop={() => {}} />);
    expect(screen.getByText('Glissez-déposez votre CV ici')).toBeInTheDocument();
    expect(screen.getByText('PDF, DOCX, TXT')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /parcourir les fichiers/i })).toBeInTheDocument();
  });

  it('shows drag-active state on drag over', () => {
    const { container } = render(<DndZone onFileDrop={() => {}} />);
    const dropZone = container.firstChild as HTMLElement;

    fireEvent.dragEnter(dropZone, {
      dataTransfer: { types: ['Files'] },
    });

    // Test that the correct text is displayed
    expect(screen.getByText('Relâchez pour déposer le fichier')).toBeInTheDocument();
  });

  it('calls onFileDrop with the file on drop', () => {
    const onFileDrop = vi.fn();
    const { container } = render(<DndZone onFileDrop={onFileDrop} />);
    const dropZone = container.firstChild as HTMLElement;

    const file = new File(['(⌐□_□)'], 'cv.pdf', { type: 'application/pdf' });

    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file],
        types: ['Files'],
      },
    });

    expect(onFileDrop).toHaveBeenCalledWith(file);
  });
});
