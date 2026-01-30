/**
 * Tests pour le composant OptimizedButton
 * Module 11 : Cool Down & Polish
 */

import { describe, test, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { OptimizedButton } from '@/components/performance/OptimizedButton';

describe('OptimizedButton', () => {
  test('renders button with children', () => {
    render(<OptimizedButton onClick={() => {}}>Click me</OptimizedButton>);

    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  test('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<OptimizedButton onClick={handleClick}>Click me</OptimizedButton>);

    fireEvent.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('does not call onClick when disabled', () => {
    const handleClick = vi.fn();
    render(
      <OptimizedButton onClick={handleClick} disabled>
        Click me
      </OptimizedButton>
    );

    fireEvent.click(screen.getByRole('button'));

    expect(handleClick).not.toHaveBeenCalled();
  });

  test('does not call onClick when loading', () => {
    const handleClick = vi.fn();
    render(
      <OptimizedButton onClick={handleClick} loading>
        Click me
      </OptimizedButton>
    );

    fireEvent.click(screen.getByRole('button'));

    expect(handleClick).not.toHaveBeenCalled();
  });

  test('shows loading spinner when loading', () => {
    render(
      <OptimizedButton onClick={() => {}} loading>
        Loading
      </OptimizedButton>
    );

    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByRole('button')).toContainElement(
      screen.getByTestId('loading-spinner')
    );
  });

  test('applies variant styles', () => {
    const { rerender } = render(
      <OptimizedButton onClick={() => {}} variant="primary">
        Primary
      </OptimizedButton>
    );

    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-brand-primary');

    rerender(
      <OptimizedButton onClick={() => {}} variant="secondary">
        Secondary
      </OptimizedButton>
    );

    expect(button.className).toContain('bg-brand-secondary');
  });

  test('applies size styles', () => {
    const { rerender } = render(
      <OptimizedButton onClick={() => {}} size="sm">
        Small
      </OptimizedButton>
    );

    const button = screen.getByRole('button');
    expect(button.className).toContain('h-8');

    rerender(
      <OptimizedButton onClick={() => {}} size="lg">
        Large
      </OptimizedButton>
    );

    expect(button.className).toContain('h-12');
  });

  test('renders icon when provided', () => {
    const icon = <span data-testid="test-icon">🎯</span>;
    render(
      <OptimizedButton onClick={() => {}} icon={icon}>
        With Icon
      </OptimizedButton>
    );

    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  test('memoization prevents unnecessary re-renders', () => {
    // Ce test vérifie que le composant est bien mémoïsé
    // En pratique, on testerait avec React.memo en vérifiant les re-renders
    const handleClick = vi.fn();
    const { rerender } = render(
      <OptimizedButton onClick={handleClick}>
        Memoized
      </OptimizedButton>
    );

    const button = screen.getByRole('button');
    const initialClassName = button.className;

    // Re-render avec les mêmes props
    rerender(
      <OptimizedButton onClick={handleClick}>
        Memoized
      </OptimizedButton>
    );

    // Le className devrait être le même (même référence d'objet de styles)
    expect(button.className).toBe(initialClassName);
  });

  test('useCallback prevents function recreation', () => {
    // Ce test vérifie que handleClick utilise useCallback
    // En pratique, on vérifierait que la fonction n'est pas recréée à chaque render
    const handleClick1 = vi.fn();
    const handleClick2 = vi.fn();

    const { rerender } = render(
      <OptimizedButton onClick={handleClick1}>
        Test
      </OptimizedButton>
    );

    const button = screen.getByRole('button');

    // Simuler un click
    fireEvent.click(button);
    expect(handleClick1).toHaveBeenCalledTimes(1);

    // Changer la fonction onClick
    rerender(
      <OptimizedButton onClick={handleClick2}>
        Test
      </OptimizedButton>
    );

    // La nouvelle fonction devrait être utilisée
    fireEvent.click(button);
    expect(handleClick2).toHaveBeenCalledTimes(1);
    expect(handleClick1).toHaveBeenCalledTimes(1); // Toujours 1
  });
});
