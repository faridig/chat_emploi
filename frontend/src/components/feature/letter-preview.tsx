import React from 'react';
import { Badge } from '@/components/ui/badge';

interface LetterPreviewProps {
  content: string;
}

export function LetterPreview({ content }: LetterPreviewProps) {
  const wordCount = content.split(/\s+/).filter(Boolean).length;

  return (
    <div className="flex h-full flex-col p-6" data-testid="letter-preview">
      <header className="mb-4">
        <h2 className="text-xl font-bold">Aperçu de la lettre</h2>
        <p className="text-sm text-muted-foreground">C'est un bon début ! Vous pouvez affiner le style à droite.</p>
      </header>
      <div className="flex-1 overflow-y-auto rounded-lg border bg-surface p-6 shadow-inner">
        <div
          className="prose prose-sm max-w-none"
          // Using paragraphs for demo purposes.
          // Real content might need sanitization if it's HTML.
        >
          {content.split('\n\n').map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>
      </div>
      <footer className="mt-4 text-right">
        <Badge variant="outline">{wordCount} mots</Badge>
      </footer>
    </div>
  );
}
