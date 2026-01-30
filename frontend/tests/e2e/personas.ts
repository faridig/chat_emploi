/**
 * Personas de test basées sur le PRD.md
 * Ces personas sont utilisées pour les tests utilisateur réels automatisés
 */

export interface Persona {
  id: string;
  name: string;
  description: string;
  cvFile: string;
  profileData: {
    skills: string[];
    experienceYears: number;
    educationLevel: string;
    targetRole: string;
    targetLocation: string;
    salaryExpectation?: string;
    remotePreference: boolean;
  };
  testScenarios: {
    searchFilters: {
      location: string;
      contractTypes: string[];
      remoteOk: boolean;
      publicationMaxDays: number;
    };
    expectedMatches: {
      minScore: number;
      minCount: number;
      expectedKeywords: string[];
    };
    letterCustomization: {
      preferredTone: 'professional' | 'enthusiastic' | 'formal';
      highlightExperiences: string[];
    };
  };
  metrics: {
    expectedSessionTime: number; // en minutes
    expectedMatchRate: number; // 0-1
    expectedLetterQuality: number; // 0-1
  };
}

export const personas: Record<string, Persona> = {
  julien: {
    id: 'julien',
    name: 'Julien',
    description: '28 ans, ancien commercial en reconversion vers développeur web',
    cvFile: 'julien_reconversion_commercial_dev.pdf',
    profileData: {
      skills: ['communication', 'relation client', 'gestion de projet', 'Python (débutant)', 'HTML/CSS (débutant)'],
      experienceYears: 5,
      educationLevel: 'bac+3',
      targetRole: 'développeur web junior',
      targetLocation: 'Paris',
      salaryExpectation: '35k-40k',
      remotePreference: true
    },
    testScenarios: {
      searchFilters: {
        location: 'Paris',
        contractTypes: ['CDI', 'CDD', 'Stage'],
        remoteOk: true,
        publicationMaxDays: 30
      },
      expectedMatches: {
        minScore: 0.6,
        minCount: 3,
        expectedKeywords: ['junior', 'formation', 'accompagnement', 'débutant']
      },
      letterCustomization: {
        preferredTone: 'enthusiastic',
        highlightExperiences: ['communication', 'relation client', 'gestion de projet']
      }
    },
    metrics: {
      expectedSessionTime: 25,
      expectedMatchRate: 0.7,
      expectedLetterQuality: 0.8
    }
  },

  sophie: {
    id: 'sophie',
    name: 'Sophie',
    description: '45 ans, cadre senior avec 20 ans d\'expérience en gestion de projet',
    cvFile: 'sophie_cadre_senior_gestion_projet.pdf',
    profileData: {
      skills: ['gestion de projet', 'leadership', 'stratégie', 'budget', 'équipe', 'agile'],
      experienceYears: 20,
      educationLevel: 'bac+5',
      targetRole: 'directrice d\'équipe',
      targetLocation: 'Lyon',
      salaryExpectation: '65k-80k',
      remotePreference: false
    },
    testScenarios: {
      searchFilters: {
        location: 'Lyon',
        contractTypes: ['CDI'],
        remoteOk: false,
        publicationMaxDays: 30
      },
      expectedMatches: {
        minScore: 0.75,
        minCount: 2,
        expectedKeywords: ['senior', 'expérience', 'management', 'stratégie']
      },
      letterCustomization: {
        preferredTone: 'professional',
        highlightExperiences: ['gestion de projet', 'leadership', 'stratégie']
      }
    },
    metrics: {
      expectedSessionTime: 20,
      expectedMatchRate: 0.8,
      expectedLetterQuality: 0.9
    }
  },

  lea: {
    id: 'lea',
    name: 'Léa',
    description: '22 ans, jeune diplômée en marketing avec peu d\'expérience',
    cvFile: 'lea_jeune_diplomee_marketing.pdf',
    profileData: {
      skills: ['marketing digital', 'réseaux sociaux', 'analyse de données', 'créativité', 'anglais courant'],
      experienceYears: 0.5,
      educationLevel: 'master',
      targetRole: 'chargée de marketing junior',
      targetLocation: 'Bordeaux',
      salaryExpectation: '30k-35k',
      remotePreference: true
    },
    testScenarios: {
      searchFilters: {
        location: 'Bordeaux',
        contractTypes: ['CDI', 'CDD', 'Stage'],
        remoteOk: true,
        publicationMaxDays: 30
      },
      expectedMatches: {
        minScore: 0.65,
        minCount: 4,
        expectedKeywords: ['junior', 'diplômé', 'formation', 'début de carrière']
      },
      letterCustomization: {
        preferredTone: 'enthusiastic',
        highlightExperiences: ['marketing digital', 'réseaux sociaux', 'créativité']
      }
    },
    metrics: {
      expectedSessionTime: 30,
      expectedMatchRate: 0.75,
      expectedLetterQuality: 0.85
    }
  }
};

/**
 * Données de test pour les CVs mockés
 */
