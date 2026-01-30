"""Vector store service for ChromaDB.

This service manages vector embeddings in ChromaDB for similarity search
and retrieval of profiles and job offers.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings


class CollectionType(str, Enum):
    """Types of collections in vector store."""

    USER_PROFILES = "user_profiles"
    JOB_OFFERS = "job_offers"
    CONVERSATIONS = "conversations"
    CUSTOM = "custom"


class VectorStoreError(Exception):
    """Custom exception for vector store errors."""

    pass


class VectorStoreService:
    """Service for managing vector embeddings in ChromaDB."""

    def __init__(self, persist_directory: Path, embedding_dimension: int = 768):
        """Initialize VectorStoreService with ChromaDB.

        Args:
            persist_directory: Directory to persist ChromaDB data
            embedding_dimension: Dimension of embeddings (default: 768 for text-embedding-004)
        """
        self.persist_directory = Path(persist_directory)
        self.embedding_dimension = embedding_dimension
        self.client = None
        self.collections: dict[str, Any] = {}

        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False),
            )
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB client: {e}")
            raise VectorStoreError(f"Failed to initialize ChromaDB client: {e}")

    def create_collection(
        self,
        name: str,
        collection_type: CollectionType = CollectionType.CUSTOM,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Create a new collection.

        Args:
            name: Name of the collection
            collection_type: Type of collection (for organization)
            metadata: Additional metadata for the collection

        Returns:
            ChromaDB collection object

        Raises:
            VectorStoreError: If collection creation fails
        """
        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")

        try:
            # Prepare collection metadata
            collection_metadata = {
                "type": collection_type.value,
                "embedding_dimension": self.embedding_dimension,
                **(metadata or {}),
            }

            # Create collection
            collection = self.client.create_collection(
                name=name, metadata=collection_metadata
            )

            # Cache collection
            self.collections[name] = collection

            return collection

        except Exception as e:
            logging.error(f"Failed to create collection '{name}': {e}")
            raise VectorStoreError(f"Failed to create collection '{name}': {e}")

    def get_or_create_collection(
        self,
        name: str,
        collection_type: CollectionType = CollectionType.CUSTOM,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Get existing collection or create it if it doesn't exist.

        Args:
            name: Name of the collection
            collection_type: Type of collection
            metadata: Additional metadata

        Returns:
            ChromaDB collection object
        """
        # Prepare collection metadata
        collection_metadata = {
            "type": collection_type.value,
            "embedding_dimension": self.embedding_dimension,
            **(metadata or {}),
        }

        try:
            # Use ChromaDB's get_or_create_collection
            collection = self.client.get_or_create_collection(
                name=name, metadata=collection_metadata
            )
            self.collections[name] = collection
            return collection
        except Exception as e:
            logging.error(f"Failed to get or create collection '{name}': {e}")
            raise VectorStoreError(f"Failed to get or create collection '{name}': {e}")

    def add_embeddings(
        self,
        collection_name: str,
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
        ids: list[str],
    ) -> bool:
        """Add embeddings to a collection.

        Args:
            collection_name: Name of the collection
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            documents: List of document texts
            ids: List of unique IDs for each embedding

        Returns:
            True if successful

        Raises:
            ValueError: If input lists have mismatched lengths
            VectorStoreError: If addition fails
        """
        # Validate input
        if not all(len(lst) == len(embeddings) for lst in [metadatas, documents, ids]):
            raise ValueError("All input lists must have the same length")

        if not embeddings:
            raise ValueError("Embeddings list cannot be empty")

        try:
            # Get or create collection
            collection = self.get_or_create_collection(collection_name)

            # Add embeddings to collection
            collection.add(
                embeddings=embeddings, metadatas=metadatas, documents=documents, ids=ids
            )

            return True

        except Exception as e:
            logging.error(
                f"Failed to add embeddings to collection '{collection_name}': {e}"
            )
            raise VectorStoreError(
                f"Failed to add embeddings to collection '{collection_name}': {e}"
            )

    def query_similarity(
        self,
        collection_name: str,
        query_embeddings: list[list[float]],
        n_results: int = 5,
        where: dict[str, Any] | None = None,
        where_document: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Query similar embeddings in a collection.

        Args:
            collection_name: Name of the collection
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return per query
            where: Filter by metadata
            where_document: Filter by document content

        Returns:
            Query results dictionary
        """
        try:
            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # Query collection
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document,
            )

            return results

        except Exception as e:
            logging.error(f"Failed to query collection '{collection_name}': {e}")
            raise VectorStoreError(
                f"Failed to query collection '{collection_name}': {e}"
            )

    def get_embedding_by_id(
        self, collection_name: str, embedding_id: str
    ) -> dict[str, Any]:
        """Get embedding and metadata by ID.

        Args:
            collection_name: Name of the collection
            embedding_id: ID of the embedding

        Returns:
            Dictionary with embedding, metadata, and document
        """
        try:
            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # Get by ID
            results = collection.get(ids=[embedding_id])

            if not results["ids"]:
                raise VectorStoreError(f"Embedding with ID '{embedding_id}' not found")

            # Extract first result
            # ChromaDB returns lists of lists: for single ID, embeddings = [[embedding_vector]]
            embedding = None
            if results["embeddings"] and results["embeddings"][0]:
                embedding = results["embeddings"][0][0]

            metadata = {}
            if results["metadatas"] and results["metadatas"][0]:
                metadata = results["metadatas"][0][0]

            document = None
            if results["documents"] and results["documents"][0]:
                document = results["documents"][0][0]

            return {
                "id": (
                    results["ids"][0][0]
                    if results["ids"] and results["ids"][0]
                    else embedding_id
                ),
                "embedding": embedding,
                "metadata": metadata,
                "document": document,
            }

        except Exception as e:
            logging.error(
                f"Failed to get embedding '{embedding_id}' from '{collection_name}': {e}"
            )
            raise VectorStoreError(
                f"Failed to get embedding '{embedding_id}' from '{collection_name}': {e}"
            )

    def delete_embeddings(self, collection_name: str, ids: list[str]) -> bool:
        """Delete embeddings from a collection by IDs.

        Args:
            collection_name: Name of the collection
            ids: List of IDs to delete

        Returns:
            True if successful
        """
        try:
            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # Delete embeddings
            collection.delete(ids=ids)

            return True

        except Exception as e:
            logging.error(f"Failed to delete embeddings from '{collection_name}': {e}")
            raise VectorStoreError(
                f"Failed to delete embeddings from '{collection_name}': {e}"
            )

    def update_embedding_metadata(
        self, collection_name: str, embedding_id: str, metadata: dict[str, Any]
    ) -> bool:
        """Update metadata for an embedding.

        Note: ChromaDB doesn't support direct metadata updates.
        We need to get the embedding, delete it, and re-add with new metadata.

        Args:
            collection_name: Name of the collection
            embedding_id: ID of the embedding to update
            metadata: New metadata dictionary

        Returns:
            True if successful
        """
        try:
            # Get existing embedding
            existing = self.get_embedding_by_id(collection_name, embedding_id)

            # Delete existing
            self.delete_embeddings(collection_name, [embedding_id])

            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # Re-add with updated metadata
            collection.add(
                embeddings=[existing["embedding"]] if existing["embedding"] else None,
                metadatas=[metadata],
                documents=[existing["document"]] if existing["document"] else None,
                ids=[embedding_id],
            )

            return True

        except Exception as e:
            logging.error(f"Failed to update metadata for '{embedding_id}': {e}")
            raise VectorStoreError(
                f"Failed to update metadata for '{embedding_id}': {e}"
            )

    def get_collection_stats(self, collection_name: str) -> dict[str, Any]:
        """Get statistics for a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection statistics
        """
        try:
            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # Get count
            count = collection.count()

            # Get metadata
            metadata = collection.metadata or {}

            return {
                "name": collection_name,
                "count": count,
                "metadata": metadata,
                "embedding_dimension": self.embedding_dimension,
            }

        except Exception as e:
            logging.error(
                f"Failed to get stats for collection '{collection_name}': {e}"
            )
            raise VectorStoreError(
                f"Failed to get stats for collection '{collection_name}': {e}"
            )

    def create_index(self, collection_name: str) -> bool:
        """Create or update index for a collection.

        Note: ChromaDB creates indexes automatically, but this method
        can be used to trigger optimization.

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        try:
            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # ChromaDB indexes automatically, but we can ensure it's created
            # by performing a dummy query
            _ = collection.peek(limit=1)

            return True

        except Exception as e:
            logging.error(
                f"Failed to create index for collection '{collection_name}': {e}"
            )
            raise VectorStoreError(
                f"Failed to create index for collection '{collection_name}': {e}"
            )

    def list_collections(self) -> list[dict[str, Any]]:
        """List all collections.

        Returns:
            List of collection info dictionaries
        """
        try:
            collections = self.client.list_collections()

            result = []
            for collection in collections:
                stats = self.get_collection_stats(collection.name)
                result.append(stats)

            return result

        except Exception as e:
            logging.error(f"Failed to list collections: {e}")
            raise VectorStoreError(f"Failed to list collections: {e}")

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            True if successful
        """
        try:
            # Remove from cache
            if collection_name in self.collections:
                del self.collections[collection_name]

            # Delete collection
            self.client.delete_collection(name=collection_name)

            return True

        except Exception as e:
            logging.error(f"Failed to delete collection '{collection_name}': {e}")
            raise VectorStoreError(
                f"Failed to delete collection '{collection_name}': {e}"
            )

    def search_by_metadata(
        self, collection_name: str, metadata_filter: dict[str, Any], n_results: int = 10
    ) -> dict[str, Any]:
        """Search embeddings by metadata filter.

        Args:
            collection_name: Name of the collection
            metadata_filter: Metadata filter dictionary
            n_results: Number of results to return

        Returns:
            Query results dictionary
        """
        try:
            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # Get all embeddings matching filter
            results = collection.get(where=metadata_filter, limit=n_results)

            return results

        except Exception as e:
            logging.error(f"Failed to search by metadata in '{collection_name}': {e}")
            raise VectorStoreError(
                f"Failed to search by metadata in '{collection_name}': {e}"
            )

    def batch_operations(
        self, collection_name: str, operations: list[dict[str, Any]]
    ) -> bool:
        """Perform batch operations on a collection.

        Args:
            collection_name: Name of the collection
            operations: List of operation dictionaries
                Each operation: {"type": "add|delete|update", "data": ...}

        Returns:
            True if all operations successful
        """
        try:
            # Get collection
            collection = self.get_or_create_collection(collection_name)

            # Process each operation
            for op in operations:
                op_type = op.get("type")
                data = op.get("data", {})

                if op_type == "add":
                    collection.add(**data)
                elif op_type == "delete":
                    collection.delete(**data)
                elif op_type == "update":
                    # Update is not directly supported
                    raise NotImplementedError("Update operation not implemented")
                else:
                    raise ValueError(f"Unknown operation type: {op_type}")

            return True

        except Exception as e:
            logging.error(
                f"Failed to perform batch operations on '{collection_name}': {e}"
            )
            raise VectorStoreError(
                f"Failed to perform batch operations on '{collection_name}': {e}"
            )
