#!/usr/bin/env python3
"""
Similarity Engine Setup and Testing Script

This script helps with:
1. Setting up the vector database
2. Building the game index
3. Testing recommendations
4. Managing the similarity engine
"""

import sys
import argparse
import logging
from pathlib import Path

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.similarity.similarity_engine import SimilarityEngine
from src.schema import SlotGame, Volatility
from src.utils.file_utils import load_json, save_json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_index_from_games_directory(games_dir: str = "data/final"):
    """Build vector index from all games in the specified directory."""
    
    logger.info(f"Building index from games in: {games_dir}")
    
    # Initialize similarity engine
    engine = SimilarityEngine()
    
    # Clear existing index
    logger.info("Clearing existing index...")
    engine.clear_index()
    
    games_path = Path(games_dir)
    if not games_path.exists():
        logger.error(f"Games directory does not exist: {games_dir}")
        return False
    
    all_games = []
    
    # Load games from clean dataset first, then fall back to original files
    clean_dataset_path = games_path / "slot_games_dataset_clean.json"
    if clean_dataset_path.exists():
        logger.info(f"Loading games from clean dataset: {clean_dataset_path}")
        try:
            games_data = load_json(str(clean_dataset_path))
            
            for game_dict in games_data:
                # Convert volatility string to enum if needed
                if isinstance(game_dict.get("volatility"), str):
                    volatility_str = game_dict["volatility"].lower()
                    game_dict["volatility"] = Volatility(volatility_str)
                
                game = SlotGame(**game_dict)
                all_games.append(game)
                
        except Exception as e:
            logger.error(f"Failed to load games from clean dataset: {e}")
            logger.info("Falling back to loading from all JSON files")
    
    # Fallback: Load games from all JSON files if clean dataset wasn't loaded
    if not all_games:
        for json_file in games_path.glob("*.json"):
            if json_file.name == "slot_games_dataset_clean.json":
                continue  # Skip if we already tried this
                
            logger.info(f"Loading games from {json_file}")
            try:
                games_data = load_json(str(json_file))
                
                for game_dict in games_data:
                    # Convert volatility string to enum if needed
                    if isinstance(game_dict.get("volatility"), str):
                        volatility_str = game_dict["volatility"].lower()
                        game_dict["volatility"] = Volatility(volatility_str)
                    
                    game = SlotGame(**game_dict)
                    all_games.append(game)
                    
            except Exception as e:
                logger.error(f"Failed to load games from {json_file}: {e}")
                continue
    
    if not all_games:
        logger.error("No games found to index")
        return False
    
    logger.info(f"Total games to index: {len(all_games)}")
    
    # Build the index with incremental saving
    success = build_index_incrementally(engine, all_games)
    
    if success:
        logger.info("✅ Index built successfully!")
        status = engine.get_index_status()
        logger.info(f"Index status: {status}")
    else:
        logger.error("❌ Failed to build index")
    
    return success


def build_index_incrementally(engine, games, batch_size=5):
    """Build index in small batches with progress saving."""
    
    logger.info(f"Building index incrementally with batch size: {batch_size}")
    
    total_games = len(games)
    processed_count = 0
    
    # Process games in small batches
    for i in range(0, total_games, batch_size):
        batch = games[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_games + batch_size - 1) // batch_size
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} games)")
        
        try:
            # Generate embeddings for this batch
            processed_games = engine.embedding_generator.process_games_batch(batch)
            
            if not processed_games:
                logger.error(f"Failed to process batch {batch_num}")
                continue
            
            # Add this batch to vector store immediately
            success = engine.vector_store.add_games(processed_games)
            
            if success:
                processed_count += len(processed_games)
                logger.info(f"✅ Batch {batch_num} saved. Progress: {processed_count}/{total_games} games")
            else:
                logger.error(f"❌ Failed to save batch {batch_num}")
                
        except Exception as e:
            logger.error(f"Error processing batch {batch_num}: {e}")
            continue
    
    logger.info(f"Incremental indexing completed. Processed {processed_count}/{total_games} games")
    return processed_count > 0


