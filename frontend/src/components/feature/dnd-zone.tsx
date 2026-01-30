'use client';

import { useState, useCallback, useRef } from 'react';
import { UploadCloud } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface DndZoneProps {
  onFileDrop: (file: File) => void;
  className?: string;
}

export function DndZone({ onFileDrop, className }: DndZoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileDrop(e.dataTransfer.files[0]);
    }
  }, [onFileDrop]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileDrop(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    inputRef.current?.click();
  };

  return (
    <div
      className={cn(
        'flex h-64 w-full max-w-md flex-col items-center justify-center rounded-lg border-2 border-dashed border-[#E2E8F0] bg-surface transition-colors duration-300',
        isDragActive ? 'border-primary bg-primary/10' : '',
        className
      )}
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        id="file-upload"
        className="hidden"
        onChange={handleChange}
        accept=".pdf,.docx,.txt"
        data-testid="file-input"
      />
      <div className="text-center">
        <UploadCloud
          className={cn(
            'mx-auto mb-4 h-16 w-16 text-text-tertiary transition-colors',
            isDragActive ? 'text-primary' : ''
          )}
          strokeWidth={1.5}
        />
        <h3 className="text-lg font-semibold text-text-primary">
          {isDragActive ? 'Relâchez pour déposer le fichier' : 'Glissez-déposez votre CV ici'}
        </h3>
        <p className="text-sm text-text-secondary">ou</p>
        <Button variant="outline" className="mt-4" onClick={onButtonClick}>
          Parcourir les fichiers
        </Button>
        <p className="mt-4 text-xs text-text-tertiary">PDF, DOCX, TXT</p>
      </div>
    </div>
  );
}
