"""Script de chargement des données de test réalistes."""

import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Ajouter le chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.models import AnonymizedProfile, Application, Base, JobOffer, User


def load_test_data():
    """Charge des données de test réalistes dans la base de données."""

    # URL de la base de données de test
    database_url = "sqlite:///test_chat_emploi.db"
    engine = create_engine(database_url)

    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        # Nettoyer les données existantes
        session.query(Application).delete()
        session.query(JobOffer).delete()
        session.query(AnonymizedProfile).delete()
        session.query(User).delete()
        session.commit()

        # Créer des utilisateurs de test
        users = [
            User(
                id=str(uuid.uuid4()),
                settings={"theme": "light", "notifications": True},
                metadata_={"source": "test_data", "persona": "julien"},
            ),
            User(
                id=str(uuid.uuid4()),
                settings={"theme": "dark", "notifications": True},
                metadata_={"source": "test_data", "persona": "sophie"},
            ),
            User(
                id=str(uuid.uuid4()),
                settings={"theme": "light", "notifications": False},
                metadata_={"source": "test_data", "persona": "lea"},
            ),
        ]

        session.add_all(users)
        session.commit()

        # Créer des profils anonymisés
        profiles = [
            AnonymizedProfile(
                id=str(uuid.uuid4()),
                user_id=users[0].id,
                original_hash="hash_julien_cv_123",
                anonymized_path="/data/profiles/julien_anonymized.pdf",
                analysis_json={
                    "skills": ["négociation", "relation client", "CRM", "SaaS"],
                    "experience_years": 8,
                    "sectors": ["technologie", "SaaS"],
                    "target_position": "product management",
                },
                extracted_data={
                    "original_text": """Julien Dupont
Commercial B2B - 8 ans d'expérience
Compétences: négociation, relation client, CRM
Secteur: technologie, SaaS
Recherche: transition vers product management""",
                    "anonymized_text": """[Profil 1]
Commercial B2B - 8 ans d'expérience
Compétences: négociation, relation client, CRM
Secteur: technologie
Recherche: transition vers management produit""",
                },
            ),
            AnonymizedProfile(
                id=str(uuid.uuid4()),
                user_id=users[1].id,
                original_hash="hash_sophie_cv_456",
                anonymized_path="/data/profiles/sophie_anonymized.pdf",
                analysis_json={
                    "skills": [
                        "stratégie digitale",
                        "analytics",
                        "management",
                        "e-commerce",
                    ],
                    "experience_years": 12,
                    "sectors": ["e-commerce", "retail"],
                    "target_position": "CMO",
                },
                extracted_data={
                    "original_text": """Sophie Martin
Directrice Marketing - 12 ans d'expérience
Compétences: stratégie digitale, analytics, team management
Secteur: e-commerce, retail
Recherche: poste de CMO dans scale-up""",
                    "anonymized_text": """[Profil 2]
Directrice Marketing - 12 ans d'expérience
Compétences: stratégie digitale, analytics, management d'équipe
Secteur: e-commerce
Recherche: poste de direction marketing""",
                },
            ),
        ]

        session.add_all(profiles)
        session.commit()

        # Créer des offres d'emploi réalistes
        job_offers = [
            JobOffer(
                id="FT12345",
                source="france_travail",
                raw_data={
                    "title": "Product Manager",
                    "company": "TechScale Inc.",
                    "location": "Paris (75)",
                    "description": """Recherche Product Manager pour développer notre suite SaaS B2B.
Responsabilités:
- Définir la roadmap produit
- Travailler avec les équipes engineering et design
- Analyser les données utilisateurs
- Prioriser les features

Profil recherché:
- 5+ ans en product management
- Expérience SaaS B2B
- Compétences techniques (APIs, data)
- Anglais courant""",
                    "contract_type": "CDI",
                    "salary_range": "60k-80k",
                    "skills": [
                        "product management",
                        "SaaS",
                        "B2B",
                        "roadmap",
                        "analytics",
                    ],
                },
                title="Product Manager",
                company="TechScale Inc.",
                location="Paris (75)",
                contract_type="CDI",
                publication_date=date.today(),
                description="""Recherche Product Manager pour développer notre suite SaaS B2B.
Responsabilités:
- Définir la roadmap produit
- Travailler avec les équipes engineering et design
- Analyser les données utilisateurs
- Prioriser les features

Profil recherché:
- 5+ ans en product management
- Expérience SaaS B2B
- Compétences techniques (APIs, data)
- Anglais courant""",
                requirements="5+ ans en product management, Expérience SaaS B2B, Compétences techniques (APIs, data), Anglais courant",
                expires_at=datetime.now() + timedelta(days=30),
            ),
            JobOffer(
                id="FT12346",
                source="france_travail",
                raw_data={
                    "title": "Chief Marketing Officer",
                    "company": "EcomGrowth",
                    "location": "Lyon (69)",
                    "description": """CMO pour scale-up e-commerce en forte croissance.
Mission:
- Définir la stratégie marketing
- Manager une équipe de 10 personnes
- Optimiser le CAC et LTV
- Développer les partenariats

Profil:
- 10+ ans en marketing digital
- Expérience e-commerce
- Track record de croissance
- Leadership avéré""",
                    "contract_type": "CDI",
                    "salary_range": "100k-130k",
                    "skills": [
                        "marketing digital",
                        "e-commerce",
                        "growth",
                        "team management",
                        "strategy",
                    ],
                },
                title="Chief Marketing Officer",
                company="EcomGrowth",
                location="Lyon (69)",
                contract_type="CDI",
                publication_date=date.today(),
                description="""CMO pour scale-up e-commerce en forte croissance.
Mission:
- Définir la stratégie marketing
- Manager une équipe de 10 personnes
- Optimiser le CAC et LTV
- Développer les partenariats

Profil:
- 10+ ans en marketing digital
- Expérience e-commerce
- Track record de croissance
- Leadership avéré""",
                requirements="10+ ans en marketing digital, Expérience e-commerce, Track record de croissance, Leadership avéré",
                expires_at=datetime.now() + timedelta(days=30),
            ),
            JobOffer(
                id="FT12347",
                source="france_travail",
                raw_data={
                    "title": "Business Developer",
                    "company": "SaaS Solutions",
                    "location": "Télétravail",
                    "description": """Business Developer pour éditeur de logiciel.
Rôle:
- Prospecter de nouveaux clients
- Négocier les contrats
- Développer le réseau de partenaires
- Atteindre les objectifs de vente

Compétences requises:
- Expérience commerciale B2B
- Connaissance du secteur tech
- Excellente communication
- Autonomie et proactivité""",
                    "contract_type": "CDI",
                    "salary_range": "50k-70k + variable",
                    "skills": [
                        "business development",
                        "B2B sales",
                        "negotiation",
                        "SaaS",
                        "prospecting",
                    ],
                },
                title="Business Developer",
                company="SaaS Solutions",
                location="Télétravail",
                contract_type="CDI",
                publication_date=date.today(),
                description="""Business Developer pour éditeur de logiciel.
Rôle:
- Prospecter de nouveaux clients
- Négocier les contrats
- Développer le réseau de partenaires
- Atteindre les objectifs de vente

Compétences requises:
- Expérience commerciale B2B
- Connaissance du secteur tech
- Excellente communication
- Autonomie et proactivité""",
                requirements="Expérience commerciale B2B, Connaissance du secteur tech, Excellente communication, Autonomie et proactivité",
                expires_at=datetime.now() + timedelta(days=30),
            ),
        ]

        session.add_all(job_offers)
        session.commit()

        # Créer des candidatures de test
        applications = [
            Application(
                id=str(uuid.uuid4()),
                user_id=users[0].id,
                profile_id=profiles[0].id,
                offer_id=job_offers[0].id,
                status="applied",
                applied_date=date.today(),
                cover_letter_path="/data/cover_letters/julien_pm_letter.pdf",
                notes="CV bien adapté au poste, bonne correspondance de compétences",
                metrics={
                    "match_score": 0.85,
                    "skills_match": 0.9,
                    "experience_match": 0.8,
                },
            ),
            Application(
                id=str(uuid.uuid4()),
                user_id=users[1].id,
                profile_id=profiles[1].id,
                offer_id=job_offers[1].id,
                status="interview",
                applied_date=date.today() - timedelta(days=7),
                cover_letter_path="/data/cover_letters/sophie_cmo_letter.pdf",
                notes="Entretien prévu la semaine prochaine, bonne préparation nécessaire",
                interview_date=datetime.now() + timedelta(days=3),
                metrics={
                    "match_score": 0.92,
                    "skills_match": 0.95,
                    "experience_match": 0.9,
                },
            ),
        ]

        session.add_all(applications)
        session.commit()

        print("✅ Données de test chargées:")
        print(f"   - {len(users)} utilisateurs")
        print(f"   - {len(profiles)} profils")
        print(f"   - {len(job_offers)} offres d'emploi")
        print(f"   - {len(applications)} candidatures")


if __name__ == "__main__":
    load_test_data()
