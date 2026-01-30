// frontend/src/app/dashboard/_components/KanbanLane.tsx
"use client";

import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { ApplicationCard } from './ApplicationCard';
import { Application } from './types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface KanbanLaneProps {
  id: string;
  title: string;
  applications: Application[];
}

export function KanbanLane({ id, title, applications }: KanbanLaneProps) {
  const { setNodeRef } = useDroppable({ id });

  return (
    <Card className="flex flex-col bg-surface border border-[#E2E8F0] rounded-lg shadow-sm h-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-text-primary">{title}</CardTitle>
      </CardHeader>
      <CardContent ref={setNodeRef} className="flex-grow p-4 space-y-4 overflow-y-auto">
        <SortableContext items={applications.map(a => a.id)} strategy={verticalListSortingStrategy}>
          {applications.map(app => (
            <ApplicationCard key={app.id} application={app} />
          ))}
        </SortableContext>
      </CardContent>
    </Card>
  );
}
