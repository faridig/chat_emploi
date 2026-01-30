'use client';
import React from 'react';
import { useSessionStore } from '@/stores/session-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';

const POINTS_TO_HIGHLIGHT = [
  { id: 'experience', label: 'Expérience pertinente' },
  { id: 'skills', label: 'Compétences clés' },
  { id: 'motivation', label: 'Motivation pour le poste' },
  { id: 'company_fit', label: 'Adéquation avec l_entreprise' },
];

export function LetterControls() {
  // const { letterOptions, setLetterOption } = useSessionStore();

  return (
    <Card
      className="h-full rounded-none border-l-0 border-t-0 md:border-l md:border-t-0"
      data-testid="customization-panel"
    >
      <CardHeader>
        <CardTitle>Personnalisation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Tone Slider */}
        <div>
          <Label htmlFor="tone-slider">Ton souhaité</Label>
          <div className="flex items-center gap-4 pt-2">
            <span className="text-sm text-muted-foreground">Amical</span>
            <Slider
              id="tone-slider"
              defaultValue={[50]}
              max={100}
              step={1}
              data-testid="tone-slider"
            />
            <span className="text-sm text-muted-foreground">Formel</span>
          </div>
        </div>

        {/* Points to Highlight */}
        <div>
          <Label>Points à mettre en avant</Label>
           <div className="mt-2 space-y-2" data-testid="highlight-checklist">
            {POINTS_TO_HIGHLIGHT.map(item => (
              <div key={item.id} className="flex items-center space-x-2">
                <Checkbox id={item.id} />
                <Label htmlFor={item.id} className="font-normal">
                  {item.label}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <Button className="w-full">
          Regénérer avec ces paramètres
        </Button>
      </CardContent>
    </Card>
  );
}
