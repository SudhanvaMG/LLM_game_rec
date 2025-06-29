"""
Simple Similarity Analysis for Game Recommendations

Minimal similarity prompts focused on core recommendation functionality.
Optimized for 4-hour deliverable with basic but effective comparisons.
"""


LLM_RERANKING_PROMPT = """You are a casino game recommendation expert. Your task is to rerank and select the best game recommendations for a player who just finished playing a specific slot game.

PLAYER'S GAME:
{query_game_overview}

CANDIDATE SIMILAR GAMES:
{candidate_games_text}

TASK: Rerank these {num_candidates} candidate games and select the TOP 3 most suitable recommendations for this player.

RANKING CRITERIA (in order of importance):
1. **Theme & Setting Compatibility** (30%) - Does the theme appeal to the same interests?
2. **Gameplay Mechanics Similarity** (25%) - Similar features, volatility, and play style?
3. **Visual & Audio Harmony** (20%) - Compatible art and music styles?
4. **Player Experience Level** (15%) - Appropriate complexity and target audience?
5. **Risk Profile Match** (10%) - Similar volatility and RTP expectations?

REQUIREMENTS:
- Select exactly 3 games that best match the player's preferences
- Provide a detailed explanation for each recommendation
- Explain why each game is similar and what the player will enjoy
- Consider the player's likely motivations and interests
- Rank them in order of recommendation strength (1=best match)

RESPONSE FORMAT:
```json
{{
  "recommendations": [
    {{
      "rank": 1,
      "game_id": "exact_game_id_from_candidates",
      "similarity_score": 0.95,
      "explanation": "Detailed explanation of why this game is recommended, highlighting specific similarities and what the player will enjoy.",
      "key_similarities": ["theme match", "similar features", "compatible style"],
      "appeal_factors": ["what makes this appealing to the player"]
    }},
    {{
      "rank": 2,
      "game_id": "second_game_id",
      "similarity_score": 0.88,
      "explanation": "...",
      "key_similarities": ["..."],
      "appeal_factors": ["..."]
    }},
    {{
      "rank": 3,
      "game_id": "third_game_id", 
      "similarity_score": 0.82,
      "explanation": "...",
      "key_similarities": ["..."],
      "appeal_factors": ["..."]
    }}
  ],
  "reasoning": "Brief explanation of the overall ranking logic and why these 3 games were selected over the others."
}}
```

Focus on creating recommendations that feel natural and appealing to the player, not just technically similar."""

GAME_OVERVIEW_FOR_EMBEDDING_PROMPT = """You are a casino game copywriter. Create a comprehensive, natural text overview of this slot game that captures its essence for similarity matching.

GAME DATA:
{game_data}

INSTRUCTIONS:
- Write a flowing, natural paragraph (not bullet points)
- Capture the game's theme, mood, and key characteristics
- Include gameplay mechanics and special features naturally
- Mention the target audience and complexity level
- Include visual/audio style and developer context
- Focus on what makes this game unique and appealing
- Keep it comprehensive but readable (150-200 words)

EXAMPLE STYLE:
"[Game Name] is a [volatility] slot that transports players into [theme description]. This [complexity] game from [developer] combines [art style] visuals with [music style] to create [mood]. Players can expect [RTP description] with [special features description]. The game features [technical specs] and appeals to [target audience]. What sets it apart is [unique selling points]."

Write a natural, comprehensive game overview:""" 