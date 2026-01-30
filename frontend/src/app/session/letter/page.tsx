'use client';
import { LetterControls } from "@/components/feature/letter-controls";
import { LetterPreview } from "@/components/feature/letter-preview";
import { Button } from "@/components/ui/button";
import { Download, Copy, RefreshCw } from "lucide-react";

const MOCK_LETTER_CONTENT = `Madame, Monsieur,

Vivement intéressé par le poste de [Poste] chez [Entreprise], je vous soumets ma candidature. Mon expérience en [Domaine] et ma maîtrise de [Compétence clé] correspondent parfaitement aux exigences de votre offre.

Lors de ma précédente mission chez [Ancienne entreprise], j'ai pu [Réalisation chiffrée]. Je suis convaincu que mon profil saura contribuer au succès de vos projets.

Je serais ravi de vous exposer plus en détail mes motivations lors d'un entretien.`;

export default function LetterPage() {
    return (
        <div className="flex h-full flex-col">
            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 overflow-hidden">
                <div className="md:col-span-2 h-full overflow-y-auto">
                    <LetterPreview content={MOCK_LETTER_CONTENT} />
                </div>
                <div className="h-full overflow-y-auto">
                    <LetterControls />
                </div>
            </div>
            <footer className="flex items-center justify-end gap-4 border-t p-4">
                <Button variant="ghost">
                    <RefreshCw className="mr-2" />
                    Générer une alternative
                </Button>
                <Button variant="secondary">
                    <Copy className="mr-2" />
                    Copier le texte
                </Button>
                <Button>
                    <Download className="mr-2" />
                    Télécharger PDF
                </Button>
            </footer>
        </div>
    );
}
