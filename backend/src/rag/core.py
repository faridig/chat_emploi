"""RAG (Retrieval-Augmented Generation) core system.

This module implements the RAG system for matching CVs with job offers
using embeddings and vector similarity search.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.services.embedding.embedding_service import EmbeddingModel, EmbeddingService
from src.services.vector_store.vector_store_service import (
    CollectionType,
    VectorStoreService,
)


@dataclass
class RAGConfig:
    """Configuration for RAG system."""

    embedding_model: EmbeddingModel = EmbeddingModel.GEMINI_TEXT_EMBEDDING_004
    embedding_dimension: int = 768
    persist_directory: Path = Path("./data/vector_store")
    embedding_cache_path: Path = Path("./data/embeddings_cache.json")
    max_results: int = 10
    similarity_threshold: float = 0.7
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class JobOffer:
    """Job offer data structure."""

    id: str
    title: str
    description: str
    company: str
    location: str
    skills: list[str]
    experience_level: str
    salary_range: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class CVProfile:
    """CV profile data structure."""

    id: str
    skills: list[str]
    experiences: list[dict[str, Any]]
    education: list[dict[str, Any]]
    summary: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class MatchResult:
    """Result of matching a CV with job offers."""

    job_offer: JobOffer
    similarity_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    explanation: str | None = None


class RAGError(Exception):
    """Custom exception for RAG system errors."""

    pass


class RAGSystem:
    """RAG system for matching CVs with job offers."""

    def __init__(self, embedding_api_key: str, config: RAGConfig | None = None):
        """Initialize RAG system.

        Args:
            embedding_api_key: API key for embedding service
            config: RAG configuration (optional)
        """
        self.config = config or RAGConfig()

        # Initialize services
        try:
            self.embedding_service = EmbeddingService(
                api_key=embedding_api_key, model_name=self.config.embedding_model
            )

            # Load embedding cache if exists
            if self.config.embedding_cache_path.exists():
                try:
                    cache_data = self.embedding_service.load_embeddings_cache(
                        self.config.embedding_cache_path
                    )
                    self.embedding_service.embedding_cache = cache_data
                    logging.info(f"Loaded {len(cache_data)} embeddings from cache")
                except Exception as e:
                    logging.warning(f"Failed to load embedding cache: {e}")

            self.vector_store = VectorStoreService(
                persist_directory=self.config.persist_directory,
                embedding_dimension=self.config.embedding_dimension,
            )

            # Create collections if they don't exist
            self._initialize_collections()

            logging.info("RAG system initialized successfully")

        except Exception as e:
            logging.error(f"Failed to initialize RAG system: {e}")
            raise RAGError(f"Failed to initialize RAG system: {e}")

    def _initialize_collections(self):
        """Initialize vector store collections."""
        # Create job offers collection
        self.vector_store.get_or_create_collection(
            name=CollectionType.JOB_OFFERS.value,
            metadata={"description": "Job offers for matching"},
        )

        # Create CV profiles collection
        self.vector_store.get_or_create_collection(
            name=CollectionType.USER_PROFILES.value,
            metadata={"description": "User CV profiles"},
        )

    def save_state(self):
        """Save system state (cache, etc.)."""
        try:
            # Ensure directory exists
            self.config.embedding_cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.embedding_service.save_embeddings_cache(
                self.embedding_service.embedding_cache, self.config.embedding_cache_path
            )
            logging.info("Saved embedding cache")
        except Exception as e:
            logging.error(f"Failed to save system state: {e}")

    def index_job_offer(self, job_offer: JobOffer) -> str:
        """Index a job offer in the vector store.

        Args:
            job_offer: Job offer to index

        Returns:
            Document ID in vector store
        """
        try:
            # Create text representation for embedding
            text = self._create_job_offer_text(job_offer)

            # Generate embedding
            embedding = self.embedding_service.embed_text_with_cache(text)

            # Prepare metadata
            metadata = {
                "title": job_offer.title,
                "company": job_offer.company,
                "location": job_offer.location,
                "skills": ",".join(job_offer.skills),
                "experience_level": job_offer.experience_level,
                "source": "france_travail",
            }
            if job_offer.metadata:
                metadata.update(job_offer.metadata)

            # Add to vector store
            self.vector_store.add_embeddings(
                collection_name=CollectionType.JOB_OFFERS.value,
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[job_offer.id],
            )
            doc_id = job_offer.id

            # Save cache
            self.save_state()

            logging.info(f"Indexed job offer: {job_offer.title} (ID: {doc_id})")
            return doc_id

        except Exception as e:
            logging.error(f"Failed to index job offer {job_offer.id}: {e}")
            raise RAGError(f"Failed to index job offer: {e}")

    def index_cv_profile(self, cv_profile: CVProfile) -> str:
        """Index a CV profile in the vector store.

        Args:
            cv_profile: CV profile to index

        Returns:
            Document ID in vector store
        """
        try:
            # Create text representation for embedding
            text = self._create_cv_profile_text(cv_profile)

            # Generate embedding
            embedding = self.embedding_service.embed_text(text)

            # Prepare metadata
            metadata = {
                "skills": ",".join(cv_profile.skills),
                "experience_count": len(cv_profile.experiences),
                "education_count": len(cv_profile.education),
            }
            if cv_profile.metadata:
                metadata.update(cv_profile.metadata)

            # Add to vector store
            self.vector_store.add_embeddings(
                collection_name=CollectionType.USER_PROFILES.value,
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[cv_profile.id],
            )
            doc_id = cv_profile.id

            logging.info(f"Indexed CV profile: {cv_profile.id}")
            return doc_id

        except Exception as e:
            logging.error(f"Failed to index CV profile {cv_profile.id}: {e}")
            raise RAGError(f"Failed to index CV profile: {e}")

    def match_cv_with_jobs(
        self, cv_profile: CVProfile, max_results: int | None = None
    ) -> list[MatchResult]:
        """Match a CV profile with relevant job offers.

        Args:
            cv_profile: CV profile to match
            max_results: Maximum number of results to return

        Returns:
            List of match results sorted by similarity score
        """
        try:
            start_time = time.time()

            # Create text representation for embedding
            query_text = self._create_cv_profile_text(cv_profile)

            # Generate embedding for query
            query_embedding = self.embedding_service.embed_text_with_cache(query_text)

            # Save cache (in case it was a new query)
            self.save_state()

            # Search for similar job offers
            max_results = max_results or self.config.max_results
            results = self.vector_store.query_similarity(
                collection_name=CollectionType.JOB_OFFERS.value,
                query_embeddings=[query_embedding],
                n_results=max_results,
            )

            # Process results
            match_results = []
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                distance = results["distances"][0][i]
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i]

                # Convert distance to similarity score (1 - normalized distance)
                similarity_score = 1.0 - (distance / 2.0)  # ChromaDB uses L2 distance

                # Create job offer from metadata
                job_offer = JobOffer(
                    id=doc_id,
                    title=metadata.get("title", ""),
                    description=document,
                    company=metadata.get("company", ""),
                    location=metadata.get("location", ""),
                    skills=(
                        metadata.get("skills", "").split(",")
                        if metadata.get("skills")
                        else []
                    ),
                    experience_level=metadata.get("experience_level", ""),
                    metadata=metadata,
                )

                # Calculate skill matching
                cv_skills = set(cv_profile.skills)
                job_skills = set(job_offer.skills)
                matching_skills = list(cv_skills.intersection(job_skills))
                missing_skills = list(job_skills - cv_skills)

                # Create match result
                match_result = MatchResult(
                    job_offer=job_offer,
                    similarity_score=similarity_score,
                    matching_skills=matching_skills,
                    missing_skills=missing_skills,
                )

                match_results.append(match_result)

            # Sort by similarity score (descending)
            match_results.sort(key=lambda x: x.similarity_score, reverse=True)

            # Filter by similarity threshold
            match_results = [
                result
                for result in match_results
                if result.similarity_score >= self.config.similarity_threshold
            ]

            elapsed_time = time.time() - start_time
            logging.info(
                f"Matched CV {cv_profile.id} with {len(match_results)} jobs in {elapsed_time:.2f}s"
            )

            return match_results

        except Exception as e:
            logging.error(f"Failed to match CV {cv_profile.id}: {e}")
            raise RAGError(f"Failed to match CV with jobs: {e}")

    def _create_job_offer_text(self, job_offer: JobOffer) -> str:
        """Create text representation of a job offer for embedding.

        Args:
            job_offer: Job offer to convert to text

        Returns:
            Text representation
        """
        parts = [
            f"Title: {job_offer.title}",
            f"Company: {job_offer.company}",
            f"Location: {job_offer.location}",
            f"Description: {job_offer.description}",
            f"Required Skills: {', '.join(job_offer.skills)}",
            f"Experience Level: {job_offer.experience_level}",
        ]

        if job_offer.salary_range:
            salary = job_offer.salary_range
            parts.append(
                f"Salary: {salary.get('min', 'N/A')} - {salary.get('max', 'N/A')} {salary.get('currency', '')}"
            )

        return "\n".join(parts)

    def _create_cv_profile_text(self, cv_profile: CVProfile) -> str:
        """Create text representation of a CV profile for embedding.

        Args:
            cv_profile: CV profile to convert to text

        Returns:
            Text representation
        """
        parts = []

        if cv_profile.summary:
            parts.append(f"Summary: {cv_profile.summary}")

        parts.append(f"Skills: {', '.join(cv_profile.skills)}")

        if cv_profile.experiences:
            parts.append("Experiences:")
            for exp in cv_profile.experiences[:3]:  # Limit to 3 most recent
                title = exp.get("title", "")
                company = exp.get("company", "")
                duration = exp.get("duration", "")
                parts.append(f"  - {title} at {company} ({duration})")

        if cv_profile.education:
            parts.append("Education:")
            for edu in cv_profile.education[:2]:  # Limit to 2 most recent
                degree = edu.get("degree", "")
                institution = edu.get("institution", "")
                year = edu.get("year", "")
                parts.append(f"  - {degree} from {institution} ({year})")

        return "\n".join(parts)

    def batch_index_job_offers(self, job_offers: list[JobOffer]) -> list[str]:
        """Index multiple job offers in batch.

        Args:
            job_offers: List of job offers to index

        Returns:
            List of document IDs
        """
        if not job_offers:
            return []

        try:
            texts = []
            ids = []
            metadatas = []
            embeddings = []

            for offer in job_offers:
                # Create text representation
                text = self._create_job_offer_text(offer)
                texts.append(text)
                ids.append(offer.id)

                # Create metadata
                metadata = {
                    "title": offer.title,
                    "company": offer.company,
                    "location": offer.location,
                    "skills": ",".join(offer.skills),
                    "experience_level": offer.experience_level,
                    "source": "france_travail",
                }
                if offer.metadata:
                    metadata.update(offer.metadata)
                metadatas.append(metadata)

                # Generate embedding with cache
                embedding = self.embedding_service.embed_text_with_cache(text)
                embeddings.append(embedding)

            # Add to vector store in batch
            self.vector_store.add_embeddings(
                collection_name=CollectionType.JOB_OFFERS.value,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids,
            )

            # Save cache
            self.save_state()

            logging.info(f"Batch indexed {len(job_offers)} job offers")
            return ids

        except Exception as e:
            logging.error(f"Failed to batch index job offers: {e}")
            raise RAGError(f"Failed to batch index job offers: {e}")

    def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store collections.

        Returns:
            Dictionary with collection statistics
        """
        try:
            stats = {}

            for collection_name in [
                CollectionType.JOB_OFFERS.value,
                CollectionType.USER_PROFILES.value,
            ]:
                collection_stats = self.vector_store.get_collection_stats(
                    collection_name
                )
                stats[collection_name] = collection_stats

            return stats

        except Exception as e:
            logging.error(f"Failed to get collection stats: {e}")
            raise RAGError(f"Failed to get collection stats: {e}")
