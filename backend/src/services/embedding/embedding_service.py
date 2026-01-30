"""Embedding generation service.

This service handles text embedding generation using Gemini text-embedding-004
and other embedding models. Includes caching and similarity calculations.
"""

import json
import logging
import math
from enum import Enum
from pathlib import Path
from typing import Any

from google import genai


class EmbeddingModel(str, Enum):
    """Available embedding models."""

    GEMINI_TEXT_EMBEDDING_004 = "text-embedding-004"
    # Add other models as needed


class EmbeddingError(Exception):
    """Custom exception for embedding generation errors."""

    pass


class EmbeddingService:
    """Service for generating and managing text embeddings."""

    def __init__(
        self,
        api_key: str,
        model_name: EmbeddingModel = EmbeddingModel.GEMINI_TEXT_EMBEDDING_004,
    ):
        """Initialize EmbeddingService with Gemini API configuration.

        Args:
            api_key: Gemini API key
            model_name: Name of the embedding model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        self.embedding_cache: dict[str, list[float]] = {}

        # Configure Gemini API
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Gemini embedding model: {e}")
            raise EmbeddingError(f"Failed to initialize Gemini embedding model: {e}")

    def embed_text(self, text: str, truncate: bool = True) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed
            truncate: Whether to truncate long texts (default: True)

        Returns:
            Embedding vector as list of floats

        Raises:
            ValueError: If text is empty
            EmbeddingError: If embedding generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            # Prepare text (truncate if needed)
            processed_text = self._prepare_text(text, truncate)

            # Generate embedding using new API
            response = self.client.models.embed_content(
                model=self.model_name.value, contents=processed_text
            )

            # Extract embedding from response
            embedding = self._extract_embedding_from_response(response)

            return embedding

        except Exception as e:
            logging.error(f"Failed to generate embedding: {e}")
            raise EmbeddingError(f"Failed to generate embedding: {e}")

    def embed_text_batch(
        self, texts: list[str], truncate: bool = True
    ) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed
            truncate: Whether to truncate long texts (default: True)

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
            EmbeddingError: If embedding generation fails
        """
        if not texts:
            raise ValueError("Text list cannot be empty")

        try:
            # Prepare texts
            processed_texts = [self._prepare_text(text, truncate) for text in texts]

            # Generate embeddings in batch using new API
            response = self.client.models.embed_content(
                model=self.model_name.value, contents=processed_texts
            )

            # Extract embeddings from response
            embeddings = []
            for embedding_obj in response.embeddings:
                if hasattr(embedding_obj, "values"):
                    embeddings.append(embedding_obj.values)
                else:
                    raise EmbeddingError(
                        "Invalid embedding structure in batch response"
                    )

            return embeddings

        except Exception as e:
            logging.error(f"Failed to generate batch embeddings: {e}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {e}")

    def _prepare_text(self, text: str, truncate: bool) -> str:
        """Prepare text for embedding generation.

        Args:
            text: Input text
            truncate: Whether to truncate

        Returns:
            Prepared text
        """
        # Basic cleaning
        text = text.strip()

        if truncate:
            # text-embedding-004 has limit, but let model handle it
            # We can add truncation logic here if needed
            pass

        return text

    def _extract_embedding_from_response(self, response: Any) -> list[float]:
        """Extract embedding vector from Gemini response.

        Args:
            response: Gemini API response

        Returns:
            Embedding vector

        Raises:
            EmbeddingError: If embedding extraction fails
        """
        try:
            # New API response structure
            if hasattr(response, "embeddings") and response.embeddings:
                embedding_obj = response.embeddings[0]
                if hasattr(embedding_obj, "values"):
                    return embedding_obj.values

            # Fallback for old structure or dict
            elif isinstance(response, dict):
                if "embeddings" in response and response["embeddings"]:
                    embedding_data = response["embeddings"][0]
                    if "values" in embedding_data:
                        return embedding_data["values"]

            # Try to find embedding in nested structure
            import json

            response_str = json.dumps(response, default=str)
            logging.warning(
                f"Unexpected embedding response structure: {response_str[:200]}"
            )

            raise EmbeddingError("Could not extract embedding from response")

        except Exception as e:
            logging.error(f"Failed to extract embedding: {e}")
            raise EmbeddingError(f"Failed to extract embedding: {e}")

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings generated by the current model.

        Returns:
            Embedding dimension
        """
        # text-embedding-004 has 768 dimensions
        if self.model_name == EmbeddingModel.GEMINI_TEXT_EMBEDDING_004:
            return 768
        else:
            # Default or raise error for unknown models
            raise EmbeddingError(f"Unknown embedding model: {self.model_name}")

    def cosine_similarity(
        self, embedding1: list[float], embedding2: list[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)

        Raises:
            ValueError: If embeddings have different dimensions
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have same dimension")

        # Normalize embeddings
        norm1 = self._vector_norm(embedding1)
        norm2 = self._vector_norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2, strict=False))

        # Cosine similarity
        similarity = dot_product / (norm1 * norm2)

        # Clamp to [-1, 1] due to floating point errors
        return max(-1.0, min(1.0, similarity))

    def _vector_norm(self, vector: list[float]) -> float:
        """Calculate Euclidean norm of a vector.

        Args:
            vector: Input vector

        Returns:
            Euclidean norm
        """
        return math.sqrt(sum(x * x for x in vector))

    def normalize_embedding(self, embedding: list[float]) -> list[float]:
        """Normalize embedding vector to unit length.

        Args:
            embedding: Input embedding

        Returns:
            Normalized embedding
        """
        norm = self._vector_norm(embedding)
        if norm == 0:
            return [0.0] * len(embedding)

        return [x / norm for x in embedding]

    def embed_text_with_cache(self, text: str, use_cache: bool = True) -> list[float]:
        """Generate embedding with caching.

        Args:
            text: Text to embed
            use_cache: Whether to use cache (default: True)

        Returns:
            Embedding vector
        """
        if not use_cache:
            return self.embed_text(text)

        # Check cache
        cache_key = text.strip().lower()
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key].copy()

        # Generate and cache
        embedding = self.embed_text(text)
        self.embedding_cache[cache_key] = embedding.copy()

        return embedding

    def clear_cache(self):
        """Clear embedding cache."""
        self.embedding_cache.clear()

    def save_embeddings_cache(
        self, cache_data: dict[str, list[float]], file_path: Path
    ):
        """Save embeddings cache to file.

        Args:
            cache_data: Cache data to save
            file_path: Path to save file
        """
        try:
            with open(file_path, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            logging.error(f"Failed to save embeddings cache: {e}")
            raise EmbeddingError(f"Failed to save embeddings cache: {e}")

    def load_embeddings_cache(self, file_path: Path) -> dict[str, list[float]]:
        """Load embeddings cache from file.

        Args:
            file_path: Path to cache file

        Returns:
            Loaded cache data
        """
        try:
            if not file_path.exists():
                return {}

            with open(file_path) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load embeddings cache: {e}")
            raise EmbeddingError(f"Failed to load embeddings cache: {e}")

    def similarity_search(
        self,
        query_embedding: list[float],
        candidate_embeddings: list[list[float]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Find most similar embeddings to query.

        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of results to return

        Returns:
            List of results with indices and similarity scores
        """
        if not candidate_embeddings:
            return []

        # Calculate similarities
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            try:
                similarity = self.cosine_similarity(query_embedding, candidate)
                similarities.append((i, similarity))
            except ValueError:
                # Skip invalid embeddings
                continue

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top-k results
        results = []
        for i, (idx, score) in enumerate(similarities[:top_k]):
            results.append({"index": idx, "similarity_score": score, "rank": i + 1})

        return results
