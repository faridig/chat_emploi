"""Test suite for RAG (Retrieval-Augmented Generation) core system.

This module implements TDD tests for the RAG system following the "Zero Debt"
strategy. Tests are written before any modifications to the implementation.
"""

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from rag.core import (
    CollectionType,
    CVProfile,
    EmbeddingModel,
    JobOffer,
    MatchResult,
    RAGConfig,
    RAGError,
    RAGSystem,
)
from services.embedding.embedding_service import EmbeddingService
from services.vector_store.vector_store_service import VectorStoreService

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_embedding_service():
    """Mock EmbeddingService."""
    mock = Mock(spec=EmbeddingService)
    mock.embed_text.return_value = [0.1] * 768  # Mock embedding vector
    mock.embed_text_with_cache.return_value = [0.1] * 768
    mock.load_embeddings_cache.return_value = {}
    mock.embedding_cache = {}  # Add attribute
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock VectorStoreService."""
    mock = Mock(spec=VectorStoreService)

    # Mock collection stats
    mock.get_collection_stats.return_value = {"count": 10}

    # Mock query results
    mock.query_similarity.return_value = {
        "ids": [["job_1", "job_2", "job_3"]],
        "distances": [[0.3, 0.5, 0.7]],
        "metadatas": [
            [
                {
                    "title": "Développeur Python",
                    "company": "TechCorp",
                    "location": "Paris",
                    "skills": "python,django,postgresql",
                    "experience_level": "Mid-level",
                },
                {
                    "title": "Data Scientist",
                    "company": "DataLab",
                    "location": "Lyon",
                    "skills": "python,machine learning,sql",
                    "experience_level": "Senior",
                },
                {
                    "title": "DevOps Engineer",
                    "company": "CloudTech",
                    "location": "Remote",
                    "skills": "docker,kubernetes,aws",
                    "experience_level": "Mid-level",
                },
            ]
        ],
        "documents": [
            [
                "Title: Développeur Python\nCompany: TechCorp\nLocation: Paris\nDescription: Développement applications Python\nRequired Skills: python, django, postgresql\nExperience Level: Mid-level",
                "Title: Data Scientist\nCompany: DataLab\nLocation: Lyon\nDescription: Analyse données machine learning\nRequired Skills: python, machine learning, sql\nExperience Level: Senior",
                "Title: DevOps Engineer\nCompany: CloudTech\nLocation: Remote\nDescription: Infrastructure cloud et CI/CD\nRequired Skills: docker, kubernetes, aws\nExperience Level: Mid-level",
            ]
        ],
    }

    # Mock add_embeddings
    mock.add_embeddings.return_value = True

    # Mock get_or_create_collection
    mock.get_or_create_collection.return_value = Mock()

    return mock


@pytest.fixture
def sample_job_offer():
    """Sample job offer for testing."""
    return JobOffer(
        id="job_123",
        title="Développeur Python Senior",
        description="Développement d'applications Python avec Django et FastAPI",
        company="StartupTech",
        location="Paris",
        skills=["python", "django", "fastapi", "postgresql", "docker"],
        experience_level="Senior",
        salary_range={"min": 50000, "max": 70000, "currency": "EUR"},
        metadata={"source": "france_travail", "contract_type": "CDI"},
    )


@pytest.fixture
def sample_cv_profile():
    """Sample CV profile for testing."""
    return CVProfile(
        id="cv_456",
        skills=["python", "django", "postgresql", "docker", "git"],
        experiences=[
            {
                "title": "Développeur Python",
                "company": "PreviousCorp",
                "duration": "2 ans",
                "description": "Développement backend avec Django",
            },
            {
                "title": "Stagiaire Développeur",
                "company": "InternTech",
                "duration": "6 mois",
                "description": "Développement fonctionnalités Python",
            },
        ],
        education=[
            {
                "degree": "Master Informatique",
                "institution": "Université Paris",
                "year": "2022",
            },
            {
                "degree": "Licence Informatique",
                "institution": "Université Lyon",
                "year": "2020",
            },
        ],
        summary="Développeur Python passionné avec 2 ans d'expérience en développement web",
        metadata={"language": "fr", "experience_years": 2},
    )


@pytest.fixture
def rag_system(mock_embedding_service, mock_vector_store):
    """RAGSystem with mocked dependencies."""
    with (
        patch("rag.core.EmbeddingService", return_value=mock_embedding_service),
        patch("rag.core.VectorStoreService", return_value=mock_vector_store),
    ):
        system = RAGSystem(
            embedding_api_key="test_api_key",
            config=RAGConfig(
                persist_directory=Path("./test_data/vector_store"),
                similarity_threshold=0.7,
            ),
        )
        system.embedding_service = mock_embedding_service
        system.vector_store = mock_vector_store
        return system


# ============================================================================
# TESTS UNITAIRES - DATACLASSES
# ============================================================================


class TestRAGConfig:
    """Tests for RAGConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RAGConfig()

        assert config.embedding_model == EmbeddingModel.GEMINI_TEXT_EMBEDDING_004
        assert config.embedding_dimension == 768
        assert config.persist_directory == Path("./data/vector_store")
        assert config.max_results == 10
        assert config.similarity_threshold == 0.7
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200

    def test_custom_config(self):
        """Test custom configuration values."""
        config = RAGConfig(
            embedding_model=EmbeddingModel.GEMINI_TEXT_EMBEDDING_004,
            embedding_dimension=512,
            persist_directory=Path("/custom/path"),
            max_results=20,
            similarity_threshold=0.8,
            chunk_size=500,
            chunk_overlap=100,
        )

        assert config.embedding_dimension == 512
        assert config.persist_directory == Path("/custom/path")
        assert config.max_results == 20
        assert config.similarity_threshold == 0.8
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100


