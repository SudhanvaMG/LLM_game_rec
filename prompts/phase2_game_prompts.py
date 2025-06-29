"""
Phase 2: Game Generation Prompts (Hybrid Approach)

Contains prompts for generating complete slot games using sampled attributes
with creative flexibility for realistic and engaging results.
"""

GAME_GENERATION_PROMPT = """
You are an expert slot machine game designer. I will provide you with specific attributes as guidelines, but you have creative freedom to adjust them if needed to create a coherent, engaging game.

ATTRIBUTE GUIDELINES:
Theme: {theme}
Art Style: {art_style}
Music Style: {music_style}
Volatility: {volatility}
Special Features: {special_features}
Developer: {developer}
Complexity Level: {complexity_level}

INSTRUCTIONS:
1. Use the provided attributes as strong guidelines (follow ~80% of them)
2. You may creatively adjust attributes if they don't work well together
3. Create a compelling, realistic slot game that players would want to play
4. Ensure all technical specifications make sense for slot machines
5. Generate rich, engaging descriptions

REQUIRED JSON FORMAT:
{{
    "name": "Creative and memorable game name",
    "description": "Detailed 50-200 word description of the game experience",
    "theme": "Final theme (may be refined from guideline)",
    "volatility": "low|medium|high",
    "rtp": 0.XX, // realistic RTP between 0.85-0.98
    "art_style": "Final art style choice",
    "music_style": "Final music style choice", 
    "reels": 5, // typically 5, but can vary
    "paylines": XX, // realistic number 10-50
    "special_features": ["feature1", "feature2", "feature3"], // 2-4 features
    "has_bonus_round": true/false,
    "has_progressive_jackpot": true/false,
    "max_win_multiplier": XXXX, // realistic multiplier 100x-10000x
    "complexity_level": "Beginner|Intermediate|Advanced",
    "target_demographics": ["demographic1", "demographic2"], // 1-3 demographics
    "release_year": 2024, // or 2023
    "developer": "Final developer name",
    "tags": ["tag1", "tag2", "tag3"] // 2-5 relevant tags
}}

Generate a single, complete slot game now:
"""

BATCH_GAME_GENERATION_PROMPT = """
You are a slot machine game designer. Generate complete slot games for the provided attribute sets.

IMPORTANT: Return ONLY a valid JSON array. Do not add explanations or extra text.

ATTRIBUTE SETS:
{attribute_sets}

Return exactly this JSON structure:
[
  {{
    "name": "Game name",
    "description": "Brief engaging description (50-150 words)",
    "theme": "Theme name",
    "volatility": "low|medium|high",
    "rtp": 0.XX,
    "art_style": "Art style",
    "music_style": "Music style",
    "reels": 5,
    "paylines": 25,
    "special_features": ["feature1", "feature2"],
    "has_bonus_round": true,
    "has_progressive_jackpot": false,
    "max_win_multiplier": 1000,
    "complexity_level": "Beginner|Intermediate|Advanced",
    "target_demographics": ["demo1", "demo2"],
    "release_year": 2024,
    "developer": "Developer name",
    "tags": ["tag1", "tag2"]
  }}
]""" 