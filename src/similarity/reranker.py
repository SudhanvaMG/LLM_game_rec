"""
LLM Reranker for Game Recommendations

Takes vector similarity candidates and reranks them using LLM intelligence
for more nuanced similarity assessment and explanation generation.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.llm_client import LLMClient
from src.schema import SlotGame
from prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class LLMReranker:
    """
    LLM-powered reranking system for game recommendations.
    
    Takes vector similarity candidates and applies sophisticated LLM reasoning
    to produce final recommendations with detailed explanations.
    """
    
    def __init__(self, config_path: str = "config/llm_config.yaml"):
        """Initialize the LLM reranker."""
        self.llm_client = LLMClient(config_path)
        self.prompt_loader = PromptLoader()
        
    def create_reranking_prompt(self, 
                              query_game: Dict[str, Any], 
                              candidate_games: List[Dict[str, Any]]) -> str:
        """
        Create a structured prompt for LLM reranking using the prompt loader.
        
        Args:
            query_game: The game to find recommendations for
            candidate_games: List of candidate games from vector search
            
        Returns:
            Formatted prompt string
        """
        return self.prompt_loader.get_reranking_prompt(
            query_game_overview=query_game['overview_text'],
            candidate_games=candidate_games
        )
    
    def rerank_candidates(self, 
                         query_game: Dict[str, Any],
                         candidate_games: List[Dict[str, Any]],
                         top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Rerank candidate games using LLM intelligence.
        
        Args:
            query_game: Game to find recommendations for (with overview_text)
            candidate_games: List of candidates from vector search
            top_k: Number of final recommendations to return
            
        Returns:
            List of reranked recommendations with explanations
        """
        
        if not candidate_games:
            logger.warning("No candidate games provided for reranking")
            return []
        
        if len(candidate_games) < top_k:
            logger.warning(f"Only {len(candidate_games)} candidates available, less than requested {top_k}")
        
        try:
            # Create reranking prompt
            prompt = self.create_reranking_prompt(query_game, candidate_games)
            
            # Get LLM reranking response
            from src.utils.llm_client import TaskType
            response = self.llm_client.generate(
                prompt=prompt,
                task_type=TaskType.SIMILARITY_ANALYSIS,  # Will use appropriate model from config
                temperature=0.3,  # Lower temperature for more consistent ranking
                max_tokens=1500
            )
            
            # Parse JSON response
            try:
                # Extract JSON from response (handle potential markdown formatting)
                response_text = response.strip()
                
                if response_text.startswith("```json"):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith("```"):
                    response_text = response_text[:-3]  # Remove ```
                
                result = json.loads(response_text)
                recommendations = result.get("recommendations", [])
                
                # Validate and enhance recommendations
                final_recommendations = []
                for rec in recommendations[:top_k]:  # Ensure we don't exceed top_k
                    # Find the original candidate game data
                    game_id = rec.get("game_id")
                    original_candidate = next(
                        (c for c in candidate_games if c["game_id"] == game_id), 
                        None
                    )
                    
                    if original_candidate:
                        enhanced_rec = {
                            **rec,
                            "metadata": original_candidate["metadata"],
                            "overview_text": original_candidate["overview_text"],
                            "vector_similarity_score": original_candidate["similarity_score"]
                        }
                        final_recommendations.append(enhanced_rec)
                
                logger.info(f"Successfully reranked {len(final_recommendations)} recommendations")
                return final_recommendations
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM reranking response as JSON: {e}")
                
                # Fallback: return top candidates by vector similarity
                return self._fallback_ranking(candidate_games, top_k)
                
        except Exception as e:
            logger.error(f"Failed to rerank candidates: {e}")
            return self._fallback_ranking(candidate_games, top_k)
    
    def _fallback_ranking(self, 
                         candidate_games: List[Dict[str, Any]], 
                         top_k: int) -> List[Dict[str, Any]]:
        """
        Fallback ranking based on vector similarity scores.
        Used when LLM reranking fails.
        """
        
        # Sort by vector similarity score and take top_k
        sorted_candidates = sorted(
            candidate_games, 
            key=lambda x: x["similarity_score"], 
            reverse=True
        )
        
        fallback_recommendations = []
        for i, candidate in enumerate(sorted_candidates[:top_k]):
            fallback_rec = {
                "rank": i + 1,
                "game_id": candidate["game_id"],
                "similarity_score": candidate["similarity_score"],
                "explanation": f"Recommended based on high vector similarity ({candidate['similarity_score']:.3f}). This game shares similar themes and characteristics with your previous choice.",
                "key_similarities": ["vector similarity"],
                "appeal_factors": ["similar game characteristics"],
                "metadata": candidate["metadata"],
                "overview_text": candidate["overview_text"],
                "vector_similarity_score": candidate["similarity_score"]
            }
            fallback_recommendations.append(fallback_rec)
        
        return fallback_recommendations
    
    def create_player_friendly_explanation(self, 
                                         recommendation: Dict[str, Any],
                                         query_game_name: str) -> str:
        """
        Create a player-friendly explanation for the UI.
        
        Args:
            recommendation: Recommendation dict from rerank_candidates
            query_game_name: Name of the game the player just played
            
        Returns:
            User-friendly explanation string
        """
        
        explanation = recommendation.get("explanation", "")
        key_similarities = recommendation.get("key_similarities", [])
        
        # Create engaging, conversational explanation
        friendly_explanation = f"Because you enjoyed **{query_game_name}**, you might love this game! "
        
        if explanation:
            # Use the LLM-generated explanation
            friendly_explanation += explanation
        else:
            # Fallback explanation
            friendly_explanation += f"It shares similar gameplay elements and themes that made {query_game_name} appealing."
        
        # Add key similarities if available
        if key_similarities:
            similarities_text = ", ".join(key_similarities)
            friendly_explanation += f" Key similarities include: {similarities_text}."
        
        return friendly_explanation


# Testing and utility functions
if __name__ == "__main__":
    # Test the reranker
    
    # Sample query game
    query_game = {
        "overview_text": "Game: Pharaoh's Golden Vault | Theme: Ancient Egypt | Description: Explore ancient Egyptian tombs for hidden treasures | Volatility: medium risk level | RTP: 96.0% return rate"
    }
    
    # Sample candidates
    candidate_games = [
        {
            "game_id": "cleopatra_quest",
            "overview_text": "Game: Cleopatra's Quest | Theme: Ancient Egypt | Description: Journey with the legendary queen through mystical pyramids",
            "similarity_score": 0.92,
            "metadata": {"theme": "Ancient Egypt", "volatility": "medium"}
        },
        {
            "game_id": "space_adventure",
            "overview_text": "Game: Space Adventure | Theme: Sci-Fi | Description: Explore alien worlds and cosmic treasures",
            "similarity_score": 0.78,
            "metadata": {"theme": "Sci-Fi", "volatility": "high"}
        }
    ]
    
    reranker = LLMReranker()
    
    # Test reranking
    recommendations = reranker.rerank_candidates(query_game, candidate_games)
    
    print(f"Generated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations):
        print(f"{i+1}. {rec['game_id']} (Score: {rec['similarity_score']:.3f})")
        print(f"   {rec['explanation']}")
        print() 