class TestJobOffer:
    """Tests for JobOffer dataclass."""

    def test_job_offer_creation(self, sample_job_offer):
        """Test JobOffer creation with all fields."""
        job = sample_job_offer

        assert job.id == "job_123"
        assert job.title == "Développeur Python Senior"
        assert job.company == "StartupTech"
        assert job.location == "Paris"
        assert job.skills == ["python", "django", "fastapi", "postgresql", "docker"]
        assert job.experience_level == "Senior"
        assert job.salary_range == {"min": 50000, "max": 70000, "currency": "EUR"}
        assert job.metadata == {"source": "france_travail", "contract_type": "CDI"}

    def test_job_offer_minimal(self):
        """Test JobOffer creation with minimal fields."""
        job = JobOffer(
            id="job_min",
            title="Test Job",
            description="Test Description",
            company="Test Company",
            location="Test Location",
            skills=["skill1"],
            experience_level="Junior",
        )

        assert job.id == "job_min"
        assert job.title == "Test Job"
        assert job.salary_range is None
        assert job.metadata is None

    def test_job_offer_skills_empty(self):
        """Test JobOffer with empty skills list."""
        job = JobOffer(
            id="job_empty",
            title="Test Job",
            description="Test",
            company="Test",
            location="Test",
            skills=[],
            experience_level="Junior",
        )

        assert job.skills == []


class TestCVProfile:
    """Tests for CVProfile dataclass."""

    def test_cv_profile_creation(self, sample_cv_profile):
        """Test CVProfile creation with all fields."""
        cv = sample_cv_profile

        assert cv.id == "cv_456"
        assert cv.skills == ["python", "django", "postgresql", "docker", "git"]
        assert len(cv.experiences) == 2
        assert len(cv.education) == 2
        assert (
            cv.summary
            == "Développeur Python passionné avec 2 ans d'expérience en développement web"
        )
        assert cv.metadata == {"language": "fr", "experience_years": 2}

    def test_cv_profile_minimal(self):
        """Test CVProfile creation with minimal fields."""
        cv = CVProfile(id="cv_min", skills=["python"], experiences=[], education=[])

        assert cv.id == "cv_min"
        assert cv.skills == ["python"]
        assert cv.experiences == []
        assert cv.education == []
        assert cv.summary is None
        assert cv.metadata is None

    def test_cv_profile_empty_skills(self):
        """Test CVProfile with empty skills list."""
        cv = CVProfile(id="cv_empty", skills=[], experiences=[], education=[])

        assert cv.skills == []


