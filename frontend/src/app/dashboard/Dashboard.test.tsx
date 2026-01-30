import React from 'react';
import { render, screen, within } from '@testing-library/react';
import { DndContext } from '@dnd-kit/core';
import { DashboardPage } from './page';
import '@testing-library/jest-dom';

// Mock the components with forwardRef to handle refs correctly
vi.mock('@/components/ui/card', () => ({
  Card: React.forwardRef<HTMLDivElement, { children: React.ReactNode }>(({ children }, ref) => (
    <div ref={ref} data-testid="card">{children}</div>
  )),
  CardHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="card-header">{children}</div>,
  CardTitle: ({ children }: { children: React.ReactNode }) => <h3 data-testid="card-title">{children}</h3>,
  CardContent: React.forwardRef<HTMLDivElement, { children: React.ReactNode }>(({ children }, ref) => (
    <div ref={ref} data-testid="card-content">{children}</div>
  )),
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children }: { children: React.ReactNode }) => <button>{children}</button>,
}));

// Mock child components to isolate the DashboardPage logic
vi.mock('./_components/KanbanLane', () => ({
    KanbanLane: ({ title, applications }: { title: string, applications: any[] }) => (
      <div data-testid={`lane-${title.toLowerCase().replace(' ', '-')}`}>
        <h3>{title}</h3>
        <div>
          {applications.map(app => (
            <div key={app.id} data-testid={`app-card-${app.id}`}>
              {app.role} at {app.company}
            </div>
          ))}
        </div>
      </div>
    ),
}));

describe('DashboardPage', () => {
    it('renders the main title', () => {
      render(
        <DndContext>
          <DashboardPage />
        </DndContext>
      );
      expect(screen.getByText('Vos candidatures')).toBeInTheDocument();
    });

    it('renders the Kanban columns', () => {
        render(
          <DndContext>
            <DashboardPage />
          </DndContext>
        );

        expect(screen.getByText('Postulées')).toBeInTheDocument();
        expect(screen.getByText('En cours')).toBeInTheDocument();
        expect(screen.getByText('Entretiens')).toBeInTheDocument();
        expect(screen.getByText('Refusées')).toBeInTheDocument();
    });

    it('renders the application cards in the correct columns', () => {
        render(
          <DndContext>
            <DashboardPage />
          </DndContext>
        );

        const appliedColumn = screen.getByTestId('lane-postulées');
        expect(within(appliedColumn).getByText(/Développeur Frontend/i)).toBeInTheDocument();
        expect(within(appliedColumn).getByText(/UI\/UX Designer/i)).toBeInTheDocument();

        const interviewsColumn = screen.getByTestId('lane-entretiens');
        expect(within(interviewsColumn).getByText(/Product Manager/i)).toBeInTheDocument();

        const inProgressColumn = screen.getByTestId('lane-en-cours');
        expect(within(inProgressColumn).getByText(/Data Analyst/i)).toBeInTheDocument();
    });
});
