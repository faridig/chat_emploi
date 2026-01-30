"""Annotated test dataset for RAG system quality evaluation.

This dataset contains realistic job offers from France Travail and CV profiles
with manual annotations for expected matches and similarity scores.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class AnnotatedJobOffer:
    """Job offer with annotation for expected matches."""

    id: str
    title: str
    description: str
    company: str
    location: str
    skills: list[str]
    experience_level: str
    salary_range: dict[str, Any] = None
    metadata: dict[str, Any] = None
    # Annotation fields
    expected_cv_match: str = None  # ID of CV that should match
    expected_score_min: float = 0.7  # Minimum expected similarity score
    expected_matching_skills: list[str] = None  # Skills expected to match


@dataclass
class AnnotatedCVProfile:
    """CV profile with annotation for expected job matches."""

    id: str
    skills: list[str]
    experiences: list[dict[str, Any]]
    education: list[dict[str, Any]]
    summary: str = None
    metadata: dict[str, Any] = None
    # Annotation fields
    expected_job_matches: list[str] = None  # IDs of jobs that should match
    expected_scores_min: list[float] = None  # Minimum expected scores


# ============================================================================
# ANNOTATED TEST DATASET
# ============================================================================

# CV Profiles (realistic examples)
CV_PROFILES = [
    AnnotatedCVProfile(
        id="cv_dev_python_junior",
        skills=["python", "django", "postgresql", "git", "docker", "html", "css"],
        experiences=[
            {
                "title": "Développeur Python Junior",
                "company": "StartupTech",
                "duration": "1 an",
                "description": "Développement features backend Django",
            },
            {
                "title": "Stagiaire Développeur Web",
                "company": "WebAgency",
                "duration": "6 mois",
                "description": "Développement sites web responsive",
            },
        ],
        education=[
            {
                "degree": "Licence Informatique",
                "institution": "Université Paris 8",
                "year": "2023",
            },
            {"degree": "BTS SIO", "institution": "Lycée Technique", "year": "2021"},
        ],
        summary="Développeur Python junior passionné par le web, 1 an d'expérience Django",
        metadata={"language": "fr", "experience_years": 1, "status": "junior"},
        expected_job_matches=["job_python_junior", "job_web_dev"],
        expected_scores_min=[0.75, 0.70],
    ),
    AnnotatedCVProfile(
        id="cv_data_scientist_senior",
        skills=[
            "python",
            "machine learning",
            "deep learning",
            "sql",
            "pandas",
            "scikit-learn",
            "tensorflow",
            "aws",
            "docker",
        ],
        experiences=[
            {
                "title": "Data Scientist Senior",
                "company": "DataCorp",
                "duration": "4 ans",
                "description": "Développement modèles ML pour prévision ventes",
            },
            {
                "title": "Data Analyst",
                "company": "AnalyticsLab",
                "duration": "2 ans",
                "description": "Analyse données business intelligence",
            },
        ],
        education=[
            {
                "degree": "Master Data Science",
                "institution": "École Polytechnique",
                "year": "2018",
            },
            {
                "degree": "Licence Mathématiques",
                "institution": "Université Paris-Saclay",
                "year": "2016",
            },
        ],
        summary="Data Scientist senior avec 6 ans d'expérience en ML et analyse données",
        metadata={"language": "fr", "experience_years": 6, "status": "senior"},
        expected_job_matches=["job_data_scientist_senior", "job_ml_engineer"],
        expected_scores_min=[0.80, 0.75],
    ),
    AnnotatedCVProfile(
        id="cv_devops_midlevel",
        skills=[
            "docker",
            "kubernetes",
            "aws",
            "terraform",
            "python",
            "bash",
            "jenkins",
            "gitlab",
            "monitoring",
        ],
        experiences=[
            {
                "title": "DevOps Engineer",
                "company": "CloudCompany",
                "duration": "3 ans",
                "description": "Infrastructure cloud et pipelines CI/CD",
            },
            {
                "title": "Administrateur Système",
                "company": "ITServices",
                "duration": "2 ans",
                "description": "Gestion serveurs et réseaux",
            },
        ],
        education=[
            {
                "degree": "Master Réseaux et Télécoms",
                "institution": "Télécom Paris",
                "year": "2019",
            }
        ],
        summary="DevOps Engineer avec expertise cloud et automation",
        metadata={"language": "fr", "experience_years": 5, "status": "mid-level"},
        expected_job_matches=["job_devops_engineer", "job_cloud_engineer"],
        expected_scores_min=[0.78, 0.72],
    ),
    AnnotatedCVProfile(
        id="cv_fullstack_react",
        skills=[
            "javascript",
            "react",
            "node.js",
            "typescript",
            "python",
            "mongodb",
            "docker",
            "aws",
            "git",
        ],
        experiences=[
            {
                "title": "Développeur Fullstack",
                "company": "DigitalAgency",
                "duration": "2 ans",
                "description": "Développement applications React/Node.js",
            },
            {
                "title": "Développeur Frontend",
                "company": "WebStudio",
                "duration": "1 an",
                "description": "Développement interfaces React",
            },
        ],
        education=[
            {
                "degree": "Bootcamp Développement Web",
                "institution": "Le Wagon",
                "year": "2021",
            },
            {
                "degree": "Licence Design Graphique",
                "institution": "École des Arts",
                "year": "2020",
            },
        ],
        summary="Développeur Fullstack spécialisé React/Node.js avec background design",
        metadata={"language": "fr", "experience_years": 3, "status": "mid-level"},
        expected_job_matches=["job_fullstack_react", "job_frontend_senior"],
        expected_scores_min=[0.76, 0.70],
    ),
]

# Job Offers (realistic France Travail examples)
JOB_OFFERS = [
    AnnotatedJobOffer(
        id="job_python_junior",
        title="Développeur Python Junior",
        description="Nous recherchons un développeur Python junior pour rejoindre notre équipe "
        "et participer au développement de nos applications web. Missions: "
        "développement features backend avec Django, maintenance code, "
        "participation aux revues de code.",
        company="TechStartup",
        location="Paris (75)",
        skills=["python", "django", "postgresql", "git", "docker"],
        experience_level="Junior",
        salary_range={"min": 35000, "max": 42000, "currency": "EUR"},
        metadata={
            "source": "france_travail",
            "contract_type": "CDI",
            "remote": "partiel",
        },
        expected_cv_match="cv_dev_python_junior",
        expected_score_min=0.75,
        expected_matching_skills=["python", "django", "postgresql", "git", "docker"],
    ),
    AnnotatedJobOffer(
        id="job_data_scientist_senior",
        title="Data Scientist Senior",
        description="Poste de Data Scientist senior pour développer des modèles de machine learning "
        "appliqués à la finance. Responsabilités: conception et déploiement modèles ML, "
        "analyse données complexes, collaboration avec équipes métier.",
        company="FinTechBank",
        location="Lyon (69)",
        skills=[
            "python",
            "machine learning",
            "deep learning",
            "sql",
            "statistics",
            "aws",
            "docker",
        ],
        experience_level="Senior",
        salary_range={"min": 60000, "max": 80000, "currency": "EUR"},
        metadata={"source": "france_travail", "contract_type": "CDI", "remote": "oui"},
        expected_cv_match="cv_data_scientist_senior",
        expected_score_min=0.80,
        expected_matching_skills=[
            "python",
            "machine learning",
            "deep learning",
            "sql",
            "aws",
            "docker",
        ],
    ),
    AnnotatedJobOffer(
        id="job_devops_engineer",
        title="DevOps Engineer",
        description="Ingénieur DevOps pour gérer notre infrastructure cloud AWS et automatiser "
        "nos processus de déploiement. Technologies: Docker, Kubernetes, Terraform, "
        "CI/CD, monitoring.",
        company="SaaSCompany",
        location="Remote",
        skills=["docker", "kubernetes", "aws", "terraform", "python", "bash", "ci/cd"],
        experience_level="Mid-level",
        salary_range={"min": 50000, "max": 65000, "currency": "EUR"},
        metadata={"source": "france_travail", "contract_type": "CDI", "remote": "full"},
        expected_cv_match="cv_devops_midlevel",
        expected_score_min=0.78,
        expected_matching_skills=[
            "docker",
            "kubernetes",
            "aws",
            "terraform",
            "python",
            "bash",
        ],
    ),
    AnnotatedJobOffer(
        id="job_fullstack_react",
        title="Développeur Fullstack React/Node.js",
        description="Développeur Fullstack pour créer des applications web modernes avec React "
        "frontend et Node.js backend. Stack: React, TypeScript, Node.js, MongoDB, Docker.",
        company="DigitalProduct",
        location="Bordeaux (33)",
        skills=[
            "javascript",
            "react",
            "node.js",
            "typescript",
            "mongodb",
            "docker",
            "aws",
        ],
        experience_level="Mid-level",
        salary_range={"min": 45000, "max": 58000, "currency": "EUR"},
        metadata={
            "source": "france_travail",
            "contract_type": "CDI",
            "remote": "hybride",
        },
        expected_cv_match="cv_fullstack_react",
        expected_score_min=0.76,
        expected_matching_skills=[
            "javascript",
            "react",
            "node.js",
            "docker",
            "aws",
            "git",
        ],
    ),
    AnnotatedJobOffer(
        id="job_web_dev",
        title="Développeur Web",
        description="Développeur web polyvalent pour création sites et applications. "
        "Compétences requises: HTML, CSS, JavaScript, Python, bases de données.",
        company="WebAgency",
        location="Marseille (13)",
        skills=["html", "css", "javascript", "python", "sql", "git"],
        experience_level="Junior",
        salary_range={"min": 32000, "max": 38000, "currency": "EUR"},
        metadata={"source": "france_travail", "contract_type": "CDI", "remote": "non"},
        expected_cv_match="cv_dev_python_junior",
        expected_score_min=0.70,
        expected_matching_skills=["python", "git", "html", "css"],
    ),
    AnnotatedJobOffer(
        id="job_ml_engineer",
        title="Machine Learning Engineer",
        description="Ingénieur ML pour productionalisation modèles. Compétences: Python, "
        "MLOps, déploiement modèles, cloud computing.",
        company="AIStartup",
        location="Paris (75)",
        skills=["python", "machine learning", "docker", "aws", "mlops", "ci/cd"],
        experience_level="Senior",
        salary_range={"min": 55000, "max": 75000, "currency": "EUR"},
        metadata={
            "source": "france_travail",
            "contract_type": "CDI",
            "remote": "partiel",
        },
        expected_cv_match="cv_data_scientist_senior",
        expected_score_min=0.75,
        expected_matching_skills=["python", "machine learning", "docker", "aws"],
    ),
    AnnotatedJobOffer(
        id="job_cloud_engineer",
        title="Cloud Engineer",
        description="Ingénieur Cloud pour migration vers AWS. Technologies: AWS, Docker, "
        "Kubernetes, infrastructure as code.",
        company="EnterpriseCorp",
        location="Lille (59)",
        skills=["aws", "docker", "kubernetes", "terraform", "python", "networking"],
        experience_level="Mid-level",
        salary_range={"min": 48000, "max": 62000, "currency": "EUR"},
        metadata={"source": "france_travail", "contract_type": "CDI", "remote": "oui"},
        expected_cv_match="cv_devops_midlevel",
        expected_score_min=0.72,
        expected_matching_skills=["docker", "kubernetes", "aws", "terraform", "python"],
    ),
    AnnotatedJobOffer(
        id="job_frontend_senior",
        title="Développeur Frontend Senior React",
        description="Développeur Frontend senior React/TypeScript pour application complexe. "
        "Expertise React, state management, performance optimization.",
        company="ProductTech",
        location="Nantes (44)",
        skills=["javascript", "react", "typescript", "redux", "webpack", "testing"],
        experience_level="Senior",
        salary_range={"min": 52000, "max": 68000, "currency": "EUR"},
        metadata={
            "source": "france_travail",
            "contract_type": "CDI",
            "remote": "hybride",
        },
        expected_cv_match="cv_fullstack_react",
        expected_score_min=0.70,
        expected_matching_skills=["javascript", "react", "typescript"],
    ),
    # Negative test cases (should NOT match well)
    AnnotatedJobOffer(
        id="job_java_developer",
        title="Développeur Java Senior",
        description="Développeur Java Spring pour applications enterprise. "
        "Stack: Java, Spring Boot, Hibernate, Oracle, Maven.",
        company="BankCorp",
        location="Paris (75)",
        skills=["java", "spring", "hibernate", "oracle", "maven", "junit"],
        experience_level="Senior",
        salary_range={"min": 55000, "max": 70000, "currency": "EUR"},
        metadata={"source": "france_travail", "contract_type": "CDI", "remote": "non"},
        expected_cv_match=None,  # No good match in our CVs
        expected_score_min=0.3,  # Should be low similarity
        expected_matching_skills=[],  # No matching skills with our Python-focused CVs
    ),
    AnnotatedJobOffer(
        id="job_marketing_manager",
        title="Responsable Marketing Digital",
        description="Responsable marketing digital pour stratégie et campagnes. "
        "Compétences: SEO, réseaux sociaux, analytics, content marketing.",
        company="MarketingAgency",
        location="Paris (75)",
        skills=["marketing", "seo", "social media", "analytics", "content", "strategy"],
        experience_level="Senior",
        salary_range={"min": 45000, "max": 60000, "currency": "EUR"},
        metadata={
            "source": "france_travail",
            "contract_type": "CDI",
            "remote": "partiel",
        },
        expected_cv_match=None,  # No technical CV should match
        expected_score_min=0.2,  # Very low similarity expected
        expected_matching_skills=[],
    ),
]


# ============================================================================
# DATASET STATISTICS
# ============================================================================


def get_dataset_stats() -> dict[str, Any]:
    """Get statistics about the annotated dataset."""
    return {
        "cv_profiles": len(CV_PROFILES),
        "job_offers": len(JOB_OFFERS),
        "annotated_matches": sum(1 for job in JOB_OFFERS if job.expected_cv_match),
        "avg_skills_per_cv": sum(len(cv.skills) for cv in CV_PROFILES)
        / len(CV_PROFILES),
        "avg_skills_per_job": sum(len(job.skills) for job in JOB_OFFERS)
        / len(JOB_OFFERS),
        "skill_categories": {
            "python": sum(1 for cv in CV_PROFILES if "python" in cv.skills),
            "javascript": sum(1 for cv in CV_PROFILES if "javascript" in cv.skills),
            "docker": sum(1 for cv in CV_PROFILES if "docker" in cv.skills),
            "aws": sum(1 for cv in CV_PROFILES if "aws" in cv.skills),
            "machine_learning": sum(
                1 for cv in CV_PROFILES if "machine learning" in cv.skills
            ),
        },
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_cv_by_id(cv_id: str) -> AnnotatedCVProfile:
    """Get CV profile by ID."""
    for cv in CV_PROFILES:
        if cv.id == cv_id:
            return cv
    raise ValueError(f"CV with ID {cv_id} not found")


def get_job_by_id(job_id: str) -> AnnotatedJobOffer:
    """Get job offer by ID."""
    for job in JOB_OFFERS:
        if job.id == job_id:
            return job
    raise ValueError(f"Job with ID {job_id} not found")


def get_expected_matches_for_cv(cv_id: str) -> list[dict[str, Any]]:
    """Get expected job matches for a CV with minimum scores."""
    cv = get_cv_by_id(cv_id)
    matches = []

    for i, job_id in enumerate(cv.expected_job_matches or []):
        job = get_job_by_id(job_id)
        min_score = (
            cv.expected_scores_min[i]
            if cv.expected_scores_min and i < len(cv.expected_scores_min)
            else 0.7
        )

        matches.append(
            {
                "job_id": job_id,
                "job_title": job.title,
                "expected_score_min": min_score,
                "expected_matching_skills": job.expected_matching_skills,
            }
        )

    return matches


def get_expected_match_for_job(job_id: str) -> dict[str, Any]:
    """Get expected CV match for a job."""
    job = get_job_by_id(job_id)

    if not job.expected_cv_match:
        return None

    cv = get_cv_by_id(job.expected_cv_match)

    return {
        "cv_id": cv.id,
        "expected_score_min": job.expected_score_min,
        "expected_matching_skills": job.expected_matching_skills,
    }


if __name__ == "__main__":
    # Print dataset statistics
    stats = get_dataset_stats()
    print("=== RAG Test Dataset Statistics ===")
    print(f"CV Profiles: {stats['cv_profiles']}")
    print(f"Job Offers: {stats['job_offers']}")
    print(f"Annotated Matches: {stats['annotated_matches']}")
    print(f"Avg Skills per CV: {stats['avg_skills_per_cv']:.1f}")
    print(f"Avg Skills per Job: {stats['avg_skills_per_job']:.1f}")
    print("\nSkill Distribution in CVs:")
    for skill, count in stats["skill_categories"].items():
        print(f"  {skill}: {count}/{stats['cv_profiles']}")

    # Print example matches
    print("\n=== Example Expected Matches ===")
    for cv in CV_PROFILES[:2]:  # First 2 CVs
        matches = get_expected_matches_for_cv(cv.id)
        print(f"\nCV: {cv.id} ({cv.summary[:50]}...)")
        for match in matches:
            print(
                f"  → Job: {match['job_id']} (min score: {match['expected_score_min']})"
            )
