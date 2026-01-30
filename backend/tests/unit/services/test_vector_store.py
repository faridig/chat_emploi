"""Test suite for Vector Store service.

Tests the VectorStoreService for managing embeddings in ChromaDB.
Following TDD approach - tests should fail initially.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from services.vector_store.vector_store_service import (
    CollectionType,
    VectorStoreService,
)


class TestVectorStoreService:
    """Test suite for VectorStoreService."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary directory for ChromaDB storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_chromadb(self):
        """Mock ChromaDB client and components."""
        with patch(
            "services.vector_store.vector_store_service.chromadb"
        ) as mock_chroma:
            # Mock persistent client
            mock_client = Mock()
            mock_chroma.PersistentClient.return_value = mock_client

            # Mock collection
            mock_collection = Mock()
            mock_collection.add = Mock()
            mock_collection.get = Mock()
            mock_collection.query = Mock()
            mock_collection.delete = Mock()
            mock_collection.count = Mock()

            mock_client.get_or_create_collection.return_value = mock_collection
            mock_client.create_collection.return_value = mock_collection
            mock_client.get_collection.return_value = mock_collection

            yield mock_chroma, mock_client, mock_collection

    @pytest.fixture
    def sample_embeddings(self):
        """Sample embeddings for testing."""
        return [
            [1.0, 0.0, 0.0, 0.0],  # Embedding 1
            [0.0, 1.0, 0.0, 0.0],  # Embedding 2
            [0.0, 0.0, 1.0, 0.0],  # Embedding 3
            [0.0, 0.0, 0.0, 1.0],  # Embedding 4
        ]

    @pytest.fixture
    def sample_metadata(self):
        """Sample metadata for testing."""
        return [
            {"title": "Python Developer", "source": "profile_1"},
            {"title": "React Developer", "source": "profile_2"},
            {"title": "AWS Engineer", "source": "offer_1"},
            {"title": "Data Scientist", "source": "offer_2"},
        ]

    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing."""
        return [
            "Python developer with 5 years experience",
            "React frontend developer with 3 years experience",
            "AWS cloud engineer certified",
            "Data scientist with ML expertise",
        ]

    @pytest.fixture
    def vector_store_service(self, mock_chromadb, temp_db_path):
        """Create VectorStoreService instance with mocked dependencies."""
        chroma_mock, _, _ = mock_chromadb
        return VectorStoreService(
            persist_directory=temp_db_path,
            embedding_dimension=4,  # Small dimension for testing
        )

    def test_init_with_persist_directory(self, mock_chromadb, temp_db_path):
        """Test VectorStoreService initialization."""
        # Arrange
        chroma_mock, mock_client, _ = mock_chromadb

        # Act
        service = VectorStoreService(
            persist_directory=temp_db_path, embedding_dimension=768
        )

        # Assert
        assert service.persist_directory == temp_db_path
        assert service.embedding_dimension == 768
        chroma_mock.PersistentClient.assert_called_once()
        # Check that path is passed as first positional argument or as keyword
        call_args = chroma_mock.PersistentClient.call_args
        # The path should be in the call
        assert str(temp_db_path) in str(call_args)

    def test_create_collection(self, vector_store_service, mock_chromadb):
        """Test creating a new collection."""
        # Arrange
        _, mock_client, mock_collection = mock_chromadb

        # Act
        collection = vector_store_service.create_collection(
            name="test_collection",
            collection_type=CollectionType.USER_PROFILES,
            metadata={"description": "Test collection"},
        )

        # Assert
        assert collection is not None
        mock_client.create_collection.assert_called_once()
        call_args = mock_client.create_collection.call_args
        assert call_args[1]["name"] == "test_collection"
        assert "metadata" in call_args[1]

    def test_get_or_create_collection(self, vector_store_service, mock_chromadb):
        """Test getting or creating a collection."""
        # Arrange
        _, mock_client, mock_collection = mock_chromadb

        # Act
        collection = vector_store_service.get_or_create_collection("profiles")

        # Assert
        assert collection is not None
        mock_client.get_or_create_collection.assert_called_once()
        # Verify name parameter
        call_args = mock_client.get_or_create_collection.call_args
        assert call_args[1]["name"] == "profiles"
        # Verify metadata includes type and embedding_dimension
        assert "metadata" in call_args[1]
        assert call_args[1]["metadata"]["type"] == "custom"
        assert call_args[1]["metadata"]["embedding_dimension"] == 4

    def test_add_embeddings(
        self,
        vector_store_service,
        mock_chromadb,
        sample_embeddings,
        sample_metadata,
        sample_documents,
    ):
        """Test adding embeddings to collection."""
        # Arrange
        _, _, mock_collection = mock_chromadb

        # Act
        result = vector_store_service.add_embeddings(
            collection_name="profiles",
            embeddings=sample_embeddings,
            metadatas=sample_metadata,
            documents=sample_documents,
            ids=["id1", "id2", "id3", "id4"],
        )

        # Assert
        assert result is True
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args

        # Verify call arguments
        assert "embeddings" in call_args[1]
        assert "metadatas" in call_args[1]
        assert "documents" in call_args[1]
        assert "ids" in call_args[1]
        assert len(call_args[1]["ids"]) == 4

    def test_query_similarity(
        self, vector_store_service, mock_chromadb, sample_embeddings
    ):
        """Test similarity search query."""
        # Arrange
        _, _, mock_collection = mock_chromadb

        # Mock query response
        mock_response = {
            "ids": [["id1", "id2"]],
            "distances": [[0.1, 0.3]],
            "metadatas": [
                [{"title": "Python Developer"}, {"title": "React Developer"}]
            ],
            "documents": [["doc1", "doc2"]],
        }
        mock_collection.query.return_value = mock_response

        query_embedding = [0.9, 0.1, 0.0, 0.0]

        # Act
        results = vector_store_service.query_similarity(
            collection_name="profiles", query_embeddings=[query_embedding], n_results=2
        )

        # Assert
        assert results is not None
        assert "ids" in results
        assert len(results["ids"][0]) == 2
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert "query_embeddings" in call_args[1]
        assert call_args[1]["n_results"] == 2

    def test_get_collection_stats(self, vector_store_service, mock_chromadb):
        """Test getting collection statistics."""
        # Arrange
        _, _, mock_collection = mock_chromadb
        mock_collection.count.return_value = 42

        # Act
        stats = vector_store_service.get_collection_stats("profiles")

        # Assert
        assert stats["count"] == 42
        mock_collection.count.assert_called_once()

    def test_delete_embeddings(self, vector_store_service, mock_chromadb):
        """Test deleting embeddings from collection."""
        # Arrange
        _, _, mock_collection = mock_chromadb

        # Act
        result = vector_store_service.delete_embeddings(
            collection_name="profiles", ids=["id1", "id2"]
        )

        # Assert
        assert result is True
        mock_collection.delete.assert_called_once_with(ids=["id1", "id2"])

    def test_add_embeddings_invalid_input(self, vector_store_service):
        """Test adding embeddings with invalid input."""
        # Test mismatched lengths
        with pytest.raises(ValueError):
            vector_store_service.add_embeddings(
                collection_name="profiles",
                embeddings=[[1.0, 0.0]],
                metadatas=[{"a": 1}],
                documents=["doc1", "doc2"],  # Mismatch
                ids=["id1"],
            )

    def test_get_embedding_by_id(self, vector_store_service, mock_chromadb):
        """Test retrieving embedding by ID."""
        # Arrange
        _, _, mock_collection = mock_chromadb

        mock_response = {
            "ids": [["id1"]],
            "embeddings": [[[1.0, 0.0, 0.0, 0.0]]],
            "metadatas": [[{"title": "Python Developer"}]],
            "documents": [["Python developer"]],
        }
        mock_collection.get.return_value = mock_response

        # Act
        result = vector_store_service.get_embedding_by_id("profiles", "id1")

        # Assert
        assert result is not None
        assert "embedding" in result
        assert result["embedding"] == [1.0, 0.0, 0.0, 0.0]
        mock_collection.get.assert_called_once_with(ids=["id1"])

    def test_update_embedding_metadata(self, vector_store_service, mock_chromadb):
        """Test updating embedding metadata."""
        # Arrange
        _, _, mock_collection = mock_chromadb

        # Mock get response (structure that get_embedding_by_id expects)
        mock_get_response = {
            "ids": [["id1"]],
            "embeddings": [[[1.0, 0.0, 0.0, 0.0]]],
            "metadatas": [[{"title": "Python Developer"}]],
            "documents": [["Python developer"]],
        }
        mock_collection.get.return_value = mock_get_response

        # Mock delete and add
        mock_collection.delete.return_value = None
        mock_collection.add.return_value = None

        # Act
        result = vector_store_service.update_embedding_metadata(
            collection_name="profiles",
            embedding_id="id1",
            metadata={"updated": True, "status": "active"},
        )

        # Assert
        assert result is True
        # Verify get was called
        mock_collection.get.assert_called_once_with(ids=["id1"])
        # Verify delete was called
        mock_collection.delete.assert_called_once_with(ids=["id1"])
        # Verify add was called with updated metadata
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert call_args[1]["metadatas"] == [{"updated": True, "status": "active"}]

    def test_create_index(self, vector_store_service, mock_chromadb):
        """Test creating index for collection."""
        # Arrange
        _, _, mock_collection = mock_chromadb

        # Act
        result = vector_store_service.create_index("profiles")

        # Assert
        # ChromaDB creates index automatically, but we can test our wrapper
        assert result is True

    def test_persist_and_load(self, vector_store_service, temp_db_path):
        """Test persistence and loading of vector store."""
        # This is more integration test, but we can test basic functionality
        # For unit test, we mock ChromaDB so persistence is mocked
        assert vector_store_service.persist_directory == temp_db_path

        # Test that we can "reload" by creating new instance
        # (in real usage, ChromaDB handles persistence)
        service2 = VectorStoreService(
            persist_directory=temp_db_path, embedding_dimension=4
        )
        assert service2.persist_directory == temp_db_path
