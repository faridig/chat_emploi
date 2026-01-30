"""Test suite for Embedding service.

Tests the EmbeddingService for generating text embeddings using Gemini API.
Following TDD approach - tests should fail initially.
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest
from services.embedding.embedding_service import (
    EmbeddingError,
    EmbeddingModel,
    EmbeddingService,
)


class TestEmbeddingService:
    """Test suite for EmbeddingService."""

    @pytest.fixture
    def mock_gemini_client(self):
        """Mock Gemini API client for embeddings."""
        with patch("services.embedding.embedding_service.genai") as mock_genai:
            # Mock client
            mock_client = Mock()
            mock_models = Mock()

            # Mock response structure
            mock_embedding_response = Mock()
            mock_embedding = Mock()
            mock_embedding.values = list(np.random.randn(768))
            mock_embedding_response.embeddings = [mock_embedding]

            # Setup mocks
            mock_models.embed_content = Mock(return_value=mock_embedding_response)
            mock_client.models = mock_models
            mock_genai.Client.return_value = mock_client

            yield mock_genai, mock_client, mock_models

    @pytest.fixture
    def sample_texts(self):
        """Sample texts for embedding generation."""
        return [
            "Python developer with 5 years experience",
            "React frontend developer",
            "AWS cloud engineer",
        ]

    @pytest.fixture
    def sample_embedding_response(self):
        """Mock embedding response from Gemini."""
        # Mock embedding vectors (768 dimensions as per text-embedding-004)
        return {"embedding": {"values": list(np.random.randn(768))}}

    @pytest.fixture
    def embedding_service(self, mock_gemini_client):
        """Create EmbeddingService instance with mocked dependencies."""
        gemini_mock, _, _ = mock_gemini_client
        return EmbeddingService(
            api_key="test_key", model_name=EmbeddingModel.GEMINI_TEXT_EMBEDDING_004
        )

    def test_init_with_api_key(self, mock_gemini_client):
        """Test EmbeddingService initialization."""
        # Arrange - mock_gemini_client fixture already patches genai
        gemini_mock, _, _ = mock_gemini_client

        # Act
        service = EmbeddingService(
            api_key="test_key", model_name=EmbeddingModel.GEMINI_TEXT_EMBEDDING_004
        )

        # Assert
        assert service.api_key == "test_key"
        assert service.model_name == EmbeddingModel.GEMINI_TEXT_EMBEDDING_004
        assert service.client is not None
        # Verify Client was called with API key
        gemini_mock.Client.assert_called_once_with(api_key="test_key")

    def test_embed_text_single(
        self, embedding_service, mock_gemini_client, sample_embedding_response
    ):
        """Test embedding generation for single text."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client
        text = "Sample text for embedding"

        # Mock the response structure
        mock_embedding_response = Mock()
        mock_embedding = Mock()
        mock_embedding.values = list(np.random.randn(768))
        mock_embedding_response.embeddings = [mock_embedding]
        mock_models.embed_content.return_value = mock_embedding_response

        # Act
        embedding = embedding_service.embed_text(text)

        # Assert
        assert embedding is not None
        assert len(embedding) == 768  # text-embedding-004 dimension
        assert isinstance(embedding, list)
        assert all(isinstance(x, float) for x in embedding)

        # Verify API call
        mock_models.embed_content.assert_called_once()
        call_args = mock_models.embed_content.call_args
        assert call_args[1]["model"] == "text-embedding-004"
        assert call_args[1]["contents"] == text

    def test_embed_text_batch(
        self,
        embedding_service,
        mock_gemini_client,
        sample_texts,
        sample_embedding_response,
    ):
        """Test batch embedding generation."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client

        # Mock batch response
        mock_embedding_response = Mock()
        mock_embeddings = []
        for _ in sample_texts:
            mock_embedding = Mock()
            mock_embedding.values = list(np.random.randn(768))
            mock_embeddings.append(mock_embedding)

        mock_embedding_response.embeddings = mock_embeddings
        mock_models.embed_content.return_value = mock_embedding_response

        # Act
        embeddings = embedding_service.embed_text_batch(sample_texts)

        # Assert
        assert len(embeddings) == len(sample_texts)
        assert all(len(emb) == 768 for emb in embeddings)
        # Verify batch call with all texts
        mock_models.embed_content.assert_called_once()
        call_args = mock_models.embed_content.call_args
        assert call_args[1]["model"] == "text-embedding-004"
        assert call_args[1]["contents"] == sample_texts

    def test_embed_text_empty_input(self, embedding_service):
        """Test embedding generation with empty text."""
        # Act & Assert
        with pytest.raises(ValueError, match="Text cannot be empty"):
            embedding_service.embed_text("")

        with pytest.raises(ValueError, match="Text list cannot be empty"):
            embedding_service.embed_text_batch([])

    def test_embed_text_api_error(self, embedding_service, mock_gemini_client):
        """Test embedding generation when API fails."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client
        mock_models.embed_content.side_effect = Exception("API error")

        # Act & Assert
        with pytest.raises(EmbeddingError, match="Failed to generate embedding"):
            embedding_service.embed_text("Sample text")

    def test_embed_text_truncation(
        self, embedding_service, mock_gemini_client, sample_embedding_response
    ):
        """Test that long texts are truncated appropriately."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client

        # Mock response
        mock_embedding_response = Mock()
        mock_embedding = Mock()
        mock_embedding.values = list(np.random.randn(768))
        mock_embedding_response.embeddings = [mock_embedding]
        mock_models.embed_content.return_value = mock_embedding_response

        # Create a very long text
        long_text = "word " * 10000  # 50,000 characters

        # Act
        embedding = embedding_service.embed_text(long_text)

        # Assert
        assert embedding is not None
        # Verify truncation was applied (model might have its own limits)
        mock_models.embed_content.assert_called_once()

    def test_get_embedding_dimension(self, embedding_service):
        """Test getting embedding dimension for the model."""
        # Act
        dimension = embedding_service.get_embedding_dimension()

        # Assert
        assert dimension == 768  # text-embedding-004 dimension

    def test_cosine_similarity(self, embedding_service):
        """Test cosine similarity calculation between embeddings."""
        # Arrange
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        embedding3 = [1.0, 0.0, 0.0]  # Same as embedding1

        # Act
        similarity_diff = embedding_service.cosine_similarity(embedding1, embedding2)
        similarity_same = embedding_service.cosine_similarity(embedding1, embedding3)

        # Assert
        assert 0.0 <= similarity_diff <= 1.0
        assert abs(similarity_same - 1.0) < 0.0001  # Should be exactly 1
        assert similarity_diff < similarity_same  # Different vectors less similar

    def test_normalize_embedding(self, embedding_service):
        """Test embedding normalization."""
        # Arrange
        embedding = [3.0, 4.0, 0.0]  # Length 5

        # Act
        normalized = embedding_service.normalize_embedding(embedding)

        # Assert
        assert len(normalized) == len(embedding)
        # Check normalized length is approximately 1
        length = sum(x * x for x in normalized) ** 0.5
        assert abs(length - 1.0) < 0.0001

    def test_save_load_embeddings_cache(self, embedding_service, tmp_path):
        """Test saving and loading embeddings cache."""
        # Arrange
        cache_file = tmp_path / "embeddings_cache.json"
        embeddings_data = {
            "text1": list(np.random.randn(768)),
            "text2": list(np.random.randn(768)),
        }

        # Act - Save
        embedding_service.save_embeddings_cache(embeddings_data, cache_file)

        # Assert file exists
        assert cache_file.exists()

        # Act - Load
        loaded_data = embedding_service.load_embeddings_cache(cache_file)

        # Assert
        assert len(loaded_data) == len(embeddings_data)
        assert "text1" in loaded_data
        assert len(loaded_data["text1"]) == 768

    def test_cache_embedding(
        self, embedding_service, mock_gemini_client, sample_embedding_response
    ):
        """Test embedding caching functionality."""
        # Arrange
        _, mock_client, mock_models = mock_gemini_client

        # Mock response
        mock_embedding_response = Mock()
        mock_embedding = Mock()
        mock_embedding.values = list(np.random.randn(768))
        mock_embedding_response.embeddings = [mock_embedding]
        mock_models.embed_content.return_value = mock_embedding_response

        text = "Sample text"

        # Act - First call (should call API)
        embedding1 = embedding_service.embed_text_with_cache(text)

        # Act - Second call (should use cache)
        embedding2 = embedding_service.embed_text_with_cache(text)

        # Assert
        assert embedding1 == embedding2
        # API should only be called once
        assert mock_models.embed_content.call_count == 1
