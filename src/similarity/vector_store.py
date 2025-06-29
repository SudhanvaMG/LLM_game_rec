"""
Vector Store Interface for Game Embeddings

Uses ChromaDB for storing and searching game embeddings.
Provides fast similarity search for the two-stage recommendation system.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import logging
import uuid
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class VectorStore:
    """
    ChromaDB interface for storing and searching game embeddings.
    
    Handles the vector similarity search component of the recommendation system,
    providing fast candidate retrieval before LLM reranking.
    """
    
    def __init__(self, 
                 collection_name: str = "game_embeddings",
                 persist_directory: str = "./data/vector_db",
                 host: str = "localhost",
                 port: int = 8000):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Local persistence path (for embedded mode)
            host: ChromaDB server host (for client-server mode)
            port: ChromaDB server port (for client-server mode)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Try to connect to ChromaDB server first, fallback to embedded mode
        try:
            # Client-server mode (Docker)
            self.client = chromadb.HttpClient(host=host, port=port)
            self.mode = "client-server"
            logger.info(f"Connected to ChromaDB server at {host}:{port}")
        except Exception as e:
            logger.warning(f"Failed to connect to ChromaDB server: {e}")
            logger.info("Falling back to embedded ChromaDB mode")
            
            # Embedded mode (local file system)
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.mode = "embedded"
        
        # Get or create the collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Game embeddings for similarity search"}
            )
            logger.info(f"Created new collection: {collection_name}")
    
    def add_games(self, processed_games: List[Dict[str, Any]]) -> bool:
        """
        Add processed games (with embeddings) to the vector store.
        
        Args:
            processed_games: List of dicts from EmbeddingGenerator.process_games_batch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for game_data in processed_games:
                # Generate unique ID if needed
                game_id = game_data.get("game_id", str(uuid.uuid4()))
                
                ids.append(game_id)
                embeddings.append(game_data["embedding"])
                documents.append(game_data["overview_text"])
                metadatas.append(game_data["metadata"])
            
            # Add to ChromaDB collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(processed_games)} games to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add games to vector store: {e}")
            return False
    
    def search_similar_games(self, 
                           query_embedding: List[float], 
                           exclude_game_id: Optional[str] = None,
                           n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar games using vector similarity.
        
        Args:
            query_embedding: Vector embedding of the query game
            exclude_game_id: Game ID to exclude from results (avoid self-matches)
            n_results: Number of similar games to return
            
        Returns:
            List of similar games with scores and metadata
        """
        try:
            # Perform similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results + (1 if exclude_game_id else 0),  # Get extra if excluding
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            similar_games = []
            for i, game_id in enumerate(results["ids"][0]):
                # Skip excluded game
                if exclude_game_id and game_id == exclude_game_id:
                    continue
                
                # Stop if we have enough results
                if len(similar_games) >= n_results:
                    break
                
                similar_games.append({
                    "game_id": game_id,
                    "overview_text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": 1.0 - results["distances"][0][i],  # Convert distance to similarity
                })
            
            logger.info(f"Found {len(similar_games)} similar games")
            return similar_games
            
        except Exception as e:
            logger.error(f"Failed to search similar games: {e}")
            return []
    
    def search_by_game_id(self, 
                         game_id: str, 
                         n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar games to a specific game by its ID.
        
        Args:
            game_id: ID of the game to find similarities for
            n_results: Number of similar games to return
            
        Returns:
            List of similar games
        """
        try:
            # Get the game's embedding
            game_results = self.collection.get(
                ids=[game_id],
                include=["embeddings"]
            )
            
            # Check if embeddings array is empty or None
            embeddings = game_results["embeddings"]
            if embeddings is None or len(embeddings) == 0:
                logger.warning(f"Game {game_id} not found in vector store")
                return []
            
            query_embedding = game_results["embeddings"][0]
            
            # Search for similar games (excluding the query game itself)
            return self.search_similar_games(
                query_embedding=query_embedding,
                exclude_game_id=game_id,
                n_results=n_results
            )
            
        except Exception as e:
            logger.error(f"Failed to search by game ID {game_id}: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the current collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_games": count,
                "mode": self.mode,
                "status": "healthy" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection (useful for testing)."""
        try:
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Game embeddings for similarity search"}
            )
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False


# Testing and utility functions
if __name__ == "__main__":
    # Test the vector store
    import numpy as np
    
    # Create test vector store
    vs = VectorStore()
    
    # Test with dummy data
    dummy_games = [
        {
            "game_id": "test_game_1",
            "overview_text": "Ancient Egyptian themed slot with pyramids and pharaohs",
            "embedding": np.random.rand(1536).tolist(),  # OpenAI embedding size
            "metadata": {
                "theme": "Ancient Egypt",
                "volatility": "medium",
                "developer": "Test Studios"
            }
        },
        {
            "game_id": "test_game_2", 
            "overview_text": "Space adventure slot with aliens and rockets",
            "embedding": np.random.rand(1536).tolist(),
            "metadata": {
                "theme": "Space",
                "volatility": "high",
                "developer": "Galaxy Games"
            }
        }
    ]
    
    # Test adding games
    vs.add_games(dummy_games)
    
    # Test search
    results = vs.search_by_game_id("test_game_1", n_results=5)
    print(f"Found {len(results)} similar games")
    
    # Test stats
    stats = vs.get_collection_stats()
    print(f"Collection stats: {stats}") 