"""
Phase 1: Attribute Generation

This module implements the thematic bucketing strategy:
1. Generate 12 core themes
2. Generate 6 thematic features per theme (core innovation)
3. Generate essential global attributes (art, music, developers)
"""

import json
from typing import Dict, List, Any
from utils.llm_client import LLMClient, TaskType
from utils.file_utils import save_json, load_json, ensure_directories_exist
from utils.config_loader import load_config
from prompts.phase1_attribute_prompts import (
    THEMES_GENERATION_PROMPT,
    THEMATIC_FEATURES_GENERATION_PROMPT,
    ART_STYLES_GENERATION_PROMPT,
    MUSIC_STYLES_GENERATION_PROMPT,
    DEVELOPERS_GENERATION_PROMPT
)


class AttributeGenerator:
    """
    Implements the thematic bucketing strategy for Phase 1.
    Core innovation: generate thematically-coherent features for each theme.
    """
    
    def __init__(self, 
                 llm_config_path: str = "config/llm_config.yaml",
                 generation_config_path: str = "config/generation_config.yaml"):
        """Initialize the attribute generator with LLM and configuration."""
        self.llm_client = LLMClient(llm_config_path)
        self.generation_config = load_config(generation_config_path)
        self.attribute_config = self.generation_config['attribute_generation']
        
        # Output paths
        self.output_dir = "data/attributes"
        ensure_directories_exist(self.output_dir)
        
        print("🎯 AttributeGenerator initialized with thematic bucketing strategy")
    
    def generate_all_attributes(self) -> Dict[str, Any]:
        """
        Generate all attributes using thematic bucketing strategy.
        
        Returns:
            Dictionary containing all generated attributes
        """
        print("\n🚀 Starting Phase 1: Thematic Bucketing Strategy")
        print("=" * 55)
        
        attributes = {}
        
        # Step 1: Generate 12 core themes
        print("\n1️⃣ Generating 12 core themes...")
        attributes['themes'] = self.generate_themes()
        
        # Step 2: Generate thematic features for each theme (CORE INNOVATION)
        print("\n2️⃣ Generating thematic features (core innovation)...")
        attributes['thematic_features'] = self.generate_thematic_features(attributes['themes'])
        
        # Step 3: Generate global attributes
        print("\n3️⃣ Generating global attributes...")
        attributes['art_styles'] = self.generate_art_styles()
        attributes['music_styles'] = self.generate_music_styles()
        attributes['developers'] = self.generate_developers()
        
        # Save all attributes
        self.save_attributes(attributes)
        
        summary = self._generate_summary(attributes)
        print(f"\n✅ Phase 1 Complete! {summary}")
        return attributes
    
    def generate_themes(self) -> List[str]:
        """Generate 12 diverse game themes using LLM."""
        try:
            response = self.llm_client.generate(
                prompt=THEMES_GENERATION_PROMPT,
                task_type=TaskType.ATTRIBUTE_GENERATION
            )
            
            themes = self._parse_json_response(response, "themes")
            target_count = self.attribute_config['target_counts']['themes']
            
            if len(themes) != target_count:
                print(f"⚠️ Expected {target_count} themes, got {len(themes)}")
                # Trim or pad to exact count
                themes = themes[:target_count]
            
            print(f"   ✅ Generated {len(themes)} themes")
            return themes
            
        except Exception as e:
            print(f"❌ Failed to generate themes: {e}")
            return self._get_fallback_themes()
    
    def generate_thematic_features(self, themes: List[str]) -> Dict[str, List[str]]:
        """
        Generate thematically-appropriate features for each theme.
        This is the CORE INNOVATION of the thematic bucketing strategy.
        """
        print("   🎨 This is the core innovation: thematic coherence guaranteed!")
        thematic_features = {}
        target_features_per_theme = self.attribute_config['target_counts']['thematic_features']
        
        for i, theme in enumerate(themes):
            print(f"   Generating features for theme {i+1}/{len(themes)}: {theme}")
            
            try:
                prompt = THEMATIC_FEATURES_GENERATION_PROMPT.format(theme=theme)
                response = self.llm_client.generate(
                    prompt=prompt,
                    task_type=TaskType.ATTRIBUTE_GENERATION
                )
                
                features = self._parse_json_response(response, f"features for {theme}")
                
                # Ensure exact count
                features = features[:target_features_per_theme]
                if len(features) < target_features_per_theme:
                    # Pad with fallback features if needed
                    fallback = self._get_fallback_features(theme)
                    features.extend(fallback[:target_features_per_theme - len(features)])
                
                thematic_features[theme] = features
                print(f"      ✅ Generated {len(features)} features")
                
            except Exception as e:
                print(f"      ❌ Failed to generate features for {theme}: {e}")
                thematic_features[theme] = self._get_fallback_features(theme)
        
        total_features = sum(len(features) for features in thematic_features.values())
        print(f"   ✅ Generated {total_features} total thematic features across {len(themes)} themes")
        print(f"   🎯 Each theme has {target_features_per_theme} coherent features for natural game generation")
        
        return thematic_features
    
    def generate_art_styles(self) -> List[str]:
        """Generate 8 art styles for games."""
        try:
            response = self.llm_client.generate(
                prompt=ART_STYLES_GENERATION_PROMPT,
                task_type=TaskType.ATTRIBUTE_GENERATION
            )
            
            art_styles = self._parse_json_response(response, "art_styles")
            target_count = self.attribute_config['target_counts']['art_styles']
            art_styles = art_styles[:target_count]
            
            print(f"   ✅ Generated {len(art_styles)} art styles")
            return art_styles
            
        except Exception as e:
            print(f"❌ Failed to generate art styles: {e}")
            return self._get_fallback_art_styles()
    
    def generate_music_styles(self) -> List[str]:
        """Generate 10 music styles for games."""
        try:
            response = self.llm_client.generate(
                prompt=MUSIC_STYLES_GENERATION_PROMPT,
                task_type=TaskType.ATTRIBUTE_GENERATION
            )
            
            music_styles = self._parse_json_response(response, "music_styles")
            target_count = self.attribute_config['target_counts']['music_styles']
            music_styles = music_styles[:target_count]
            
            print(f"   ✅ Generated {len(music_styles)} music styles")
            return music_styles
            
        except Exception as e:
            print(f"❌ Failed to generate music styles: {e}")
            return self._get_fallback_music_styles()
    
    def generate_developers(self) -> List[str]:
        """Generate 12 fictional game developer names."""
        try:
            response = self.llm_client.generate(
                prompt=DEVELOPERS_GENERATION_PROMPT,
                task_type=TaskType.ATTRIBUTE_GENERATION
            )
            
            developers = self._parse_json_response(response, "developers")
            target_count = self.attribute_config['target_counts']['developers']
            developers = developers[:target_count]
            
            print(f"   ✅ Generated {len(developers)} developers")
            return developers
            
        except Exception as e:
            print(f"❌ Failed to generate developers: {e}")
            return self._get_fallback_developers()
    
    def save_attributes(self, attributes: Dict[str, Any]) -> None:
        """Save all generated attributes to JSON files."""
        print("\n💾 Saving generated attributes...")
        
        # Save complete attributes file
        save_json(attributes, f"{self.output_dir}/all_attributes.json")
        
        # Save individual attribute files for easy access
        for category, data in attributes.items():
            if category != 'thematic_features':
                save_json(data, f"{self.output_dir}/{category}.json")
        
        # Save thematic features separately (this is the key innovation)
        save_json(attributes['thematic_features'], f"{self.output_dir}/thematic_features.json")
        
        print("   ✅ All attributes saved successfully")
    
    def _parse_json_response(self, response: str, context: str) -> List[str]:
        """Parse JSON response from LLM, handling potential formatting issues."""
        try:
            # Try to find JSON array in the response
            response = response.strip()
            
            # Look for JSON array pattern
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end]
                
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if item]
            
            raise ValueError("No valid JSON array found in response")
            
        except Exception as e:
            print(f"⚠️ Failed to parse JSON for {context}: {e}")
            print(f"Raw response: {response[:200]}...")
            raise
    
    def _generate_summary(self, attributes: Dict[str, Any]) -> str:
        """Generate a summary of generated attributes."""
        theme_count = len(attributes['themes'])
        feature_count = sum(len(features) for features in attributes['thematic_features'].values())
        art_count = len(attributes['art_styles'])
        music_count = len(attributes['music_styles'])
        dev_count = len(attributes['developers'])
        
        total = theme_count + feature_count + art_count + music_count + dev_count
        
        return (f"Generated {total} total attributes: "
                f"{theme_count} themes × {feature_count//theme_count} features = {feature_count} thematic features, "
                f"{art_count} art styles, {music_count} music styles, {dev_count} developers")
    
    def _get_fallback_themes(self) -> List[str]:
        """Fallback themes if generation fails."""
        return [
            "Ancient Egypt", "Sci-Fi Adventure", "Fantasy Kingdom", "Wild West",
            "Underwater World", "Space Exploration", "Pirate Treasure", "Norse Mythology",
            "Jungle Adventure", "Steampunk", "Fairy Tale", "Asian Dynasty"
        ][:self.attribute_config['target_counts']['themes']]
    
    def _get_fallback_art_styles(self) -> List[str]:
        """Fallback art styles if generation fails."""
        return [
            "Realistic 3D", "Cartoon Style", "Minimalist", "Art Deco",
            "Pixel Art", "Hand-drawn", "Photorealistic", "Stylized"
        ][:self.attribute_config['target_counts']['art_styles']]
    
    def _get_fallback_music_styles(self) -> List[str]:
        """Fallback music styles if generation fails."""
        return [
            "Epic Orchestral", "Upbeat Electronic", "Jazzy Lounge", "Mystical Ambient",
            "Rock Anthem", "Classical Symphony", "Tribal Drums", "Synthwave",
            "Folk Acoustic", "Heavy Metal"
        ][:self.attribute_config['target_counts']['music_styles']]
    
    def _get_fallback_developers(self) -> List[str]:
        """Fallback developers if generation fails."""
        return [
            "Golden Reel Studios", "Nexus Gaming", "Crimson Peak Entertainment",
            "Atlas Game Works", "Phoenix Interactive", "Thunder Bay Games",
            "Midnight Studios", "Crystal Vision", "Iron Gate Productions",
            "Starlight Gaming", "Diamond Edge", "Mystic Forge Games"
        ][:self.attribute_config['target_counts']['developers']]
    
    def _get_fallback_features(self, theme: str) -> List[str]:
        """Generate fallback features for a theme."""
        target_count = self.attribute_config['target_counts']['thematic_features']
        base_features = ["Wild Symbols", "Free Spins", "Multipliers", "Bonus Round", "Scatter Symbols"]
        theme_word = theme.split()[0].lower()
        
        # Add theme-specific feature
        thematic_feature = f"{theme_word.title()} Special Feature"
        features = base_features[:target_count-1] + [thematic_feature]
        
        return features[:target_count]


# Convenience function for direct usage
def generate_attributes() -> Dict[str, Any]:
    """
    Convenience function to generate all attributes using thematic bucketing.
    
    Returns:
        Complete attribute dictionary
    """
    generator = AttributeGenerator()
    return generator.generate_all_attributes() 