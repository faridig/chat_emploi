import React from 'react';
import { TimelineProgress, Step } from '@/components/ui/timeline-progress';
import { useSessionStore } from '@/stores/session-store';

const ALL_STEPS: Step[] = [
  { id: 'profile', label: 'Profil' },
  { id: 'search', label: 'Recherche' },
  { id: 'selection', label: 'Sélection' },
  { id: 'letter', label: 'Lettre' },
  { id: 'interview', label: 'Entretien' },
  { id: 'tracking', label: 'Suivi' },
];

export default function SessionLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Ce composant devra être 'use client' si on utilise le hook ici,
  // ou alors on passe currentStepId en props depuis la page (meilleur pour le Server Component).
  // Pour l'instant, on le laisse en Server Component.
  // const { currentStepId } = useSessionStore.getState(); // Ne pas faire ça dans un SC

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="flex h-20 items-center justify-center border-b px-8">
        <TimelineProgress steps={ALL_STEPS} currentStepId={'profile'} />
      </header>
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}
