/**
 * Tests pour le composant LazyImage
 * Module 11 : Cool Down & Polish
 */

import { describe, test, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { LazyImage } from '@/components/performance/LazyImage';

// Mock IntersectionObserver
const mockIntersectionObserver = vi.fn();
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
});
window.IntersectionObserver = mockIntersectionObserver;

describe('LazyImage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset Image constructor
    global.Image = vi.fn().mockImplementation(() => ({
      onload: vi.fn(),
      onerror: vi.fn(),
      src: '',
    }));
  });

  test('renders with placeholder initially', () => {
    render(<LazyImage src="/test.jpg" alt="Test image" />);

    const img = screen.getByAltText('Test image');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', expect.stringContaining('data:image/svg+xml'));
  });

  test('loads image when in viewport', async () => {
    const mockOnLoad = vi.fn();
    const mockImageConstructor = vi.fn().mockImplementation(() => {
      const img = {
        onload: vi.fn(),
        onerror: vi.fn(),
        src: '',
      };

      // Simuler le chargement réussi
      setTimeout(() => {
        img.onload();
      }, 10);

      return img;
    });

    global.Image = mockImageConstructor;

    render(
      <LazyImage
        src="/test.jpg"
        alt="Test image"
        onLoad={mockOnLoad}
      />
    );

    // Simuler l'intersection
    const observerCallback = mockIntersectionObserver.mock.calls[0][0];
    const entry = { isIntersecting: true, target: {} };
    observerCallback([entry]);

    await waitFor(() => {
      expect(mockImageConstructor).toHaveBeenCalled();
      expect(mockOnLoad).toHaveBeenCalled();
    });
  });

  test('handles image load error', async () => {
    const mockOnError = vi.fn();
    const mockImageConstructor = vi.fn().mockImplementation(() => {
      const img = {
        onload: vi.fn(),
        onerror: vi.fn(),
        src: '',
      };

      // Simuler une erreur de chargement
      setTimeout(() => {
        img.onerror();
      }, 10);

      return img;
    });

    global.Image = mockImageConstructor;

    render(
      <LazyImage
        src="/invalid.jpg"
        alt="Invalid image"
        onError={mockOnError}
      />
    );

    // Simuler l'intersection
    const observerCallback = mockIntersectionObserver.mock.calls[0][0];
    const entry = { isIntersecting: true, target: {} };
    observerCallback([entry]);

    await waitFor(() => {
      expect(mockImageConstructor).toHaveBeenCalled();
      expect(mockOnError).toHaveBeenCalled();
    });
  });

  test('loads immediately when priority is true', () => {
    const mockImageConstructor = vi.fn().mockImplementation(() => ({
      onload: vi.fn(),
      onerror: vi.fn(),
      src: '',
    }));

    global.Image = mockImageConstructor;

    render(
      <LazyImage
        src="/test.jpg"
        alt="Test image"
        priority
      />
    );

    expect(mockImageConstructor).toHaveBeenCalled();
    expect(mockIntersectionObserver).not.toHaveBeenCalled();
  });

  test('applies width and height styles', () => {
    render(
      <LazyImage
        src="/test.jpg"
        alt="Test image"
        width={300}
        height={200}
      />
    );

    const container = screen.getByAltText('Test image').parentElement;
    expect(container).toHaveStyle({
      width: '300px',
      height: '200px',
    });
  });

  test('uses blurDataURL for placeholder', () => {
    const blurDataURL = 'data:image/jpeg;base64,test';

    render(
      <LazyImage
        src="/test.jpg"
        alt="Test image"
        blurDataURL={blurDataURL}
      />
    );

    const placeholder = screen.getByAltText('Test image').previousSibling;
    expect(placeholder).toHaveStyle({
      backgroundImage: `url(${blurDataURL})`,
    });
  });

  test('applies custom className', () => {
    render(
      <LazyImage
        src="/test.jpg"
        alt="Test image"
        className="custom-class"
      />
    );

    const container = screen.getByAltText('Test image').parentElement;
    expect(container).toHaveClass('custom-class');
  });

  test('sets loading attribute based on priority', () => {
    const { rerender } = render(
      <LazyImage
        src="/test.jpg"
        alt="Test image"
        priority={false}
      />
    );

    let img = screen.getByAltText('Test image');
    expect(img).toHaveAttribute('loading', 'lazy');

    rerender(
      <LazyImage
        src="/test.jpg"
        alt="Test image"
        priority={true}
      />
    );

    img = screen.getByAltText('Test image');
    expect(img).toHaveAttribute('loading', 'eager');
  });

  test('shows loading spinner while loading', () => {
    render(<LazyImage src="/test.jpg" alt="Test image" />);

    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
  });

  test('shows error state when image fails to load', async () => {
    const mockImageConstructor = vi.fn().mockImplementation(() => {
      const img = {
        onload: vi.fn(),
        onerror: vi.fn(),
        src: '',
      };

      setTimeout(() => {
        img.onerror();
      }, 10);

      return img;
    });

    global.Image = mockImageConstructor;

    render(<LazyImage src="/invalid.jpg" alt="Invalid image" />);

    // Simuler l'intersection
    const observerCallback = mockIntersectionObserver.mock.calls[0][0];
    const entry = { isIntersecting: true, target: {} };
    observerCallback([entry]);

    await waitFor(() => {
      expect(screen.getByText('Image non disponible')).toBeInTheDocument();
    });
  });
});
