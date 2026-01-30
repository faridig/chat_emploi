export interface JobOffer {
  id: string;
  title: string;
  description: string;
  company: string;
  location: string;
  skills: string[];
  contractType: string;
  publishedAt: string;
  matchScore: number;
}
