import { JobOffer } from '@/types/job-offer';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { MapPin, Briefcase, Clock } from 'lucide-react';

interface JobOfferCardProps {
  offer: JobOffer;
}

function getMatchScoreColor(score: number): string {
  if (score > 0.85) return 'from-green-500 to-emerald-500';
  if (score > 0.7) return 'from-blue-500 to-cyan-500';
  return 'from-amber-500 to-yellow-500';
}

export function JobOfferCard({ offer }: JobOfferCardProps) {
  const scorePercent = Math.round(offer.matchScore * 100);

  return (
    <Card
      className="flex flex-col justify-between transition-all hover:shadow-lg hover:-translate-y-1"
      data-testid="offer-card"
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg">{offer.title}</CardTitle>
          <div
            className={cn(
              'flex items-center justify-center rounded-full bg-gradient-to-br p-0.5 text-white shadow-md',
              getMatchScoreColor(offer.matchScore)
            )}
          >
            <span className="rounded-full bg-surface px-2 py-1 text-xs font-bold text-text-primary">
              {scorePercent}%
            </span>
          </div>
        </div>
        <p className="text-sm font-medium text-text-secondary">{offer.company}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-text-secondary">
          <MapPin size={14} /> <span>{offer.location}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-text-secondary">
          <Briefcase size={14} /> <span>{offer.contractType}</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {offer.skills.slice(0, 3).map((skill) => (
            <Badge key={skill} variant="secondary">{skill}</Badge>
          ))}
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="outline" className="w-full">
          Voir détails
        </Button>
      </CardFooter>
    </Card>
  );
}
