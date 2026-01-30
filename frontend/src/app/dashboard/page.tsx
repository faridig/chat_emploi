"use client";

import React, { useState } from 'react';
import { DndContext, closestCenter, DragEndEvent } from '@dnd-kit/core';
import { arrayMove } from '@dnd-kit/sortable';
import { KanbanLane } from './_components/KanbanLane';
import { Application, Lane } from './_components/types';
import { Button } from '@/components/ui/button';

const initialLanes: Lane[] = [
  { id: 'applied', title: 'Postulées' },
  { id: 'in-progress', title: 'En cours' },
  { id: 'interviews', title: 'Entretiens' },
  { id: 'rejected', title: 'Refusées' },
];

const initialApplications: Application[] = [
  { id: 'app-1', laneId: 'applied', company: 'Tech Startup Inc.', role: 'Développeur Frontend', date: '2026-01-15' },
  { id: 'app-2', laneId: 'applied', company: 'Innovate Solutions', role: 'UI/UX Designer', date: '2026-01-18' },
  { id: 'app-3', laneId: 'in-progress', company: 'Data Systems', role: 'Data Analyst', date: '2026-01-12' },
  { id: 'app-4', laneId: 'interviews', company: 'Creative Minds', role: 'Product Manager', date: '2026-01-10' },
  { id: 'app-5', laneId: 'rejected', company: 'MegaCorp', role: 'Backend Engineer', date: '2026-01-05' },
];

export default function DashboardPage() {
  const [lanes, setLanes] = useState<Lane[]>(initialLanes);
  const [applications, setApplications] = useState<Application[]>(initialApplications);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const activeApp = applications.find(app => app.id === active.id);
      const overLaneId = over.id.toString().replace('lane-', '');

      if (activeApp && activeApp.laneId !== overLaneId) {
        setApplications(prev =>
          prev.map(app =>
            app.id === active.id ? { ...app, laneId: overLaneId } : app
          )
        );
      }
    }
  };

  return (
    <div className="flex flex-col h-full bg-background text-text-primary p-6">
      <header className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Vos candidatures</h1>
            <p className="text-text-secondary">Suivez et organisez vos postulations.</p>
          </div>
          <Button>Nouvelle recherche</Button>
        </div>
      </header>

      <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 flex-grow">
          {lanes.map(lane => (
            <KanbanLane
              key={lane.id}
              id={`lane-${lane.id}`}
              title={lane.title}
              applications={applications.filter(app => app.laneId === lane.id)}
            />
          ))}
        </div>
      </DndContext>
    </div>
  );
}

// Exporting for testing purposes
export { DashboardPage };
