"""
Prompt Loader and Template Engine

Simplified prompt management for thematic bucketing approach.
Focuses only on essential prompts for our 4-hour deliverable.
"""

from typing import Dict, Any, List
import json


class PromptLoader:
    """
    Simplified prompt management for thematic bucketing generation.
    """
    
    def __init__(self):
        """Initialize prompt loader"""
        # Import only the prompt modules we need
        from prompts import phase1_attribute_prompts as p1
        from prompts import phase2_game_prompts as p2
        from prompts import similarity_prompts as sim
        
        self.phase1_prompts = p1
        self.phase2_prompts = p2
        self.similarity_prompts = sim
    
    def get_attribute_prompt(self, attribute_type: str) -> str:
        """
        Get Phase 1 attribute generation prompt.
        
        Args:
            attribute_type: Type of attribute ('themes', 'art_styles', etc.)
            
        Returns:
            Formatted prompt string
        """
        prompt_map = {
            'themes': self.phase1_prompts.THEMES_GENERATION_PROMPT,
            'art_styles': self.phase1_prompts.ART_STYLES_GENERATION_PROMPT,
            'music_styles': self.phase1_prompts.MUSIC_STYLES_GENERATION_PROMPT,
            'developers': self.phase1_prompts.DEVELOPERS_GENERATION_PROMPT
        }
        
        if attribute_type not in prompt_map:
            raise ValueError(f"Unknown attribute type: {attribute_type}")
            
        return prompt_map[attribute_type]
    
    def get_game_generation_prompt(self, **attributes) -> str:
        """
        Get Phase 2 game generation prompt with attribute substitution.
        
        Args:
            **attributes: Game attributes to substitute in template
            
        Returns:
            Formatted prompt with attributes filled in
        """
        return self.phase2_prompts.GAME_GENERATION_PROMPT.format(**attributes)
    
    def get_batch_game_prompt(self, attribute_sets: List[Dict[str, Any]]) -> str:
        """
        Get batch game generation prompt.
        
        Args:
            attribute_sets: List of attribute dictionaries
            
        Returns:
            Formatted prompt for batch generation
        """
        # Format attribute sets as readable text
        formatted_sets = []
        for i, attrs in enumerate(attribute_sets, 1):
            formatted_attrs = "\n".join([f"  {k}: {v}" for k, v in attrs.items()])
            formatted_sets.append(f"SET {i}:\n{formatted_attrs}")
        
        attribute_sets_text = "\n\n".join(formatted_sets)
        
        return self.phase2_prompts.BATCH_GAME_GENERATION_PROMPT.format(
            attribute_sets=attribute_sets_text
        )
    
    def get_thematic_features_prompt(self, theme: str) -> str:
        """
        Get thematic features generation prompt.
        
        Args:
            theme: Theme name for generating appropriate features
            
        Returns:
            Formatted thematic features prompt
        """
        return self.phase1_prompts.THEMATIC_FEATURES_GENERATION_PROMPT.format(theme=theme)
    
    def get_similarity_prompt(self, game_a: Dict[str, Any], game_b: Dict[str, Any]) -> str:
        """
        Get simple similarity analysis prompt.
        
        Args:
            game_a: First game for comparison
            game_b: Second game for comparison
            
        Returns:
            Formatted similarity prompt
        """
        return self.similarity_prompts.SIMPLE_SIMILARITY_PROMPT.format(
            game_a=json.dumps(game_a, indent=2),
            game_b=json.dumps(game_b, indent=2)
        )
    
    def get_batch_recommendations_prompt(self, target_game: Dict[str, Any], candidate_games: List[Dict[str, Any]]) -> str:
        """
        Get batch recommendations prompt.
        
        Args:
            target_game: Game the player just finished
            candidate_games: List of games to compare against
            
        Returns:
            Formatted batch recommendations prompt
        """
        return self.similarity_prompts.BATCH_RECOMMENDATIONS_PROMPT.format(
            target_game=json.dumps(target_game, indent=2),
            candidate_games=json.dumps(candidate_games, indent=2)
        )
    
    def get_reranking_prompt(self, query_game_overview: str, candidate_games: List[Dict[str, Any]]) -> str:
        """
        Get LLM reranking prompt for sophisticated game recommendations.
        
        Args:
            query_game_overview: Overview text of the game to find recommendations for
            candidate_games: List of candidate games from vector search
            
        Returns:
            Formatted reranking prompt
        """
        # Format candidate games for the prompt - use shorter format to avoid safety issues
        candidate_games_text = ""
        for i, candidate in enumerate(candidate_games, 1):
            # Extract key info from metadata for shorter prompt
            metadata = candidate.get('metadata', {})
            theme = metadata.get('theme', 'Unknown')
            volatility = metadata.get('volatility', 'Unknown')
            features = metadata.get('special_features', 'None')
            
            # Truncate overview to first 100 characters to avoid long prompts
            short_overview = candidate['overview_text'][:100] + "..." if len(candidate['overview_text']) > 100 else candidate['overview_text']
            
            candidate_games_text += f"\n{i}. {candidate['game_id']}"
            candidate_games_text += f"\n   Theme: {theme} | Volatility: {volatility}"
            candidate_games_text += f"\n   Overview: {short_overview}"
            candidate_games_text += f"\n   Features: {features[:50]}..." if len(str(features)) > 50 else f"\n   Features: {features}"
            candidate_games_text += f"\n   Similarity: {candidate['similarity_score']:.3f}\n"
        
        return self.similarity_prompts.LLM_RERANKING_PROMPT.format(
            query_game_overview=query_game_overview,
            candidate_games_text=candidate_games_text,
            num_candidates=len(candidate_games)
        )
    
    def get_game_overview_prompt(self, game_data: Dict[str, Any]) -> str:
        """
        Get game overview generation prompt for embedding purposes.
        
        Args:
            game_data: Dictionary containing game attributes
            
        Returns:
            Formatted prompt for generating natural game overview
        """
        return self.similarity_prompts.GAME_OVERVIEW_FOR_EMBEDDING_PROMPT.format(
            game_data=json.dumps(game_data, indent=2)
        ) 