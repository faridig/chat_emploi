import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { JobOfferCard } from './job-offer-card';
import { JobOffer } from '@/types/job-offer';

const mockOffer: JobOffer = {
  id: '1',
  title: 'Développeur Frontend',
  company: 'Tech Solutions',
  location: 'Paris, France',
  matchScore: 0.92,
  description: 'Nous recherchons un développeur Frontend expérimenté...',
  skills: ['React', 'TypeScript', 'Next.js'],
  contractType: 'CDI',
  publishedAt: '2026-01-29T10:00:00Z',
};

describe('JobOfferCard', () => {
  it('renders all offer details correctly', () => {
    render(<JobOfferCard offer={mockOffer} />);

    expect(screen.getByText('92%')).toBeInTheDocument();
    expect(screen.getByText('Développeur Frontend')).toBeInTheDocument();
    expect(screen.getByText('Tech Solutions')).toBeInTheDocument();
    expect(screen.getByText('Paris, France')).toBeInTheDocument();
    expect(screen.getByText('CDI')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
  });

  it('applies correct gradient based on match score', () => {
    const { container } = render(<JobOfferCard offer={mockOffer} />);
    const badge = screen.getByText('92%').parentElement;
    // Test for a class that should be applied for high scores
    expect(badge).toHaveClass('from-green-500');
  });
});
