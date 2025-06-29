#!/usr/bin/env python3
"""
LLM-Powered Game Recommender - Main Entry Point

This script provides easy access to different components of the system.
"""

import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_streamlit_app():
    """Launch the Streamlit UI."""
    print("🚀 Launching Casino Game Recommender UI...")
    print("The app will open in your browser at http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def run_similarity_setup():
    """Run the similarity engine setup."""
    print("🔧 Setting up similarity engine...")
    subprocess.run([sys.executable, "scripts/similarity_engine_setup.py"])

def run_data_generation():
    """Run data generation scripts."""
    print("📊 Running data generation...")
    subprocess.run([sys.executable, "scripts/generate_data.py"])

def show_help():
    """Show available commands."""
    print("""
🎰 LLM-Powered Game Recommender
==============================

Available commands:
  ui          - Launch the Streamlit web interface
  setup       - Setup the similarity engine (build vector index)
  generate    - Generate game data (if not already done)
  help        - Show this help message

Usage:
  python main.py ui          # Launch the web app
  python main.py setup       # Setup similarity engine
  python main.py generate    # Generate game data
  python main.py help        # Show help

Quick Start:
1. python main.py generate   # Generate games (if needed)
2. python main.py setup      # Build similarity index
3. python main.py ui         # Launch the web app
    """)

def main():
    if len(sys.argv) < 2:
        print("🎰 Welcome to the LLM-Powered Game Recommender!")
        print("Use 'python main.py help' to see available commands.")
        print("Or run 'python main.py ui' to launch the web interface.")
        return

    command = sys.argv[1].lower()
    
    if command == "ui":
        run_streamlit_app()
    elif command == "setup":
        run_similarity_setup()
    elif command == "generate":
        run_data_generation()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python main.py help' to see available commands.")

if __name__ == "__main__":
    main()
