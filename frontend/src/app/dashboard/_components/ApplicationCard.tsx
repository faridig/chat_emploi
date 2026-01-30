// frontend/src/app/dashboard/_components/ApplicationCard.tsx
"use client";

import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Application } from './types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface ApplicationCardProps {
  application: Application;
}

export function ApplicationCard({ application }: ApplicationCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: application.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <Card
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-white hover:bg-gray-50 cursor-grab active:cursor-grabbing shadow-md rounded-lg"
    >
      <CardHeader className="p-4">
        <CardTitle className="text-base font-semibold">{application.role}</CardTitle>
      </CardHeader>
      <CardContent className="p-4 text-sm text-text-secondary">
        <p>{application.company}</p>
        <p className="text-xs text-text-tertiary mt-2">{application.date}</p>
      </CardContent>
    </Card>
  );
}
