# Color definitions for the game
import tcod

# Indoor level colors
COLOR_WALL = (100, 100, 100)  # Gray walls
COLOR_FLOOR = (50, 50, 50)    # Dark gray floor
COLOR_PLAYER = (255, 255, 255)  # White player
COLOR_STAIRS = (255, 255, 255)  # White stairs
COLOR_DARK_WALL = (30, 30, 30)  # Very dark gray for unseen walls
COLOR_DARK_FLOOR = (15, 15, 15)  # Very dark gray for unseen floor
COLOR_DARK_STAIRS = (100, 100, 100)  # Dimmed gray for discovered but unseen stairs

# Outdoor level colors
COLOR_OUTDOOR_WALL = (0, 100, 0)  # Dark green for trees/walls
COLOR_OUTDOOR_GROUND = (144, 238, 144)  # Light green for grass
COLOR_OUTDOOR_STAIRS = (100, 100, 100)  # Gray for cave entrance
COLOR_ROCK = (128, 128, 128)  # Gray for rocks
COLOR_CAVE = (64, 64, 64)  # Dark gray for cave
COLOR_WATER = (0, 0, 255)  # Blue for water
COLOR_SAND = (194, 178, 128)  # Light brown for sand

# Colors
COLOR_LIGHT_WALL = (130, 110, 50)
COLOR_DARK_GROUND = (50, 50, 150)
COLOR_LIGHT_GROUND = (200, 180, 50)
COLOR_ILLUMINATED = (160, 150, 110)  # Even softer, warmer candlelight-like illumination
COLOR_WHITE = (255, 255, 255)

# Outdoor colors
COLOR_OUTDOOR_GROUND = (200, 200, 150)  # Light yellow-green for grass
COLOR_ROCK = (150, 150, 150)  # Gray for rocks
COLOR_CAVE = (80, 80, 80)  # Dark gray for cave
COLOR_SAND = (238, 214, 175)  # Light brown for sand

# Color constants for the game
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_ORANGE = (255, 165, 0)
COLOR_GRAY = (128, 128, 128)

# Game-specific colors
COLOR_PLAYER = (255, 255, 255)  # White
COLOR_DARK_RED = (139, 0, 0)    # Dark red for health bar background
COLOR_DARK_WALL = (0, 0, 100)   # Dark blue for walls
COLOR_LIGHT_WALL = (130, 110, 50)  # Light brown for walls
COLOR_DARK_GROUND = (50, 50, 150)  # Dark blue for ground
COLOR_LIGHT_GROUND = (200, 180, 50)  # Light brown for ground

# Terrain colors
COLOR_OUTDOOR_WALL = (34, 139, 34)    # Forest green for trees
COLOR_OUTDOOR_GROUND = (34, 139, 34)  # Forest green for grass
COLOR_ROCK = (169, 169, 169)          # Dark gray for rocks
COLOR_CAVE = (139, 69, 19)            # Brown for cave
COLOR_WATER = (0, 105, 148)           # Deep blue for water
COLOR_SAND = (238, 214, 175)          # Sand color

# UI colors
COLOR_STAIRS = (255, 215, 0)          # Gold for stairs
COLOR_DARK_STAIRS = (128, 107, 0)     # Dark gold for discovered stairs
COLOR_HEALTH = (255, 0, 0)  # Red for health
COLOR_STAMINA = (0, 255, 0)  # Green for stamina
COLOR_MESSAGE = (255, 255, 255)  # White for messages
COLOR_PLAYER = (255, 255, 0)  # Yellow for player 