export const mockCVs = {
  julien: `JULIEN DUPONT
Ancien Commercial en Reconversion vers le Développement Web

EXPÉRIENCE PROFESSIONNELLE
Commercial B2B - Tech Solutions SA (2019-2024)
- Développement du portefeuille clients (+30% en 3 ans)
- Présentation de solutions techniques aux clients
- Formation continue en développement web (Python, JavaScript)

COMPÉTENCES
- Communication et relation client
- Gestion de projet agile
- Python (formation en cours)
- HTML/CSS/JavaScript (bases)
- Anglais professionnel

FORMATION
Licence Commerce International - Université Paris (2016-2019)
Formation Développeur Web - OpenClassrooms (2024-en cours)`,

  sophie: `SOPHIE MARTIN
Directrice de Projet Senior - 20 ans d'expérience

EXPÉRIENCE PROFESSIONNELLE
Directrice de Projet - Grand Groupe International (2010-2024)
- Management d'équipes de 15+ personnes
- Budgets de 2M€+
- Implémentation de méthodologies Agile/Scrum

Chef de Projet - Entreprise Tech (2004-2010)
- Lancement de nouveaux produits digitaux
- Coordination d'équipes pluridisciplinaires

COMPÉTENCES
- Gestion de projet (PMP certifié)
- Leadership et management
- Stratégie d'entreprise
- Budget et planification
- Transformation digitale

FORMATION
MBA Management - HEC Paris (2002-2004)
Master Informatique - École Polytechnique (1998-2002)`,

  lea: `LÉA PETIT
Jeune Diplômée en Marketing Digital

FORMATION
Master Marketing Digital - Université de Bordeaux (2021-2023)
- Spécialisation en marketing des réseaux sociaux
- Mémoire: "L'impact du contenu vidéo sur l'engagement"

Licence Communication - Université de Bordeaux (2018-2021)

EXPÉRIENCE
Stage Marketing Digital - Startup Locale (6 mois, 2023)
- Gestion des réseaux sociaux (+40% d'engagement)
- Création de contenu visuel
- Analyse des données d'audience

COMPÉTENCES
- Marketing digital et réseaux sociaux
- Création de contenu (Canva, Adobe Creative Suite)
- Analyse de données (Google Analytics)
- Anglais courant (TOEIC 850)
- Créativité et adaptabilité`
};

/**
 * Données de test pour les offres mockées
 */
export const mockOffers = [
  {
    id: 'offer_tech_junior_1',
    title: 'Développeur Web Junior',
    company: 'Startup Tech Paris',
    location: 'Paris (75)',
    contract: 'CDI',
    description: 'Nous recherchons un développeur web junior pour rejoindre notre équipe. Formation offerte, environnement bienveillant pour les personnes en reconversion.',
    requirements: 'Bases en HTML/CSS/JavaScript, motivation et envie d\'apprendre',
    salary: '35k-40k',
    remote: true
  },
  {
    id: 'offer_tech_junior_2',
    title: 'Développeur Full-Stack Junior',
    company: 'Agence Web',
    location: 'Paris (75)',
    contract: 'CDD',
    description: 'Poste idéal pour un développeur débutant souhaitant monter en compétences sur des projets variés.',
    requirements: 'Connaissances en Python ou JavaScript, esprit d\'équipe',
    salary: '33k-38k',
    remote: true
  },
  {
    id: 'offer_manager_senior_1',
    title: 'Directrice d\'Équipe IT',
    company: 'Grand Groupe',
    location: 'Lyon (69)',
    contract: 'CDI',
    description: 'Nous recherchons une directrice d\'équipe expérimentée pour manager notre département IT de 20 personnes.',
    requirements: 'Minimum 10 ans d\'expérience en management, certification PMP appréciée',
    salary: '70k-85k',
    remote: false
  },
  {
    id: 'offer_marketing_junior_1',
    title: 'Chargée de Marketing Digital Junior',
    company: 'Agence de Communication',
    location: 'Bordeaux (33)',
    contract: 'CDI',
    description: 'Poste idéal pour une jeune diplômée motivée par le marketing digital et les réseaux sociaux.',
    requirements: 'Formation en marketing, maîtrise des réseaux sociaux, créativité',
    salary: '30k-35k',
    remote: true
  },
  {
    id: 'offer_marketing_junior_2',
    title: 'Community Manager',
    company: 'Marque Lifestyle',
    location: 'Bordeaux (33)',
    contract: 'CDD',
    description: 'Gestion des réseaux sociaux et création de contenu pour une marque jeune et dynamique.',
    requirements: 'Excellente maîtrise des réseaux sociaux, sens créatif',
    salary: '28k-32k',
    remote: true
  }
];

/**
 * Métriques collectées pendant les tests
 */
export interface TestMetrics {
  personaId: string;
  startTime: number;
  endTime: number;
  totalTime: number; // en secondes
  stepsCompleted: string[];
  matchesFound: number;
  averageMatchScore: number;
  letterGenerated: boolean;
  letterQualityScore?: number;
  errorsEncountered: string[];
  success: boolean;
}

/**
 * Configuration des tests
 */
export const testConfig = {
  baseURL: 'http://localhost:3000',
  timeout: 60000, // 60 secondes par test
  slowMo: 100, // ralentir les actions pour visibilité
  headless: process.env.CI ? true : false, // headless en CI, visible localement
  viewport: { width: 1280, height: 720 },
  storageState: 'playwright/.auth/user.json'
};