class TestMatchResult:
    """Tests for MatchResult dataclass."""

    def test_match_result_creation(self, sample_job_offer):
        """Test MatchResult creation."""
        match = MatchResult(
            job_offer=sample_job_offer,
            similarity_score=0.85,
            matching_skills=["python", "django"],
            missing_skills=["fastapi", "aws"],
            explanation="Good match with core skills",
        )

        assert match.job_offer == sample_job_offer
        assert match.similarity_score == 0.85
        assert match.matching_skills == ["python", "django"]
        assert match.missing_skills == ["fastapi", "aws"]
        assert match.explanation == "Good match with core skills"

    def test_match_result_minimal(self, sample_job_offer):
        """Test MatchResult creation without explanation."""
        match = MatchResult(
            job_offer=sample_job_offer,
            similarity_score=0.75,
            matching_skills=[],
            missing_skills=[],
        )

        assert match.similarity_score == 0.75
        assert match.matching_skills == []
        assert match.missing_skills == []
        assert match.explanation is None


# ============================================================================
# TESTS UNITAIRES - RAGSYSTEM
# ============================================================================


class TestRAGSystemInitialization:
    """Tests for RAGSystem initialization."""

    def test_init_default_config(self, mock_embedding_service, mock_vector_store):
        """Test RAGSystem initialization with default config."""
        with (
            patch("rag.core.EmbeddingService", return_value=mock_embedding_service),
            patch("rag.core.VectorStoreService", return_value=mock_vector_store),
        ):
            system = RAGSystem(embedding_api_key="test_key")

            assert system.config is not None
            assert system.config.similarity_threshold == 0.7
            assert system.embedding_service == mock_embedding_service
            assert system.vector_store == mock_vector_store

            # Verify collections were initialized
            assert mock_vector_store.get_or_create_collection.call_count == 2

    def test_init_custom_config(self, mock_embedding_service, mock_vector_store):
        """Test RAGSystem initialization with custom config."""
        custom_config = RAGConfig(
            similarity_threshold=0.8,
            max_results=15,
            persist_directory=Path("/custom/path"),
        )

        with (
            patch("rag.core.EmbeddingService", return_value=mock_embedding_service),
            patch("rag.core.VectorStoreService", return_value=mock_vector_store),
        ):
            system = RAGSystem(embedding_api_key="test_key", config=custom_config)

            assert system.config == custom_config
            assert system.config.similarity_threshold == 0.8
            assert system.config.max_results == 15

    def test_init_embedding_service_failure(self):
        """Test RAGSystem initialization when EmbeddingService fails."""
        with (
            patch("rag.core.EmbeddingService", side_effect=Exception("API error")),
            patch("rag.core.VectorStoreService"),
        ):
            with pytest.raises(RAGError, match="Failed to initialize RAG system"):
                RAGSystem(embedding_api_key="test_key")

    def test_init_vector_store_failure(self, mock_embedding_service):
        """Test RAGSystem initialization when VectorStoreService fails."""
        with (
            patch("rag.core.EmbeddingService", return_value=mock_embedding_service),
            patch("rag.core.VectorStoreService", side_effect=Exception("DB error")),
        ):
            with pytest.raises(RAGError, match="Failed to initialize RAG system"):
                RAGSystem(embedding_api_key="test_key")


