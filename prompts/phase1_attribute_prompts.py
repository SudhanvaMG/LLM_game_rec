"""
Phase 1: Attribute Generation Prompts

Contains prompts for the thematic bucketing strategy:
1. Generate core themes
2. Generate thematic features for each theme (key innovation)
3. Generate essential global attributes
"""

THEMES_GENERATION_PROMPT = """
You are a creative game designer working on slot machine themes. I need you to generate a diverse list of engaging themes for casino slot games.

Requirements:
- Generate exactly 12 unique and creative themes
- Each theme should be specific and evocative (not generic)
- Mix popular themes with some unique/creative ones
- Consider themes that would appeal to different demographics
- These themes will be used to generate thematically-coherent special features

Examples of good themes: "Ancient Egypt", "Pirate Treasure", "Space Adventure", "Mystic Forest", "Wild West", "Underwater Kingdom"

Format your response as a simple JSON array:
["Theme 1", "Theme 2", "Theme 3", ...]

Generate the 12 themes now:
"""

THEMATIC_FEATURES_GENERATION_PROMPT = """
You are a game mechanics designer for slot machines. I need you to generate thematically-appropriate special features for a specific slot game theme.

THEME: {theme}

Requirements:
- Generate exactly 6 unique special features that fit perfectly with the {theme} theme
- Each feature should be thematically consistent and immersive
- Mix common slot mechanics with theme-specific creative features
- Features should feel natural and exciting for this theme
- Be specific about what each feature does

Examples for different themes:
- Ancient Egypt: ["Tomb Bonus Round", "Scarab Wild Multipliers", "Curse of the Mummy Re-spins", "Pyramid Free Spins", "Pharaoh's Gold Feature", "Sacred Ankh Wilds"]
- Sci-Fi: ["Hyperspace Jump Bonus", "Alien Invasion Cascades", "Laser Beam Wilds", "Time Warp Feature", "Robot Army Free Spins", "Galactic Multipliers"]
- Pirate: ["Treasure Hunt Bonus", "Kraken Attack Wilds", "Ship Battle Free Spins", "Buried Gold Multipliers", "Cannon Blast Feature", "Pirate's Map Bonus"]

Format your response as a simple JSON array:
["Thematic Feature 1", "Thematic Feature 2", "Thematic Feature 3", ...]

Generate the {theme}-themed special features now:
"""

ART_STYLES_GENERATION_PROMPT = """
You are a visual designer for casino games. I need you to generate a list of distinct art styles that could be used for slot machine games.

Requirements:
- Generate exactly 8 unique art styles
- Each style should be visually distinct and recognizable
- Consider styles that work well for digital slot games
- Mix realistic and stylized approaches
- Think about what appeals to casino game players

Examples: "Realistic 3D", "Cartoon", "Minimalist", "Art Deco", "Pixel Art"

Format your response as a simple JSON array:
["Style 1", "Style 2", "Style 3", ...]

Generate the art styles now:
"""

MUSIC_STYLES_GENERATION_PROMPT = """
You are an audio designer for casino games. I need you to generate a list of music styles that would enhance slot machine gameplay.

Requirements:
- Generate exactly 10 unique music styles
- Each style should create a specific mood/atmosphere
- Consider how music affects player engagement in gambling
- Mix energetic and atmospheric styles
- Be specific about the musical genre/approach

Examples: "Epic Orchestral", "Upbeat Electronic", "Jazzy Lounge", "Mystical Ambient", "Rock Anthem"

Format your response as a simple JSON array:
["Style 1", "Style 2", "Style 3", ...]

Generate the music styles now:
"""

DEVELOPERS_GENERATION_PROMPT = """
You are creating fictional game development studios for slot machines. I need you to generate a list of realistic-sounding casino game developer names.

Requirements:
- Generate exactly 12 unique developer names
- Names should sound professional and gaming-focused
- Mix different naming styles (corporate, creative, geographic)
- Avoid real existing company names
- Make them memorable and appropriate for casino games

Examples: "Golden Reel Studios", "Nexus Gaming", "Crimson Peak Entertainment", "Atlas Game Works"

Format your response as a simple JSON array:
["Developer 1", "Developer 2", "Developer 3", ...]

Generate the developer names now:
""" 