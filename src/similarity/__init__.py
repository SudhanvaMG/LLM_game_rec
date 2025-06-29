"""
Similarity Engine for LLM-Powered Game Recommender

Two-stage recommendation system:
1. Vector similarity search (fast candidate retrieval)  
2. LLM reranking (quality refinement)
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.similarity.similarity_engine import SimilarityEngine
from src.similarity.embedding_generator import EmbeddingGenerator
from src.similarity.vector_store import VectorStore
from src.similarity.reranker import LLMReranker

__all__ = ["SimilarityEngine", "EmbeddingGenerator", "VectorStore", "LLMReranker"] 