class TestRAGSystemTextCreation:
    """Tests for text creation methods."""

    def test_create_job_offer_text(self, rag_system, sample_job_offer):
        """Test _create_job_offer_text method."""
        text = rag_system._create_job_offer_text(sample_job_offer)

        assert "Title: Développeur Python Senior" in text
        assert "Company: StartupTech" in text
        assert "Location: Paris" in text
        assert "Required Skills: python, django, fastapi, postgresql, docker" in text
        assert "Experience Level: Senior" in text
        assert "Salary: 50000 - 70000 EUR" in text

    def test_create_job_offer_text_no_salary(self, rag_system):
        """Test _create_job_offer_text without salary."""
        job = JobOffer(
            id="test",
            title="Test",
            description="Test",
            company="Test",
            location="Test",
            skills=["test"],
            experience_level="Test",
        )

        text = rag_system._create_job_offer_text(job)
        assert "Salary:" not in text

    def test_create_cv_profile_text(self, rag_system, sample_cv_profile):
        """Test _create_cv_profile_text method."""
        text = rag_system._create_cv_profile_text(sample_cv_profile)

        assert "Summary: Développeur Python passionné" in text
        assert "Skills: python, django, postgresql, docker, git" in text
        assert "Experiences:" in text
        assert "Développeur Python at PreviousCorp" in text
        assert "Education:" in text
        assert "Master Informatique from Université Paris" in text

    def test_create_cv_profile_text_minimal(self, rag_system):
        """Test _create_cv_profile_text with minimal CV."""
        cv = CVProfile(id="test", skills=["python"], experiences=[], education=[])

        text = rag_system._create_cv_profile_text(cv)
        assert "Skills: python" in text
        assert "Experiences:" not in text
        assert "Education:" not in text

    def test_create_cv_profile_text_no_summary(self, rag_system):
        """Test _create_cv_profile_text without summary."""
        cv = CVProfile(
            id="test",
            skills=["python"],
            experiences=[{"title": "Dev", "company": "Test", "duration": "1y"}],
            education=[],
        )

        text = rag_system._create_cv_profile_text(cv)
        assert "Summary:" not in text
        assert "Skills: python" in text
        assert "Dev at Test" in text


class TestRAGSystemIndexing:
    """Tests for indexing methods."""

    def test_index_job_offer(
        self, rag_system, sample_job_offer, mock_embedding_service, mock_vector_store
    ):
        """Test index_job_offer method."""
        # Setup mocks
        mock_embedding_service.embed_text_with_cache.return_value = [0.1] * 768

        # Call method
        doc_id = rag_system.index_job_offer(sample_job_offer)

        # Verify calls
        mock_embedding_service.embed_text_with_cache.assert_called_once()
        mock_vector_store.add_embeddings.assert_called_once()
        assert doc_id == sample_job_offer.id

    def test_index_job_offer_embedding_failure(
        self, rag_system, sample_job_offer, mock_embedding_service
    ):
        """Test index_job_offer when embedding fails."""
        mock_embedding_service.embed_text_with_cache.side_effect = Exception(
            "Embedding error"
        )

        with pytest.raises(RAGError, match="Failed to index job offer"):
            rag_system.index_job_offer(sample_job_offer)

    def test_index_cv_profile(
        self, rag_system, sample_cv_profile, mock_embedding_service, mock_vector_store
    ):
        """Test index_cv_profile method."""
        # Setup mocks
        mock_embedding_service.embed_text.return_value = [0.1] * 768

        # Call method
        doc_id = rag_system.index_cv_profile(sample_cv_profile)

        # Verify calls
        mock_embedding_service.embed_text.assert_called_once()
        mock_vector_store.add_embeddings.assert_called_once()

        # Verify metadata
        call_args = mock_vector_store.add_embeddings.call_args
        metadata = call_args[1]["metadatas"][0]

        assert metadata["skills"] == "python,django,postgresql,docker,git"
        assert metadata["experience_count"] == 2
        assert doc_id == "cv_456"

    def test_batch_index_job_offers(
        self, rag_system, sample_job_offer, mock_embedding_service, mock_vector_store
    ):
        """Test batch_index_job_offers method."""
        job_offers = [sample_job_offer, sample_job_offer]

        doc_ids = rag_system.batch_index_job_offers(job_offers)

        assert len(doc_ids) == 2
        assert mock_embedding_service.embed_text_with_cache.call_count == 2
        mock_vector_store.add_embeddings.assert_called_once()

    def test_batch_index_empty_list(self, rag_system):
        """Test batch_index_job_offers with empty list."""
        doc_ids = rag_system.batch_index_job_offers([])

        assert doc_ids == []


