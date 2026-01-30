/**
 * Tests pour le monitoring des Web Vitals et optimisations de performance
 * Module 11 : Cool Down & Polish
 */

import { render, screen } from '@testing-library/react';

// Mock de next/web-vitals
vi.mock('next/web-vitals', () => ({
  useReportWebVitals: vi.fn()
}));

describe('Web Vitals Monitoring', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('WebVitals component should call useReportWebVitals', () => {
    const mockReport = vi.fn();
    (useReportWebVitals as any).mockImplementation(mockReport);

    render(<WebVitals />);

    expect(useReportWebVitals).toHaveBeenCalledTimes(1);
    expect(mockReport).toHaveBeenCalledWith(expect.any(Function));
  });

  test.skip('WebVitals should log metrics to console in development', () => {
    const consoleSpy = vi.spyOn(console, 'log');
    const mockReport = vi.fn((callback) => {
      // Simuler un callback avec une métrique
      callback({
        name: 'FCP',
        value: 1200,
        rating: 'good',
        delta: 50,
        entries: [],
        id: 'v1-123456789'
      });
    });
    (useReportWebVitals as any).mockImplementation(mockReport);

    render(<WebVitals />);

    // Vérifier que le callback a été appelé avec la métrique
    expect(consoleSpy).toHaveBeenCalledWith({
      name: 'FCP',
      value: 1200,
      rating: 'good',
      delta: 50,
      entries: [],
      id: 'v1-123456789'
    });
  });

  test.skip('WebVitals should handle different metric types', () => {
    const consoleSpy = vi.spyOn(console, 'log');
    const mockReport = vi.fn((callback) => {
      // Simuler plusieurs types de métriques
      const metrics = [
        { name: 'FCP', value: 1200, rating: 'good' },
        { name: 'LCP', value: 2500, rating: 'needs-improvement' },
        { name: 'CLS', value: 0.1, rating: 'good' },
        { name: 'FID', value: 80, rating: 'good' },
        { name: 'TTFB', value: 300, rating: 'good' }
      ];

      metrics.forEach(metric => callback(metric));
    });
    (useReportWebVitals as any).mockImplementation(mockReport);

    render(<WebVitals />);

    expect(consoleSpy).toHaveBeenCalledTimes(5);
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'FCP', value: 1200 })
    );
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'LCP', value: 2500 })
    );
  });
});

describe('Performance Utilities', () => {
  test('should calculate performance score from metrics', () => {
    const calculatePerformanceScore = (metrics: any[]) => {
      let score = 100;

      metrics.forEach(metric => {
        if (metric.rating === 'good') score += 0;
        else if (metric.rating === 'needs-improvement') score -= 10;
        else if (metric.rating === 'poor') score -= 20;
      });

      return Math.max(0, Math.min(100, score));
    };

    const goodMetrics = [
      { name: 'FCP', rating: 'good' },
      { name: 'LCP', rating: 'good' },
      { name: 'CLS', rating: 'good' }
    ];

    const mixedMetrics = [
      { name: 'FCP', rating: 'good' },
      { name: 'LCP', rating: 'needs-improvement' },
      { name: 'CLS', rating: 'poor' }
    ];

    expect(calculatePerformanceScore(goodMetrics)).toBe(100);
    expect(calculatePerformanceScore(mixedMetrics)).toBe(70);
  });

  test('should format performance metrics for display', () => {
    const formatMetric = (metric: any) => {
      const formats: Record<string, (value: number) => string> = {
        'FCP': (v) => `${v}ms`,
        'LCP': (v) => `${v}ms`,
        'CLS': (v) => v.toFixed(3),
        'FID': (v) => `${v}ms`,
        'TTFB': (v) => `${v}ms`
      };

      return formats[metric.name]?.(metric.value) || metric.value.toString();
    };

    const fcp = { name: 'FCP', value: 1200 };
    const cls = { name: 'CLS', value: 0.123 };

    expect(formatMetric(fcp)).toBe('1200ms');
    expect(formatMetric(cls)).toBe('0.123');
  });
});
