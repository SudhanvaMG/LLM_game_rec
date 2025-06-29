"""
Phase 2: Game Generation (Hybrid Approach)

This module handles the main game generation process:
1. Samples attributes from pre-generated lists
2. Allows LLM creative flexibility (10-20% deviation)
3. Generates coherent, realistic slot games
"""

import json
import random
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.utils.llm_client import LLMClient
from src.utils.file_utils import load_json, save_json
from src.schema import SlotGame, Volatility
from prompts.phase2_game_prompts import GAME_GENERATION_PROMPT, BATCH_GAME_GENERATION_PROMPT


class GameGenerator:
    """
    Handles Phase 2 game generation using the hybrid thematic approach.
    
    Combines pre-generated thematic attributes with LLM creativity to produce
    coherent, realistic slot games at scale.
    """
    
    def __init__(self, llm_client: LLMClient, attributes_path: str = "data/attributes"):
        """
        Initialize the game generator.
        
        Args:
            llm_client: Configured LLM client for game generation
            attributes_path: Path to the generated attributes from Phase 1
        """
        self.llm_client = llm_client
        self.attributes_path = Path(attributes_path)
        
        # Load all attributes generated in Phase 1
        self.attributes = self._load_attributes()
        
        # Configuration for generation
        self.volatility_distribution = {"low": 0.3, "medium": 0.5, "high": 0.2}
        self.complexity_distribution = {"Beginner": 0.4, "Intermediate": 0.4, "Advanced": 0.2}
        
    def _load_attributes(self) -> Dict[str, Any]:
        """Load all attribute files generated in Phase 1."""
        try:
            all_attributes = load_json(self.attributes_path / "all_attributes.json")
            print(f"✅ Loaded attributes: {len(all_attributes['themes'])} themes, "
                  f"{len(all_attributes['art_styles'])} art styles, "
                  f"{len(all_attributes['developers'])} developers")
            return all_attributes
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Attributes not found at {self.attributes_path}. "
                "Please run Phase 1 attribute generation first."
            )
    
    def sample_attributes(self) -> Dict[str, Any]:
        """
        Sample a coherent set of attributes for game generation.
        
        Uses thematic bucketing to ensure natural coherence.
        
        Returns:
            Dict containing sampled attributes for one game
        """
        # Sample core theme (drives coherence)
        theme = random.choice(self.attributes["themes"])
        
        # Get thematic features for this theme
        theme_features = self.attributes["thematic_features"][theme]
        
        # Sample 2-4 features from this theme's coherent set
        num_features = random.randint(2, 4)
        special_features = random.sample(theme_features, min(num_features, len(theme_features)))
        
        # Sample other attributes
        art_style = random.choice(self.attributes["art_styles"])
        music_style = random.choice(self.attributes["music_styles"])
        developer = random.choice(self.attributes["developers"])
        
        # Sample gameplay attributes
        volatility = self._sample_weighted(self.volatility_distribution)
        complexity_level = self._sample_weighted(self.complexity_distribution)
        
        return {
            "theme": theme,
            "art_style": art_style,
            "music_style": music_style,
            "volatility": volatility,
            "special_features": special_features,
            "developer": developer,
            "complexity_level": complexity_level
        }
    
    def _sample_weighted(self, distribution: Dict[str, float]) -> str:
        """Sample from a weighted distribution."""
        choices = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(choices, weights=weights)[0]
    
    async def generate_single_game(self, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a single slot game using the hybrid approach.
        
        Args:
            attributes: Pre-sampled attributes, or None to sample new ones
            
        Returns:
            Generated game as dictionary
        """
        if attributes is None:
            attributes = self.sample_attributes()
        
        # Format prompt with sampled attributes
        prompt = GAME_GENERATION_PROMPT.format(
            theme=attributes["theme"],
            art_style=attributes["art_style"],
            music_style=attributes["music_style"],
            volatility=attributes["volatility"],
            special_features=", ".join(attributes["special_features"][:3]),  # Limit for prompt clarity
            developer=attributes["developer"],
            complexity_level=attributes["complexity_level"]
        )
        
        # Generate game using LLM - fail if this fails
        print(f"🎯 Generating game with theme: {attributes['theme']}")
        response = await self.llm_client.generate_async(
            prompt=prompt,
            task_type="game_generation"
        )
        
        # Parse JSON response - fail if parsing fails
        try:
            # Extract JSON from markdown code blocks if present
            json_content = self._extract_json_from_response(response)
            game_data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM response as JSON: {e}")
            print(f"🔍 LLM Response: {response[:500]}...")
            raise Exception(f"LLM returned invalid JSON: {e}")
        
        # Validate and clean up the response
        game_data = self._validate_and_clean_game(game_data, attributes)
        
        print(f"✅ Successfully generated: {game_data['name']}")
        return game_data
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON content from LLM response, handling markdown code blocks.
        
        Args:
            response: Raw LLM response that may contain markdown formatting
            
        Returns:
            Clean JSON string ready for parsing
        """
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # Check if response is wrapped in markdown code blocks
        if response.startswith("```json"):
            # Extract everything between ```json and ```
            lines = response.split('\n')
            json_lines = []
            in_json_block = False
            
            for line in lines:
                if line.strip().startswith("```json"):
                    in_json_block = True
                    continue
                elif line.strip() == "```" and in_json_block:
                    break
                elif in_json_block:
                    json_lines.append(line)
            
            json_content = '\n'.join(json_lines).strip()
            
            # For arrays, ensure we extract complete JSON
            if json_content.startswith("["):
                return self._extract_complete_json_array(json_content)
            elif json_content.startswith("{"):
                return self._extract_complete_json_object(json_content)
            else:
                return json_content
        
        # Check if response starts with [ (JSON array) or { (JSON object)
        elif response.startswith("["):
            return self._extract_complete_json_array(response)
        elif response.startswith("{"):
            return self._extract_complete_json_object(response)
        
        # Try to find JSON within the response
        else:
            # Look for array first
            array_start = response.find("[")
            if array_start != -1:
                return self._extract_complete_json_array(response[array_start:])
            
            # Then look for object
            obj_start = response.find("{")
            if obj_start != -1:
                return self._extract_complete_json_object(response[obj_start:])
            
            raise ValueError("No valid JSON found in LLM response")
    
    def _extract_complete_json_array(self, content: str) -> str:
        """Extract a complete JSON array, handling nested brackets."""
        bracket_count = 0
        start_found = False
        
        for i, char in enumerate(content):
            if char == '[':
                if not start_found:
                    start_found = True
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0 and start_found:
                    return content[:i + 1]
        
        # If we couldn't find the complete array, return everything up to the first ]
        end_bracket = content.find(']')
        if end_bracket != -1:
            return content[:end_bracket + 1]
        
        raise ValueError("Incomplete JSON array in response")
    
    def _extract_complete_json_object(self, content: str) -> str:
        """Extract a complete JSON object, handling nested braces."""
        brace_count = 0
        start_found = False
        
        for i, char in enumerate(content):
            if char == '{':
                if not start_found:
                    start_found = True
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_found:
                    return content[:i + 1]
        
        # If we couldn't find the complete object, return everything up to the last }
        end_brace = content.rfind('}')
        if end_brace != -1:
            return content[:end_brace + 1]
        
        raise ValueError("Incomplete JSON object in response")
    
    async def generate_batch_games(self, num_games: int = 100, batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple games efficiently using batch processing.
        
        Args:
            num_games: Total number of games to generate
            batch_size: Number of games to generate per LLM call
            
        Returns:
            List of generated games
        """
        print(f"🎮 Starting batch generation of {num_games} games...")
        all_games = []
        
        # Process in batches to optimize API calls
        for batch_start in range(0, num_games, batch_size):
            batch_end = min(batch_start + batch_size, num_games)
            batch_count = batch_end - batch_start
            
            print(f"⚡ Generating batch {batch_start//batch_size + 1}: "
                  f"games {batch_start + 1}-{batch_end}")
            
            # Sample attributes for this batch
            batch_attributes = [self.sample_attributes() for _ in range(batch_count)]
            
            try:
                # Generate batch using single LLM call
                batch_games = await self._generate_game_batch(batch_attributes)
                all_games.extend(batch_games)
                
                print(f"✅ Completed batch: {len(batch_games)} games generated")
                
            except Exception as e:
                print(f"❌ Batch generation failed: {e}")
                print(f"🔍 Failed batch attributes: {[attr['theme'] for attr in batch_attributes]}")
                raise Exception(f"Batch generation failed - stopping execution: {e}")
        
        print(f"🎉 Generated {len(all_games)} total games!")
        return all_games
    
    async def _generate_game_batch(self, batch_attributes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate a batch of games in a single LLM call."""
        # Format attribute sets for batch prompt
        attribute_sets_text = ""
        for i, attrs in enumerate(batch_attributes, 1):
            attribute_sets_text += f"""
SET {i}:
Theme: {attrs["theme"]}
Art Style: {attrs["art_style"]}
Music Style: {attrs["music_style"]}
Volatility: {attrs["volatility"]}
Special Features: {", ".join(attrs["special_features"][:3])}
Developer: {attrs["developer"]}
Complexity Level: {attrs["complexity_level"]}
"""
        
        prompt = BATCH_GAME_GENERATION_PROMPT.format(
            attribute_sets=attribute_sets_text.strip()
        )
        
        # Generate batch response
        response = await self.llm_client.generate_async(
            prompt=prompt,
            task_type="game_generation"
        )
        
        # Parse JSON array response - handle markdown code blocks
        try:
            json_content = self._extract_json_from_response(response)
            games_data = json.loads(json_content)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Batch JSON processing failed: {e}")
            print(f"🔍 Full Response Length: {len(response)} characters")
            print(f"🔍 Response Start: {response[:300]}...")
            print(f"🔍 Response End: ...{response[-300:]}")
            # Try individual generation as fallback
            print("🔄 Falling back to individual game generation...")
            return await self._generate_games_individually(batch_attributes)
        
        # Ensure we got a list of games
        if not isinstance(games_data, list):
            print(f"❌ Expected JSON array, got {type(games_data)}. Falling back to individual generation...")
            return await self._generate_games_individually(batch_attributes)
        
        # Validate each game in the batch
        validated_games = []
        for i, game_data in enumerate(games_data):
            try:
                original_attrs = batch_attributes[i] if i < len(batch_attributes) else {}
                validated_game = self._validate_and_clean_game(game_data, original_attrs)
                validated_games.append(validated_game)
                print(f"✅ Batch game {i+1}: {validated_game['name']}")
            except Exception as e:
                print(f"❌ Failed to validate batch game {i+1}: {e}")
                raise Exception(f"Batch game {i+1} validation failed: {e}")
        
        return validated_games
    
    async def _generate_games_individually(self, batch_attributes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fallback method to generate games individually when batch generation fails.
        
        Args:
            batch_attributes: List of attribute sets for individual generation
            
        Returns:
            List of generated games
        """
        print(f"🔄 Generating {len(batch_attributes)} games individually...")
        individual_games = []
        
        for i, attributes in enumerate(batch_attributes):
            try:
                print(f"⚡ Individual game {i+1}/{len(batch_attributes)}: {attributes['theme']}")
                game = await self.generate_single_game(attributes)
                individual_games.append(game)
            except Exception as e:
                print(f"❌ Failed to generate individual game {i+1}: {e}")
                raise Exception(f"Individual generation failed for game {i+1}: {e}")
        
        return individual_games
    
    def _validate_and_clean_game(self, game_data: Dict[str, Any], original_attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean generated game data.
        
        Ensures the game meets schema requirements and fixes common issues.
        """
        # Ensure required fields exist
        required_fields = ["name", "description", "theme", "volatility", "rtp"]
        missing_fields = [field for field in required_fields if field not in game_data]
        
        if missing_fields:
            raise ValueError(f"Generated game missing required fields: {missing_fields}")
        
        # Validate and clean specific fields
        if "rtp" in game_data:
            rtp = game_data["rtp"]
            if isinstance(rtp, str):
                rtp = float(rtp.replace("%", "").replace("0.", "0."))
            game_data["rtp"] = max(0.85, min(0.98, float(rtp)))
        
        if "volatility" in game_data:
            vol = game_data["volatility"].lower()
            if vol not in ["low", "medium", "high"]:
                raise ValueError(f"Invalid volatility value: {vol}. Must be low, medium, or high.")
        
        # Ensure special_features is a list
        if "special_features" in game_data:
            features = game_data["special_features"]
            if isinstance(features, str):
                game_data["special_features"] = [features]
            elif not isinstance(features, list):
                raise ValueError(f"special_features must be a list, got: {type(features)}")
        
        # Set default values for missing optional fields
        defaults = {
            "reels": 5,
            "paylines": random.randint(10, 50),
            "has_bonus_round": random.choice([True, False]),
            "has_progressive_jackpot": random.choice([True, False, False, False]),  # 25% chance
            "max_win_multiplier": random.randint(100, 10000),
            "complexity_level": original_attrs.get("complexity_level", "Intermediate"),
            "target_demographics": ["Casual Players", "Slot Enthusiasts"],
            "release_year": random.choice([2023, 2024]),
            "developer": original_attrs.get("developer", "Unknown Studio"),
            "tags": []
        }
        
        for key, default_value in defaults.items():
            if key not in game_data:
                game_data[key] = default_value
        
        return game_data
    
    def save_games(self, games: List[Dict[str, Any]], filename: str = "generated_games.json"):
        """Save generated games to file."""
        output_path = Path("data/final") / filename
        save_json(games, output_path)
        print(f"💾 Saved {len(games)} games to {output_path}")


# Convenience functions for direct usage
async def generate_games(num_games: int = 100, output_file: str = "generated_games.json") -> List[Dict[str, Any]]:
    """
    Main function to generate games with default configuration.
    
    Args:
        num_games: Number of games to generate
        output_file: Output filename
        
    Returns:
        List of generated games
    """
    from src.utils.llm_client import LLMClient
    from src.utils.config_loader import load_config
    
    # Load configuration and create LLM client
    config = load_config()
    llm_client = LLMClient(config)
    
    # Create generator and generate games
    generator = GameGenerator(llm_client)
    games = await generator.generate_batch_games(num_games)
    
    # Save results
    generator.save_games(games, output_file)
    
    return games 