class TestRAGSystemMatching:
    """Tests for matching methods."""

    def test_match_cv_with_jobs(
        self, rag_system, sample_cv_profile, mock_embedding_service, mock_vector_store
    ):
        """Test match_cv_with_jobs method."""
        # Call method
        results = rag_system.match_cv_with_jobs(sample_cv_profile)

        # Verify calls
        mock_embedding_service.embed_text_with_cache.assert_called_once()
        mock_vector_store.query_similarity.assert_called_once()

        # Verify results - only 2 pass the similarity threshold (0.7)
        # Scores: 0.85, 0.75, 0.65 (0.65 < 0.7 threshold)
        assert len(results) == 2

        # Check first result
        first_result = results[0]
        assert first_result.job_offer.title == "Développeur Python"
        assert first_result.similarity_score == 0.85  # 1 - (0.3 / 2)
        assert "python" in first_result.matching_skills
        assert "django" in first_result.matching_skills

    def test_match_cv_with_jobs_custom_max_results(
        self, rag_system, sample_cv_profile, mock_vector_store
    ):
        """Test match_cv_with_jobs with custom max_results."""
        results = rag_system.match_cv_with_jobs(sample_cv_profile, max_results=5)

        # Verify query was called with custom max_results
        call_args = mock_vector_store.query_similarity.call_args
        assert call_args[1]["n_results"] == 5

    def test_match_cv_with_jobs_threshold_filtering(
        self, rag_system, sample_cv_profile, mock_vector_store
    ):
        """Test match_cv_with_jobs filters by similarity threshold."""
        # Setup mock to return distances that will give scores: 0.85, 0.75, 0.65
        mock_vector_store.query_similarity.return_value = {
            "ids": [["job_1", "job_2", "job_3"]],
            "distances": [[0.3, 0.5, 0.7]],  # Scores: 0.85, 0.75, 0.65
            "metadatas": [[{}, {}, {}]],
            "documents": [["doc1", "doc2", "doc3"]],
        }

        # With default threshold 0.7, only first 2 should pass
        results = rag_system.match_cv_with_jobs(sample_cv_profile)

        assert len(results) == 2  # Only scores >= 0.7
        assert results[0].similarity_score == 0.85
        assert results[1].similarity_score == 0.75

    def test_match_cv_with_jobs_skill_matching(
        self, rag_system, sample_cv_profile, mock_vector_store
    ):
        """Test skill matching calculation."""
        # Setup CV with specific skills
        cv = CVProfile(
            id="test",
            skills=["python", "django", "postgresql"],
            experiences=[],
            education=[],
        )

        # Setup job with overlapping skills
        mock_vector_store.query_similarity.return_value = {
            "ids": [["job_1"]],
            "distances": [[0.3]],
            "metadatas": [
                [
                    {
                        "title": "Test Job",
                        "company": "Test",
                        "location": "Test",
                        "skills": "python,django,fastapi,aws",
                        "experience_level": "Mid-level",
                    }
                ]
            ],
            "documents": [["Test document"]],
        }

        results = rag_system.match_cv_with_jobs(cv)

        assert len(results) == 1
        result = results[0]
        assert sorted(result.matching_skills) == ["django", "python"]
        assert sorted(result.missing_skills) == ["aws", "fastapi"]

    def test_match_cv_with_jobs_embedding_failure(
        self, rag_system, sample_cv_profile, mock_embedding_service
    ):
        """Test match_cv_with_jobs when embedding fails."""
        mock_embedding_service.embed_text_with_cache.side_effect = Exception(
            "Embedding error"
        )

        with pytest.raises(RAGError, match="Failed to match CV with jobs"):
            rag_system.match_cv_with_jobs(sample_cv_profile)

    def test_match_cv_with_jobs_no_results(
        self, rag_system, sample_cv_profile, mock_vector_store
    ):
        """Test match_cv_with_jobs when no results found."""
        mock_vector_store.query_similarity.return_value = {
            "ids": [[]],
            "distances": [[]],
            "metadatas": [[]],
            "documents": [[]],
        }

        results = rag_system.match_cv_with_jobs(sample_cv_profile)

        assert results == []


class TestRAGSystemUtilities:
    """Tests for utility methods."""

    def test_get_collection_stats(self, rag_system, mock_vector_store):
        """Test get_collection_stats method."""
        stats = rag_system.get_collection_stats()

        assert mock_vector_store.get_collection_stats.call_count == 2
        assert CollectionType.JOB_OFFERS.value in stats
        assert CollectionType.USER_PROFILES.value in stats

    def test_get_collection_stats_failure(self, rag_system, mock_vector_store):
        """Test get_collection_stats when it fails."""
        mock_vector_store.get_collection_stats.side_effect = Exception("DB error")

        with pytest.raises(RAGError, match="Failed to get collection stats"):
            rag_system.get_collection_stats()


