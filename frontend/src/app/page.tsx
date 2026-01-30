'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { DndZone } from '@/components/feature/dnd-zone';
import { Lock } from 'lucide-react';

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  // Future state management with Zustand will go here
  // const { setCvFile, setAppState } = useAppStore();

  const handleFileDrop = (droppedFile: File) => {
    console.log('File dropped:', droppedFile.name);
    setFile(droppedFile);
    // TODO: Connect to backend
    // setCvFile(droppedFile);
    // setAppState('parsing_cv');
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
      <header className="absolute top-0 left-0 p-6">
        <h1 className="text-xl font-bold text-text-primary">Chat Emploi</h1>
        <p className="text-sm text-text-secondary">Votre coach emploi empathique</p>
      </header>

      <main className="flex flex-col items-center text-center">
        {/* DESIGN.md: Illustration: main tendue avec petite plante (à ajouter) */}
        <h2 className="text-3xl font-semibold text-text-primary">
          Bienvenue ! Prêt à transformer votre recherche ?
        </h2>
        <p className="mt-2 text-lg text-text-secondary">
          Importez votre CV pour commencer
        </p>

        <div className="mt-8">
          <DndZone onFileDrop={handleFileDrop} />
        </div>

        {file && (
          <div className="mt-4 text-sm text-success">
            Fichier <span className="font-semibold">{file.name}</span> prêt à être analysé.
          </div>
        )}

        <div className="mt-8 flex items-center gap-2">
          <Lock size={16} className="text-success" />
          <div className="text-left">
            <p className="text-sm font-semibold text-success">Confidentialité totale</p>
            <p className="text-xs text-text-secondary">Vos données restent sur votre ordinateur</p>
          </div>
        </div>
      </main>

      <footer className="absolute bottom-0 p-6">
        <Button variant="ghost">Mode démo (sans CV)</Button>
      </footer>
    </div>
  );
}
