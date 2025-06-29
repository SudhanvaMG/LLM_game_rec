#!/usr/bin/env python3
"""
Quick test script to verify batch generation is working properly.
Tests with 8 games to validate the fixes.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.generation.game_generator import GameGenerator
from src.utils.llm_client import LLMClient


async def test_batch_generation():
    """Test batch generation with a small sample."""
    print("🧪 Testing Batch Generation - 8 Games")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Initialize LLM client and generator
        print("🤖 Initializing LLM client...")
        llm_client = LLMClient("config/llm_config.yaml")
        
        print("⚡ Setting up game generator...")
        generator = GameGenerator(llm_client)
        
        # Test batch generation with 8 games
        print("\n🎯 Testing batch generation (8 games, batch size 2)...")
        games = await generator.generate_batch_games(
            num_games=8,
            batch_size=2  # Test with 2 games per batch
        )
        
        # Print results
        elapsed_time = time.time() - start_time
        print(f"\n🎉 SUCCESS! Generated {len(games)} games in {elapsed_time:.1f} seconds")
        print(f"⚡ Average time per game: {elapsed_time/len(games):.2f} seconds")
        
        # Show game names and themes
        print(f"\n🎮 Generated Games:")
        for i, game in enumerate(games, 1):
            print(f"  {i}. {game['name']} ({game['theme']})")
        
        return games
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    games = asyncio.run(test_batch_generation())
    
    if games:
        print(f"\n✅ Batch generation test PASSED!")
        print(f"🚀 Ready to generate the full dataset!")
    else:
        print(f"\n❌ Batch generation test FAILED!")
        print(f"🔧 Need to debug further...") 