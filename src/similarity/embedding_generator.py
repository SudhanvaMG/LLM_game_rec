"""
Embedding Generator for Game Similarity

Creates searchable game overviews and converts them to vector embeddings
for fast similarity search.
"""

import os
import sys
import openai
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.schema import SlotGame
from src.utils.config_loader import load_config
from src.utils.llm_client import LLMClient
from prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings for slot games using OpenAI's text-embedding model.
    
    Creates structured game overviews that capture key similarity features,
    then converts them to vector embeddings for fast search.
    """
    
    def __init__(self, config_path: str = "config/llm_config.yaml"):
        """Initialize embedding generator with OpenAI client and LLM for overview generation."""
        self.config = load_config(config_path)
        
        # Initialize OpenAI client for embeddings
        # Note: We'll use OpenAI for embeddings even if using Gemini for generation
        # as OpenAI has excellent embedding models
        api_key = (self.config.get("openai_api_key") or 
                  os.getenv("OPENAI_API_KEY") or 
                  os.getenv("OPEN_AI_KEY"))
        if not api_key:
            raise ValueError("OpenAI API key required for embeddings. Set OPENAI_API_KEY or OPEN_AI_KEY env var.")
        
        openai.api_key = api_key
        self.embedding_model = self.config.get("embedding_model", "text-embedding-3-small")
        
        # Initialize LLM client for game overview generation
        self.llm_client = LLMClient(config_path)
        self.prompt_loader = PromptLoader()
        
    def create_game_overview(self, game: SlotGame) -> str:
        """
        Create a comprehensive text overview of a game for embedding using LLM.
        
        This overview captures all the key features that affect similarity:
        theme, mechanics, audience, style, etc.
        """
        try:
            # Convert game to dictionary for the prompt
            game_dict = asdict(game)
            
            # Convert volatility enum to string
            if hasattr(game_dict['volatility'], 'value'):
                game_dict['volatility'] = game_dict['volatility'].value
            elif hasattr(game_dict['volatility'], 'name'):
                game_dict['volatility'] = game_dict['volatility'].name.lower()
            
            # Get the prompt for game overview generation
            prompt = self.prompt_loader.get_game_overview_prompt(game_dict)
            
            # Generate the overview using LLM
            from src.utils.llm_client import TaskType
            overview = self.llm_client.generate(
                prompt=prompt,
                task_type=TaskType.EMBEDDINGS_SUMMARY,  # Use Gemini 2.0 Flash for embeddings summary
                temperature=0.6,  # Use configured temperature
            )
            
            return overview.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate LLM overview for game {game.name}: {e}")
            logger.info("Falling back to programmatic overview generation")
            
            # Fallback to programmatic approach
            return self._create_programmatic_overview(game)
    
    def _create_programmatic_overview(self, game: SlotGame) -> str:
        """
        Fallback programmatic overview generation if LLM fails.
        """
        # Core theme and setting
        overview_parts = [
            f"Game: {game.name}",
            f"Theme: {game.theme}",
            f"Description: {game.description}",
        ]
        
        # Gameplay characteristics
        overview_parts.extend([
            f"Volatility: {game.volatility.value} risk level",
            f"RTP: {game.rtp:.1%} return rate",
            f"Game mechanics: {game.reels} reels with {game.paylines} paylines",
        ])
        
        # Special features (key for similarity)
        if game.special_features:
            features_text = ", ".join(game.special_features)
            overview_parts.append(f"Special features: {features_text}")
        
        # Bonus elements
        bonus_features = []
        if game.has_bonus_round:
            bonus_features.append("bonus round")
        if game.has_progressive_jackpot:
            bonus_features.append("progressive jackpot")
        if bonus_features:
            overview_parts.append(f"Bonus elements: {', '.join(bonus_features)}")
        
        # Visual and audio style
        overview_parts.extend([
            f"Art style: {game.art_style}",
            f"Music style: {game.music_style}",
        ])
        
        # Target audience and complexity
        overview_parts.extend([
            f"Complexity: {game.complexity_level} level",
            f"Target audience: {', '.join(game.target_demographics)}",
        ])
        
        # Additional context
        if game.developer:
            overview_parts.append(f"Developer: {game.developer}")
        
        if game.tags:
            overview_parts.append(f"Tags: {', '.join(game.tags)}")
        
        return " | ".join(overview_parts)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text using OpenAI's embedding model.
        """
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def process_game(self, game: SlotGame) -> Dict[str, Any]:
        """
        Process a single game: create overview + embedding.
        
        Returns:
            Dict with game_id, overview_text, embedding, and metadata
        """
        # Use Gemini (fast model) to generate natural language summary
        overview = self.create_game_overview(game)
        embedding = self.generate_embedding(overview)
        
        # Convert list fields to strings for ChromaDB compatibility
        special_features_str = ", ".join(game.special_features) if game.special_features else ""
        target_demographics_str = ", ".join(game.target_demographics) if game.target_demographics else ""
        tags_str = ", ".join(game.tags) if game.tags else ""
        
        return {
            "game_id": game.name,  # Using name as ID for now
            "overview_text": overview,
            "embedding": embedding,
            "metadata": {
                "theme": game.theme,
                "volatility": game.volatility.value,
                "rtp": game.rtp,
                "complexity": game.complexity_level,
                "developer": game.developer or "",
                "special_features": special_features_str,  # Convert list to string
                "target_demographics": target_demographics_str,  # Convert list to string
                "tags": tags_str,  # Convert list to string
                "art_style": game.art_style,
                "music_style": game.music_style,
            }
        }
    
    def process_games_batch(self, games: List[SlotGame]) -> List[Dict[str, Any]]:
        """
        Process multiple games efficiently.
        
        Args:
            games: List of SlotGame objects
            
        Returns:
            List of processed game dictionaries ready for vector store
        """
        processed_games = []
        
        logger.info(f"Processing {len(games)} games for embedding...")
        
        for i, game in enumerate(games):
            try:
                processed_game = self.process_game(game)
                processed_games.append(processed_game)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(games)} games")
                    
            except Exception as e:
                logger.error(f"Failed to process game {game.name}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_games)}/{len(games)} games")
        return processed_games


# Example usage and testing
if __name__ == "__main__":
    # Test with a sample game
    from ..schema import SlotGame, Volatility
    
    sample_game = SlotGame(
        name="Pharaoh's Golden Vault",
        description="Explore ancient Egyptian tombs for hidden treasures",
        theme="Ancient Egypt",
        volatility=Volatility.MEDIUM,
        rtp=0.96,
        art_style="Realistic 3D",
        music_style="Epic orchestral",
        reels=5,
        paylines=25,
        special_features=["Golden Wilds", "Tomb Bonus", "Free Spins"],
        has_bonus_round=True,
        has_progressive_jackpot=False,
        max_win_multiplier=5000,
        complexity_level="Intermediate",
        target_demographics=["Casino Enthusiasts", "Theme Lovers"],
        developer="Pyramid Studios"
    )
    
    generator = EmbeddingGenerator()
    overview = generator.create_game_overview(sample_game)
    print("Game Overview:")
    print(overview) 