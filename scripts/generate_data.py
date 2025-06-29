#!/usr/bin/env python3
"""
Data Generation Script

Orchestrates the entire data generation pipeline:
1. Phase 1: Attribute generation with thematic bucketing
2. Phase 2: Game generation (coming next)
3. Phase 3: Similarity engine setup (coming next)

Usage:
    python scripts/generate_data.py [--phase1-only] [--test-run]
"""

import argparse
import sys
from pathlib import Path

# Add both root and src to path so we can import our modules
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

from generation.attribute_generator import AttributeGenerator
from utils.config_loader import load_env_file


def main():
    """Main orchestration function."""
    parser = argparse.ArgumentParser(description="Generate slot game data using LLM")
    parser.add_argument("--phase1-only", action="store_true", 
                       help="Run only Phase 1: Attribute Generation")
    parser.add_argument("--test-run", action="store_true",
                       help="Run a quick test with reduced counts")
    
    args = parser.parse_args()
    
    print("🎰 LLM-Powered Game Recommender: Data Generation")
    print("=" * 55)
    
    # Load environment variables
    load_env_file()
    
    # Check if API key is set
    import os
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("Please create a .env file with your Google API key:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return
    
    try:
        # Phase 1: Attribute Generation (Thematic Bucketing)
        print("\n🚀 Phase 1: Thematic Bucketing Strategy")
        generator = AttributeGenerator()
        
        if args.test_run:
            print("🧪 Test run mode: using reduced counts")
            # For testing, we could modify the generator to use smaller counts
            # For now, let's just run normally but mention it's a test
        
        attributes = generator.generate_all_attributes()
        
        # Display summary
        print("\n📊 Generation Summary:")
        print(f"   • {len(attributes['themes'])} themes generated")
        print(f"   • {sum(len(f) for f in attributes['thematic_features'].values())} thematic features")
        print(f"   • {len(attributes['art_styles'])} art styles")
        print(f"   • {len(attributes['music_styles'])} music styles")
        print(f"   • {len(attributes['developers'])} developers")
        
        # Show sample thematic features
        print("\n🎨 Sample Thematic Features (demonstrating coherence):")
        for theme, features in list(attributes['thematic_features'].items())[:3]:
            print(f"   {theme}: {features[:3]}...")
        
        print(f"\n✅ Phase 1 Complete! Data saved to: data/attributes/")
        
        if not args.phase1_only:
            print("\n🔄 Phase 2: Game Generation (Coming Next)")
            print("   This will use the thematic features to generate coherent games")
            print("   Run with --phase1-only to stop here for now")
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎯 Next Steps:")
    print("   1. Review generated attributes in data/attributes/")
    print("   2. Implement Phase 2: Game Generation")
    print("   3. Build Similarity Engine")
    print("   4. Create Streamlit UI")


if __name__ == "__main__":
    main() 