'use client';

import React from 'react';
import { useSessionStore } from '@/stores/session-store';
import { JobOfferCard } from '@/components/feature/job-offer-card';
import { Skeleton } from '@/components/ui/skeleton';
import { JobOffer } from '@/types/job-offer';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

// Mock data for demonstration purposes
const MOCK_OFFERS: JobOffer[] = [
    { id: '1', title: 'Développeur Frontend', company: 'Tech Solutions', location: 'Paris', matchScore: 0.92, contractType: 'CDI', skills: ['React', 'TypeScript'], publishedAt: '' , description: ''},
    { id: '2', title: 'Développeur Backend Python', company: 'Data Minds', location: 'Lyon', matchScore: 0.87, contractType: 'CDI', skills: ['Python', 'Django'], publishedAt: '' , description: ''},
    { id: '3', title: 'Product Manager', company: 'Innovate Co', location: 'Télétravail', matchScore: 0.75, contractType: 'CDD', skills: ['Agile', 'Jira'], publishedAt: '' , description: ''},
    { id: '4', title: 'UI/UX Designer', company: 'Creative Hub', location: 'Bordeaux', matchScore: 0.68, contractType: 'CDI', skills: ['Figma', 'UX Research'], publishedAt: '' , description: ''},
];

function JobOfferSkeleton() {
    return (
        <div className="flex flex-col space-y-3" data-testid="skeleton-card">
            <Skeleton className="h-[125px] w-full rounded-xl" />
            <div className="space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
            </div>
        </div>
    )
}

export default function SearchPage() {
    // const { isSearching, jobOffers } = useSessionStore();
    const isSearching = false; // Mock
    const jobOffers = MOCK_OFFERS; // Mock

    return (
        <div className="flex h-full">
            <div className="flex-1 overflow-y-auto p-6">
                <header className="mb-6">
                    <h1 className="text-2xl font-bold">Offres qui pourraient vous correspondre</h1>
                    <p className="text-muted-foreground">Basé sur votre profil et vos objectifs</p>
                </header>

                {/* Filters */}
                <div className="mb-6 flex flex-wrap items-center gap-4">
                    <Select>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Localisation" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="paris">Paris</SelectItem>
                            <SelectItem value="lyon">Lyon</SelectItem>
                        </SelectContent>
                    </Select>
                    {/* Add more filters here */}
                    <Button>Actualiser</Button>
                </div>

                {/* Results */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {isSearching ? (
                        Array.from({ length: 6 }).map((_, i) => <JobOfferSkeleton key={i} />)
                    ) : jobOffers.length > 0 ? (
                        jobOffers.map(offer => <JobOfferCard key={offer.id} offer={offer} />)
                    ) : (
                        <div className="col-span-full text-center">
                            <p>Aucune offre exacte aujourd'hui. Essayez d'élargir vos critères ?</p>
                        </div>
                    )}
                </div>
            </div>
            {/* Context Panel can go here if needed in this view */}
        </div>
    );
}