# ============================================================================
# TESTS D'INTÉGRATION (avec mocks contrôlés)
# ============================================================================


class TestRAGSystemIntegration:
    """Integration tests for RAGSystem."""

    def test_full_workflow(self, rag_system, sample_job_offer, sample_cv_profile):
        """Test complete RAG workflow: index job, index CV, match."""
        # Index job offer
        job_doc_id = rag_system.index_job_offer(sample_job_offer)
        assert job_doc_id == "job_123"

        # Index CV profile
        cv_doc_id = rag_system.index_cv_profile(sample_cv_profile)
        assert cv_doc_id == "cv_456"

        # Match CV with jobs
        results = rag_system.match_cv_with_jobs(sample_cv_profile)
        assert len(results) > 0

        # Verify match quality
        for result in results:
            assert result.similarity_score >= rag_system.config.similarity_threshold
            assert isinstance(result.matching_skills, list)
            assert isinstance(result.missing_skills, list)

    def test_performance_benchmark(
        self, rag_system, sample_cv_profile, mock_vector_store
    ):
        """Test performance of matching operation."""
        # Setup timing
        start_time = time.time()

        # Execute matching
        results = rag_system.match_cv_with_jobs(sample_cv_profile)

        elapsed_time = time.time() - start_time

        # Performance requirement: < 3s for matching
        assert elapsed_time < 3.0, f"Matching took {elapsed_time:.2f}s, expected < 3s"

        # Verify we got results
        assert len(results) > 0


# ============================================================================
# TESTS DE QUALITÉ (dataset annoté)
# ============================================================================


class TestRAGQuality:
    """Quality tests with annotated dataset."""

    @pytest.fixture
    def annotated_dataset(self):
        """Create annotated test dataset."""
        return {
            "cv_profiles": [
                {
                    "id": "cv_dev_python",
                    "skills": ["python", "django", "postgresql", "git", "docker"],
                    "experiences": [
                        {
                            "title": "Développeur Python",
                            "company": "TechCorp",
                            "duration": "2 ans",
                        }
                    ],
                    "education": [
                        {
                            "degree": "Master Informatique",
                            "institution": "Université Paris",
                            "year": "2022",
                        }
                    ],
                    "summary": "Développeur Python avec 2 ans d'expérience",
                },
                {
                    "id": "cv_data_scientist",
                    "skills": [
                        "python",
                        "machine learning",
                        "sql",
                        "pandas",
                        "scikit-learn",
                    ],
                    "experiences": [
                        {
                            "title": "Data Scientist",
                            "company": "DataLab",
                            "duration": "3 ans",
                        }
                    ],
                    "education": [
                        {
                            "degree": "Master Data Science",
                            "institution": "École Polytechnique",
                            "year": "2021",
                        }
                    ],
                    "summary": "Data Scientist avec expertise ML",
                },
            ],
            "job_offers": [
                {
                    "id": "job_python_dev",
                    "title": "Développeur Python",
                    "description": "Développement applications web Python/Django",
                    "company": "PythonTech",
                    "location": "Paris",
                    "skills": ["python", "django", "postgresql", "docker"],
                    "experience_level": "Mid-level",
                    "expected_match": "cv_dev_python",  # Annotated match
                    "expected_score_min": 0.7,
                },
                {
                    "id": "job_data_scientist",
                    "title": "Data Scientist",
                    "description": "Analyse données et modèles ML",
                    "company": "MLCorp",
                    "location": "Lyon",
                    "skills": ["python", "machine learning", "sql", "pandas"],
                    "experience_level": "Senior",
                    "expected_match": "cv_data_scientist",  # Annotated match
                    "expected_score_min": 0.7,
                },
                {
                    "id": "job_devops",
                    "title": "DevOps Engineer",
                    "description": "Infrastructure cloud et CI/CD",
                    "company": "CloudTech",
                    "location": "Remote",
                    "skills": ["docker", "kubernetes", "aws", "terraform"],
                    "experience_level": "Mid-level",
                    "expected_match": None,  # No good match expected
                    "expected_score_min": 0.3,
                },
            ],
        }

    def test_quality_matching(
        self, rag_system, annotated_dataset, mock_embedding_service, mock_vector_store
    ):
        """Test matching quality with annotated dataset."""
        # This is a simplified test - in reality we would index all jobs first
        # For now, we'll test the matching logic with controlled mocks

        # Get first CV from dataset
        cv_data = annotated_dataset["cv_profiles"][0]
        cv = CVProfile(
            id=cv_data["id"],
            skills=cv_data["skills"],
            experiences=cv_data["experiences"],
            education=cv_data["education"],
            summary=cv_data["summary"],
        )

        # Setup mock to return the Python dev job as best match
        mock_vector_store.query_similarity.return_value = {
            "ids": [["job_python_dev", "job_devops"]],
            "distances": [[0.2, 0.8]],  # Scores: 0.9, 0.6
            "metadatas": [
                [
                    {
                        "title": "Développeur Python",
                        "company": "PythonTech",
                        "location": "Paris",
                        "skills": "python,django,postgresql,docker",
                        "experience_level": "Mid-level",
                    },
                    {
                        "title": "DevOps Engineer",
                        "company": "CloudTech",
                        "location": "Remote",
                        "skills": "docker,kubernetes,aws,terraform",
                        "experience_level": "Mid-level",
                    },
                ]
            ],
            "documents": [["doc1", "doc2"]],
        }

        # Match CV with jobs
        results = rag_system.match_cv_with_jobs(cv)

        # Verify we got results
        assert len(results) > 0

        # Best match should be Python dev job
        best_match = results[0]
        assert best_match.job_offer.title == "Développeur Python"
        assert best_match.similarity_score >= 0.7

        # Verify skill matching
        expected_skills = set(cv_data["skills"])
        job_skills = {"python", "django", "postgresql", "docker"}
        matching_skills = expected_skills.intersection(job_skills)

        assert len(best_match.matching_skills) == len(matching_skills)
        for skill in matching_skills:
            assert skill in best_match.matching_skills


