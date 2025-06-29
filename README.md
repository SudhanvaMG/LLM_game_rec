# LLM-Powered Casino Slot Game Recommendation System

A sophisticated recommendation system that generates fictional slot games and provides personalized recommendations using LLM-powered similarity matching with vector embeddings and intelligent reranking.

## 🎰 Overview

This system creates a comprehensive database of fictional casino slot games and provides intelligent recommendations based on user preferences. It combines vector similarity search with LLM-powered reranking to deliver highly relevant game suggestions.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key (for embeddings)
- Google Gemini API key (for LLM operations)
- UV package manager (or pip)

### Installation & Setup

```bash
# Clone and navigate to the project
cd LLM_game_rec

# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start ChromaDB (with pre-populated data)
# Note: Pre-computed embeddings are stored in data/vector_db/ and will be automatically loaded
docker-compose up -d

# Create .env file with your API keys
cat > .env << 'EOF'
# OpenAI API Key (required for text embeddings)
OPEN_AI_KEY=your_openai_api_key_here

# Google Gemini API Key (required for LLM operations)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional: Disable ChromaDB telemetry
ANONYMIZED_TELEMETRY=False
EOF

# Edit the .env file and add your actual API keys
# Or alternatively, export them manually:
# export OPEN_AI_KEY="your-openai-api-key-here"
# export GOOGLE_API_KEY="your-google-gemini-api-key-here"

# Run the application
uv run main.py ui
```

## ✨ Features

- **🎮 Game Generation**: Creates 100+ fictional slot games with rich attributes
- **🔍 Smart Recommendations**: Vector similarity + LLM reranking for accurate suggestions
- **🎨 Rich Attributes**: Detailed game features including themes, art styles, music, and mechanics
- **💻 Interactive UI**: Streamlit web interface for easy exploration
- **⚡ Fast Search**: ChromaDB vector store for efficient similarity matching
- **🧠 LLM Integration**: OpenAI GPT models for intelligent game generation and ranking
- **📦 Ready-to-Use**: Pre-populated database with pre-computed embeddings - no data generation required!

## 🛠️ Usage

When you run `python main.py`, you'll see three options:

### 1. Generate Data
- Creates fictional slot games and their attributes
- Builds the vector database for similarity search
- Generates 100+ unique games with detailed properties

### 2. Test Similarity Engine
- Batch tests the recommendation system
- Validates recommendation quality across different scenarios
- Outputs performance metrics and sample results

### 3. Interactive App
- Launches the Streamlit web interface
- Allows real-time game recommendations
- Provides intuitive game exploration and filtering

## 🏗️ Architecture

- **Data Generation**: LLM-powered creation of games and attributes
- **Vector Store**: ChromaDB for efficient similarity search with pre-computed embeddings
- **Reranking**: OpenAI models for intelligent result refinement
- **Frontend**: Streamlit for interactive user experience
- **Pre-computed Data**: Vector embeddings stored in `data/vector_db/` for immediate use

## 📊 Data

The system includes:
- **100+ slot games** with unique themes and mechanics
- **Rich attributes**: art styles, music, themes, features
- **Pre-computed vector embeddings** stored in `data/vector_db/` for fast similarity matching
- **Structured data** in JSON format for easy processing
- **ChromaDB database** with UUID-based collections ready for Docker deployment

## 🔧 Configuration

Configuration files in `config/`:
- `llm_config.yaml`: LLM model settings and parameters
- `generation_config.yaml`: Data generation parameters

## 📁 Project Structure

```
LLM_game_rec/
├── src/                    # Core application code
├── data/                   # Generated games and attributes
├── config/                 # Configuration files
├── prompts/               # LLM prompt templates
├── scripts/               # Utility scripts
└── app.py                 # Streamlit web interface
```

## 🚨 Troubleshooting

**ChromaDB Connection**: Ensure Docker is running with `docker-compose up -d`. The database will automatically load pre-computed embeddings from `data/vector_db/`

**ChromaDB Telemetry Error**: Disable with `export ANONYMIZED_TELEMETRY=False` or add it to your `.env` file

**Missing API Keys**: Ensure both `OPEN_AI_KEY` and `GOOGLE_API_KEY` are set in your `.env` file or as environment variables. The `.env` file should be in the project root directory.

**Dependencies**: Use `uv sync`

**Docker Issues**: Check container status with `docker ps | grep chroma`

## 📖 Documentation

For detailed technical documentation, implementation decisions, and architecture details, see [SOLUTION.md](SOLUTION.md).

## 🎯 Assignment Requirements

This project fulfills all requirements:
- ✅ Generate diverse fictional slot games
- ✅ Build similarity engine for recommendations  
- ✅ Create interactive user interface
- ✅ Implement LLM-powered features
- ✅ Provide comprehensive documentation
