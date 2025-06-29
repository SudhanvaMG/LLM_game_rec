#!/usr/bin/env python3
"""
Script to run Phase 2: Game Generation using the thematic bucketing approach.

This script generates 100+ slot games using the attributes created in Phase 1,
applying the hybrid approach with 80% attribute adherence and 20% LLM creativity.
"""

import asyncio
import sys
import time
from pathlib import Path
import dotenv

dotenv.load_dotenv()

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.generation.game_generator import GameGenerator
from src.utils.llm_client import LLMClient
from src.utils.config_loader import load_config
from src.utils.file_utils import ensure_directories_exist


async def main():
    """Main function to orchestrate game generation."""
    print("🎮 LLM-Powered Game Recommender - Phase 2: Game Generation")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Ensure output directories exist
        ensure_directories_exist("data/final")
        
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config("config/llm_config.yaml")
        
        # Initialize LLM client
        print("🤖 Initializing LLM client...")
        llm_client = LLMClient("config/llm_config.yaml")
        
        # Create game generator
        print("⚡ Setting up game generator...")
        generator = GameGenerator(llm_client)
        
        # Generate games
        print("\n🎯 Starting game synthesis...")
        print("Strategy: Thematic bucketing with hybrid LLM approach")
        print("Target: 100+ diverse, coherent slot games")
        
        games = await generator.generate_batch_games(
            num_games=110,  # Generate a few extra for good measure
            batch_size=5    # Reduced batch size to avoid token limits
        )
        
        # Save results
        print("\n💾 Saving generated games...")
        generator.save_games(games, "slot_games_dataset.json")
        
        # Generate summary statistics
        print_generation_summary(games, start_time)
        
        print("\n🎉 Phase 2 Complete! Game synthesis successful.")
        print(f"✅ Generated {len(games)} high-quality slot games ready for similarity matching.")
        
        return games
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure to run Phase 1 attribute generation first!")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error during game generation: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_generation_summary(games: list, start_time: float):
    """Print a summary of the generated games."""
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 Generation Summary:")
    print(f"   • Total Games: {len(games)}")
    print(f"   • Time Elapsed: {elapsed_time:.1f} seconds")
    print(f"   • Average Time per Game: {elapsed_time/len(games):.2f} seconds")
    
    # Analyze theme distribution
    themes = {}
    volatilities = {"low": 0, "medium": 0, "high": 0}
    developers = set()
    
    for game in games:
        theme = game.get("theme", "Unknown")
        themes[theme] = themes.get(theme, 0) + 1
        
        vol = game.get("volatility", "medium")
        if vol in volatilities:
            volatilities[vol] += 1
            
        dev = game.get("developer")
        if dev:
            developers.add(dev)
    
    print(f"\n🎨 Theme Distribution:")
    for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   • {theme}: {count} games")
    
    print(f"\n⚡ Volatility Distribution:")
    for vol, count in volatilities.items():
        percentage = (count / len(games)) * 100
        print(f"   • {vol.title()}: {count} games ({percentage:.1f}%)")
    
    print(f"\n🏢 Unique Developers: {len(developers)}")


def test_single_game_generation():
    """Test function to generate a single game for debugging."""
    async def test():
        config = load_config("config/llm_config.yaml")
        llm_client = LLMClient("config/llm_config.yaml")
        generator = GameGenerator(llm_client)
        
        print("🧪 Testing single game generation...")
        game = await generator.generate_single_game()
        
        print(f"✅ Generated game: {game['name']}")
        print(f"   Theme: {game['theme']}")
        print(f"   Features: {game.get('special_features', [])[:2]}")
        
        return game
    
    return asyncio.run(test())


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run single game test
        game = test_single_game_generation()
        print(f"\n🎮 Test Game Generated:")
        import json
        print(json.dumps(game, indent=2))
    else:
        # Run full generation
        games = asyncio.run(main())
        
        if games:
            print(f"\n🚀 Ready for Phase 3: Similarity engine implementation!")
            print(f"📁 Games saved to: data/final/slot_games_dataset.json") 