# ============================================================================
# TESTS D'ERREURS ET CAS LIMITES
# ============================================================================


class TestRAGSystemErrorCases:
    """Tests for error cases and edge conditions."""

    def test_empty_text_embedding(self, rag_system, mock_embedding_service):
        """Test handling of empty text in embedding."""
        mock_embedding_service.embed_text.return_value = [0.0] * 768

        # Create job with minimal description
        job = JobOffer(
            id="empty",
            title="Test",
            description="",  # Empty description
            company="Test",
            location="Test",
            skills=["test"],
            experience_level="Test",
        )

        # Should not crash
        rag_system._create_job_offer_text(job)

    def test_none_values_in_metadata(
        self, rag_system, mock_embedding_service, mock_vector_store
    ):
        """Test handling of None values in metadata."""
        job = JobOffer(
            id="test",
            title="Test",
            description="Test",
            company="Test",
            location="Test",
            skills=["test"],
            experience_level="Test",
            metadata={"key": None, "valid": "value"},  # None value in metadata
        )

        # Should handle gracefully
        rag_system.index_job_offer(job)

        # Verify metadata was processed
        call_args = mock_vector_store.add_embeddings.call_args
        metadata = call_args[1]["metadatas"][0]
        assert "valid" in metadata
        assert metadata["valid"] == "value"

    def test_very_long_text(self, rag_system, mock_embedding_service):
        """Test handling of very long text."""
        long_text = "A" * 10000  # Very long text

        job = JobOffer(
            id="long",
            title="Test",
            description=long_text,
            company="Test",
            location="Test",
            skills=["test"],
            experience_level="Test",
        )

        # Should not crash
        text = rag_system._create_job_offer_text(job)
        assert len(text) > 0

    def test_special_characters_in_text(self, rag_system):
        """Test handling of special characters."""
        job = JobOffer(
            id="special",
            title="Développeur C++/Python 🚀",
            description="Développement avec C++ & Python, SQL, NoSQL...",
            company="Tech & Co",
            location="Paris (75)",
            skills=["C++", "Python", "SQL"],
            experience_level="Senior",
        )

        # Should handle special characters
        text = rag_system._create_job_offer_text(job)
        assert "C++" in text
        assert "Python" in text
        assert "Paris (75)" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
