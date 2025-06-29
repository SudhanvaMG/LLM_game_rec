"""
Game Schema Definition for LLM-Powered Game Recommender

This module defines the structure and attributes of slot games for similarity matching.
The schema is designed to capture key features that influence player preferences.
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class Volatility(Enum):
    """Game volatility levels affecting payout frequency and size"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"


@dataclass
class SlotGame:
    """
    Core data structure for a slot game.
    
    This schema captures the essential attributes needed for 
    similarity matching and recommendation generation.
    """
    
    # Basic Information
    name: str
    description: str
    
    # Core Gameplay Attributes  
    theme: str                          # e.g., "Ancient Egypt", "Pirates", "Space"
    volatility: Volatility              # Risk/reward profile
    rtp: float                         # Return to Player percentage (0.85-0.98)
    
    # Visual & Audio
    art_style: str                # Visual design approach
    music_style: str                   # e.g., "Epic orchestral", "Upbeat pop"
    
    # Game Mechanics
    reels: int                         # Number of reels (typically 5)
    paylines: int                      # Number of winning lines
    special_features: List[str]        # e.g., ["Free Spins", "Multipliers", "Wild Symbols"]
    
    # Bonus Features
    has_bonus_round: bool              # Dedicated bonus game
    has_progressive_jackpot: bool      # Progressive jackpot available
    max_win_multiplier: int           # Maximum win multiplier (e.g., 5000x)
    
    # Target Audience
    complexity_level: str              # "Beginner", "Intermediate", "Advanced"
    target_demographics: List[str]     # e.g., ["Casual Players", "High Rollers"]
    
    # Additional Metadata
    release_year: Optional[int] = None
    developer: Optional[str] = None
    tags: Optional[List[str]] = None   # Additional categorization tags


# Schema validation and utility functions will be added here
def validate_game_schema(game: SlotGame) -> bool:
    """
    Validate that a SlotGame instance meets our schema requirements.
    
    TODO: Implement validation logic
    """
    # Placeholder for validation logic
    return True


def get_schema_template() -> dict:
    """
    Return a template dictionary for LLM data generation.
    
    This will be used to prompt the LLM with the expected structure.
    """
    template = {
        "name": "string",
        "description": "string", 
        "theme": "string",
        "volatility": "low|medium|high",
        "rtp": "float (0.85-0.98)",
        "art_style": "realistic|cartoon|minimalist|retro|fantasy",
        "music_style": "string",
        "reels": "integer (typically 5)",
        "paylines": "integer",
        "special_features": ["list of strings"],
        "has_bonus_round": "boolean",
        "has_progressive_jackpot": "boolean", 
        "max_win_multiplier": "integer",
        "complexity_level": "Beginner|Intermediate|Advanced",
        "target_demographics": ["list of strings"],
        "release_year": "integer (optional)",
        "developer": "string (optional)",
        "tags": ["list of strings (optional)"]
    }
    return template 