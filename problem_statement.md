# Problem Statement: LLM-Powered Game Recommender Prototype

## Assignment Overview
**Role:** R&D Software Engineer at Bally's Gaming  
**Duration:** 4 hours (time-boxed)  
**Focus:** Rapid prototyping and problem-solving approach using AI tools

## Business Context
Enhance player experience on Bally's online casino site by showing personalized game recommendations after a player finishes a slot game. The component should display: *"Because you played [Game X], you might like..."* followed by similar games.

## Core Challenge
Build a web application prototype that demonstrates LLM-powered game similarity recommendations using a rich, generated dataset.

## Technical Objectives

### 1. AI-Powered Data Generation
- **Task:** Create a dataset of 100+ fictional casino slot games using an LLM
- **Implementation:** Write a script (e.g., `generate_data.py`) that leverages LLM capabilities
- **Key Requirements:**
  - Define a comprehensive schema for game attributes
  - Choose features important for similarity (theme, volatility, special features, art style, etc.)
  - Generate varied and plausible game catalog
  - Save to structured format (JSON/CSV)

### 2. Similarity Engine Development
- **Task:** Build core recommendation function
- **Input:** A "played game" from the dataset
- **Output:** Top 3-5 most similar games
- **Challenge:** Design robust LLM-based similarity comparison method

### 3. Interactive User Interface
- **Framework:** Streamlit or Gradio
- **Features:**
  - Dropdown/list of all available games
  - Display top 3-5 recommendations upon selection
  - Show LLM-generated explanations for each recommendation
  - Example: *"Like Pharaoh's Fortune, this game features Ancient Egypt theme and high-volatility free spins"*

## Evaluation Criteria

### Primary Focus Areas
1. **Problem-Solving & Creativity**
   - Game schema design decisions
   - Modeling approach and assumptions
   - Creative use of LLM capabilities

2. **AI for Data Synthesis**
   - Effectiveness of LLM usage for dataset generation
   - Quality and diversity of generated data
   - Prompt engineering approach

3. **Pragmatism & Focus**
   - Time management within 4-hour constraint
   - Working proof-of-concept delivery
   - Appropriate technical choices for scope

4. **Technical Implementation**
   - Code clarity and organization
   - Effective LLM integration
   - Practical considerations (API key management, environment variables)

5. **Communication**
   - Clear README.md documentation
   - Explanation of approach and design decisions
   - Trade-offs and limitations acknowledgment

## Technical Specifications

### Required Stack
- **Language:** Python
- **UI Framework:** Streamlit or Gradio
- **LLM Provider:** Any major provider (OpenAI, Anthropic, Google)
- **API:** Use personal API key

### Deliverables
Git repository containing:
- [ ] All source code
- [ ] Data generation script (`generate_data.py`)
- [ ] Generated dataset file (`games.json` or `games.csv`)
- [ ] Requirements file (`requirements.txt`)
- [ ] Comprehensive README.md with:
  - Setup and run instructions
  - Approach explanation
  - Design decisions rationale
  - Trade-offs and limitations

## Success Metrics
- **Functional:** Working prototype within 4 hours
- **Technical:** Clean, understandable code with effective LLM usage
- **Creative:** Thoughtful game schema and similarity approach
- **Practical:** Realistic recommendations with clear explanations

## Key Considerations
- This is a **proof-of-concept**, not production-ready code
- Focus on **approach and problem-solving** over perfect implementation
- Demonstrate **rapid prototyping skills** typical of R&D environment
- Show **pragmatic use of AI tools** for data generation and similarity matching

---

*Note: This assignment tests your ability to quickly leverage AI tools for practical problem-solving in a gaming context, reflecting the fast-paced nature of R&D work.* 