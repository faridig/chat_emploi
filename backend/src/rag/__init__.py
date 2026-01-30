"""RAG (Retrieval-Augmented Generation) system for Chat Emploi.

This module provides the RAG system for matching CVs with job offers
using embeddings and vector similarity search.
"""

from .core import CVProfile, JobOffer, MatchResult, RAGConfig, RAGError, RAGSystem

__all__ = ["RAGSystem", "RAGConfig", "RAGError", "JobOffer", "CVProfile", "MatchResult"]