def test_recommendations(game_name: str = None):
    """Test the recommendation system."""
    
    logger.info("Testing recommendation system...")
    
    # Initialize similarity engine
    engine = SimilarityEngine()
    
    # Check index status
    status = engine.get_index_status()
    logger.info(f"Index status: {status}")
    
    if not status.get("ready_for_recommendations", False):
        logger.error("Index is not ready. Please build the index first.")
        return False
    
    # Use provided game name or find one from the index
    if not game_name:
        # Get a sample game from the collection
        try:
            collection_info = engine.vector_store.collection.get(limit=1)
            if collection_info["ids"]:
                game_name = collection_info["ids"][0]
                logger.info(f"Using sample game: {game_name}")
            else:
                logger.error("No games found in index")
                return False
        except Exception as e:
            logger.error(f"Failed to get sample game: {e}")
            return False
    
    # Get recommendations
    logger.info(f"Getting recommendations for: {game_name}")
    recommendations = engine.get_recommendations(game_name)
    
    if recommendations:
        logger.info(f"✅ Generated {len(recommendations)} recommendations:")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['game_id']}")
            print(f"   Similarity Score: {rec.get('similarity_score', 'N/A'):.3f}")
            print(f"   Vector Score: {rec.get('vector_similarity_score', 'N/A'):.3f}")
            print(f"   Explanation: {rec.get('explanation', 'No explanation')}")
            
            if 'key_similarities' in rec:
                print(f"   Key Similarities: {', '.join(rec['key_similarities'])}")
    else:
        logger.error("❌ No recommendations generated")
        return False
    
    return True


def check_dependencies():
    """Check if required dependencies are available."""
    
    logger.info("Checking dependencies...")
    
    try:
        import chromadb
        logger.info("✅ ChromaDB available")
    except ImportError:
        logger.error("❌ ChromaDB not available. Install with: pip install chromadb")
        return False
    
    try:
        import openai
        logger.info("✅ OpenAI available")
    except ImportError:
        logger.error("❌ OpenAI not available. Install with: pip install openai")
        return False
    
    # Check API keys
    import os
    if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY")):
        logger.warning("⚠️  OPENAI_API_KEY or OPEN_AI_KEY not set. Embeddings will fail.")
    else:
        logger.info("✅ OpenAI API key found")
    
    if not os.getenv("GOOGLE_API_KEY"):
        logger.warning("⚠️  GOOGLE_API_KEY not set. LLM reranking will fail.")
    else:
        logger.info("✅ Google API key found")
    
    return True


def show_status():
    """Show current status of the similarity engine."""
    
    logger.info("Checking similarity engine status...")
    
    try:
        engine = SimilarityEngine()
        status = engine.get_index_status()
        
        print("\n📊 Similarity Engine Status:")
        print(f"   Vector Store Mode: {status['vector_store'].get('mode', 'unknown')}")
        print(f"   Total Games Indexed: {status['vector_store'].get('total_games', 0)}")
        print(f"   Embedding Model: {status.get('embedding_model', 'unknown')}")
        print(f"   Ready for Recommendations: {'✅' if status.get('ready_for_recommendations') else '❌'}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to check status: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Similarity Engine Setup and Testing")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build index command
    build_parser = subparsers.add_parser('build', help='Build vector index from games')
    build_parser.add_argument('--games-dir', default='data/final', 
                             help='Directory containing game JSON files')
    
    # Test recommendations command
    test_parser = subparsers.add_parser('test', help='Test recommendations')
    test_parser.add_argument('--game-name', help='Specific game to get recommendations for')
    
    # Check dependencies command
    subparsers.add_parser('check', help='Check dependencies and configuration')
    
    # Status command
    subparsers.add_parser('status', help='Show current status')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        success = build_index_from_games_directory(args.games_dir)
        sys.exit(0 if success else 1)
        
    elif args.command == 'test':
        success = test_recommendations(args.game_name)
        sys.exit(0 if success else 1)
        
    elif args.command == 'check':
        success = check_dependencies()
        sys.exit(0 if success else 1)
        
    elif args.command == 'status':
        success = show_status()
        sys.exit(0 if success else 1)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 