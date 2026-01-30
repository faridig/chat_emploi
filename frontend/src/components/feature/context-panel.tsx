'use client';
// Ce composant est un placeholder pour le panneau de droite.
// Il sera développé dans une tâche future.

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export function ContextPanel() {
  return (
    <Card className="h-full rounded-none border-l border-t-0">
      <CardHeader>
        <CardTitle>Votre profil en cours</CardTitle>
        <CardDescription>Basé sur votre CV et notre conversation.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="mb-2 flex justify-between">
              <h4 className="text-sm font-medium">Complétude du profil</h4>
              <span className="text-sm font-bold text-primary">40%</span>
            </div>
            {/* Le composant Progress n'existe pas, on le remplace par un div pour l'instant */}
            <div className="h-2 w-full rounded-full bg-muted">
              <div className="h-2 rounded-full bg-primary" style={{ width: '40%' }}></div>
            </div>
          </div>
          <div className="text-sm">
            <h4 className="font-semibold">Expériences clés</h4>
            <ul className="mt-1 list-disc list-inside text-muted-foreground">
              <li>Développeur @ Tech Corp (5 ans)</li>
              <li>Lead Dev @ Startup Inc (2 ans)</li>
            </ul>
          </div>
          <div className="text-sm">
            <h4 className="font-semibold">Suggestions</h4>
            <p className="mt-1 text-muted-foreground">Pensez à mentionner vos soft skills et les projets personnels pertinents.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
