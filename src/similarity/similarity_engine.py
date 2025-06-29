"""
Main Similarity Engine for Game Recommendations

Orchestrates the two-stage recommendation process:
1. Vector similarity search (fast candidate retrieval)
2. LLM reranking (quality refinement)
"""

import logging
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.similarity.embedding_generator import EmbeddingGenerator
from src.similarity.vector_store import VectorStore
from src.similarity.reranker import LLMReranker
from src.schema import SlotGame
from src.utils.file_utils import load_json

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """
    Main similarity engine that orchestrates the complete recommendation pipeline.
    
    Combines vector similarity search with LLM reranking to provide high-quality,
    explainable game recommendations.
    """
    
    def __init__(self, 
                 config_path: str = "config/llm_config.yaml",
                 vector_db_path: str = "./data/vector_db"):
        """
        Initialize the similarity engine with all components.
        """
        
        self.embedding_generator = EmbeddingGenerator(config_path)
        self.vector_store = VectorStore(persist_directory=vector_db_path)
        self.reranker = LLMReranker(config_path)
        
        logger.info("Similarity engine initialized successfully")
    
    def build_index(self, games: List[SlotGame]) -> bool:
        """
        Build the vector index from a list of games (offline process).
        """
        
        logger.info(f"Building vector index for {len(games)} games...")
        
        try:
            # Step 1: Generate embeddings for all games
            processed_games = self.embedding_generator.process_games_batch(games)
            
            if not processed_games:
                logger.error("Failed to process any games for embedding")
                return False
            
            # Step 2: Add to vector store
            success = self.vector_store.add_games(processed_games)
            
            if success:
                logger.info("Vector index built successfully")
                stats = self.vector_store.get_collection_stats()
                logger.info(f"Index stats: {stats}")
                return True
            else:
                logger.error("Failed to add games to vector store")
                return False
                
        except Exception as e:
            logger.error(f"Failed to build vector index: {e}")
            return False
    
    def get_recommendations(self, 
                          game_name: str,
                          num_candidates: int = 10,
                          num_final_recommendations: int = 3) -> List[Dict[str, Any]]:
        """
        Get game recommendations using the two-stage process.
        """
        
        logger.info(f"Getting recommendations for game: {game_name}")
        
        try:
            # Stage 1: Vector similarity search
            candidates = self.vector_store.search_by_game_id(
                game_id=game_name,
                n_results=num_candidates
            )
            
            if not candidates:
                logger.warning(f"No candidates found for game: {game_name}")
                return []
            
            logger.info(f"Found {len(candidates)} candidates from vector search")
            
            # Get the query game overview for reranking
            query_game_overview = self._get_game_overview(game_name)
            if not query_game_overview:
                logger.error(f"Could not retrieve overview for game: {game_name}")
                return []
            
            # Stage 2: LLM reranking
            final_recommendations = self.reranker.rerank_candidates(
                query_game=query_game_overview,
                candidate_games=candidates,
                top_k=num_final_recommendations
            )
            
            logger.info(f"Generated {len(final_recommendations)} final recommendations")
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations for {game_name}: {e}")
            return []

    def _get_game_overview(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve game overview from vector store for reranking."""
        
        try:
            # Get game data from vector store
            game_results = self.vector_store.collection.get(
                ids=[game_name],
                include=["documents"]
            )
            
            if not game_results["documents"]:
                return None
            
            return {
                "overview_text": game_results["documents"][0]
            }
            
        except Exception as e:
            logger.error(f"Failed to get game overview for {game_name}: {e}")
            return None
    
    def load_games_from_json(self, games_json_path: str) -> List[SlotGame]:
        """Load games from JSON file and convert to SlotGame objects."""
        try:
            games_data = load_json(games_json_path)
            games = []
            
            for game_dict in games_data:
                # Convert volatility string to enum
                from src.schema import Volatility
                volatility_str = game_dict.get("volatility", "medium").lower()
                volatility = Volatility(volatility_str)
                game_dict["volatility"] = volatility
                
                # Create SlotGame object
                game = SlotGame(**game_dict)
                games.append(game)
            
            logger.info(f"Loaded {len(games)} games from {games_json_path}")
            return games
            
        except Exception as e:
            logger.error(f"Failed to load games from {games_json_path}: {e}")
            return []
    
    def get_index_status(self) -> Dict[str, Any]:
        """Get the current status of the vector index."""
        stats = self.vector_store.get_collection_stats()
        return {
            "vector_store": stats,
            "embedding_model": self.embedding_generator.embedding_model,
            "ready_for_recommendations": stats.get("total_games", 0) > 0
        }
    
    def clear_index(self) -> bool:
        """Clear the vector index (useful for rebuilding)."""
        return self.vector_store.clear_collection()


# Testing example
if __name__ == "__main__":
    engine = SimilarityEngine()
    status = engine.get_index_status()
    print(f"Index status: {status}") 