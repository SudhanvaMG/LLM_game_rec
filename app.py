import streamlit as st
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.similarity.similarity_engine import SimilarityEngine
from src.utils.file_utils import load_json

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🎰 Casino Game Recommender",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_similarity_engine():
    """Load the similarity engine (cached for performance)."""
    try:
        engine = SimilarityEngine()
        return engine
    except Exception as e:
        st.error(f"Failed to load similarity engine: {e}")
        return None

@st.cache_data
def load_games_data():
    """Load the games dataset (cached for performance)."""
    try:
        games_data = load_json("data/final/slot_games_dataset_clean.json")
        # Create a mapping of game names to full game data for display
        games_dict = {game["name"]: game for game in games_data}
        return games_dict
    except Exception as e:
        st.error(f"Failed to load games data: {e}")
        return {}

def display_game_card(game_data: Dict[str, Any], is_recommended: bool = False):
    """Display a game card with key information."""
    
    # Header with game name and theme
    if is_recommended:
        st.markdown(f"### 🎯 **{game_data['name']}**")
    else:
        st.markdown(f"### 🎰 **{game_data['name']}**")
    
    # Create columns for organized layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Theme:** {game_data.get('theme', 'N/A')}")
        st.markdown(f"**Description:** {game_data.get('description', 'No description available')}")
        
        # Special features
        features = game_data.get('special_features', [])
        if features:
            features_text = ", ".join(features[:3])  # Show first 3 features
            if len(features) > 3:
                features_text += f" + {len(features) - 3} more"
            st.markdown(f"**Features:** {features_text}")
    
    with col2:
        st.markdown(f"**Volatility:** {game_data.get('volatility', 'N/A').title()}")
        st.markdown(f"**RTP:** {game_data.get('rtp', 'N/A')}%")
        st.markdown(f"**Art Style:** {game_data.get('art_style', 'N/A')}")
    
    with col3:
        st.markdown(f"**Reels:** {game_data.get('reels', 'N/A')}")
        st.markdown(f"**Paylines:** {game_data.get('paylines', 'N/A')}")
        st.markdown(f"**Max Win:** {game_data.get('max_win_multiplier', 'N/A')}x")

def display_recommendation_with_explanation(rec: Dict[str, Any], games_dict: Dict[str, Any]):
    """Display a recommendation with its explanation."""
    
    game_name = rec.get('game_id') or rec.get('game_name') or rec.get('name')
    explanation = rec.get('explanation', 'No explanation available.')
    
    # Get full game data
    game_data = games_dict.get(game_name, {})
    
    with st.container():
        # Explanation box
        st.info(f"💡 **Why this recommendation:** {explanation}")
        
        # Game details
        if game_data:
            display_game_card(game_data, is_recommended=True)
        else:
            st.warning(f"Game details not found for: {game_name}")
        
        st.markdown("---")

def main():
    # Header
    st.title("🎰 Casino Game Recommender")
    st.markdown("**Discover your next favorite slot game based on what you just played!**")
    
    # Load data
    with st.spinner("Loading game data and similarity engine..."):
        games_dict = load_games_data()
        similarity_engine = load_similarity_engine()
    
    if not games_dict:
        st.error("Failed to load games data. Please check if the dataset exists.")
        st.stop()
    
    if not similarity_engine:
        st.error("Failed to load similarity engine. Please check the configuration.")
        st.stop()
    
    # Check if the similarity engine is ready
    status = similarity_engine.get_index_status()
    if not status.get('ready_for_recommendations', False):
        st.warning("⚠️ Similarity engine not ready. Vector index needs to be built first.")
        st.info("Run the similarity engine setup script to build the index.")
        
        # Show setup instructions
        with st.expander("📋 Setup Instructions"):
            st.code("""
# Build the vector index first:
python scripts/similarity_engine_setup.py

# Or run incrementally:
python scripts/similarity_engine_setup.py --incremental
            """)
        st.stop()
    
    # Sidebar with game selection
    st.sidebar.header("🎮 Select Your Game")
    st.sidebar.markdown("Choose a game you just played to get personalized recommendations:")
    
    # Game selection dropdown
    game_names = sorted(games_dict.keys())
    selected_game = st.sidebar.selectbox(
        "Select a game:",
        options=[""] + game_names,
        index=0,
        help="Choose the slot game you just finished playing"
    )
    
    # Main content area
    if not selected_game:
        # Welcome screen
        st.markdown("## 👋 Welcome!")
        st.markdown("Select a game from the sidebar to get started with personalized recommendations.")
        
        # Show some sample games
        st.markdown("### 🎰 Sample Games Available:")
        sample_games = list(games_dict.keys())[:6]  # Show first 6 games
        
        cols = st.columns(2)
        for i, game_name in enumerate(sample_games):
            with cols[i % 2]:
                game_data = games_dict[game_name]
                st.markdown(f"**{game_name}**")
                st.markdown(f"*{game_data.get('theme', 'Unknown Theme')} • {game_data.get('volatility', 'Unknown').title()} Volatility*")
                st.markdown("---")
    
    else:
        # Show selected game
        st.markdown("## 🎯 Your Selected Game")
        selected_game_data = games_dict[selected_game]
        display_game_card(selected_game_data)
        
        st.markdown("---")
        
        # Get recommendations
        st.markdown("## 🌟 Recommended For You")
        st.markdown(f"**Because you played {selected_game}, you might like:**")
        
        with st.spinner("Finding similar games..."):
            try:
                recommendations = similarity_engine.get_recommendations(
                    game_name=selected_game,
                    num_candidates=10,
                    num_final_recommendations=3
                )
                
                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        st.markdown(f"## 🏆 Recommendation #{i}")
                        display_recommendation_with_explanation(rec, games_dict)
                
                else:
                    st.warning("No recommendations found. The similarity engine may need to be rebuilt.")
                    
            except Exception as e:
                st.error(f"Error getting recommendations: {e}")
                logger.error(f"Recommendation error: {e}")

if __name__ == "__main__":
    main() 