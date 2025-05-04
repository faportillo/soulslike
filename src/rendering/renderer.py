# Renderer module for handling all game rendering
import tcod
from utils.colors import *
from .map_renderer import MapRenderer
from .ui_renderer import UIRenderer
from .character_screen import CharacterScreenRenderer

class Renderer:
    def __init__(self, console):
        """Initialize the main renderer with all sub-renderers"""
        self.console = console
        self.map_renderer = MapRenderer(console)
        self.ui_renderer = UIRenderer(console)
        self.character_screen = CharacterScreenRenderer(console)

    def render_all(self, game, player, game_map):
        """Render everything in the game"""
        # Clear the console
        self.console.clear()

        # Get the current map
        current_map = game.levels[game.current_level]

        # Render the map
        self.map_renderer.render_map(current_map, player.x, player.y)
        
        # Render stairs
        self.map_renderer.render_stairs(current_map)
        
        # Render save points
        self.map_renderer.render_save_point(current_map)

        # Render the player
        self.console.print(player.x, player.y, "@", fg=COLOR_PLAYER)

        # Render UI
        self.ui_renderer.render_ui(game, player, current_map)

        # Render character screen if it's visible
        if game.show_character_screen:
            self.character_screen.render(player)

        # Present the console
        tcod.console_flush()

    def get_terrain_color(self, terrain, is_visible, is_outdoor, level=0):
        """Get the appropriate color for terrain based on type, visibility, and level"""
        # Base colors for different terrain types
        base_colors = {
            TERRAIN_WALL: {
                'outdoor': (34, 139, 34),    # Forest green
                'indoor': (80, 80, 120),     # Vibrant blue-gray
                'deep': (60, 60, 100)        # Deep blue-gray
            },
            TERRAIN_GRASS: {
                'outdoor': (34, 139, 34),    # Forest green
                'indoor': (150, 150, 180),   # Bright gray with blue tint
                'deep': (130, 130, 160)      # Slightly darker blue-gray
            },
            TERRAIN_ROCK: {
                'outdoor': (169, 169, 169),  # Dark gray
                'indoor': (180, 140, 100),   # Warm stone color
                'deep': (160, 120, 80)       # Deep warm stone
            },
            TERRAIN_CAVE: {
                'outdoor': (139, 69, 19),    # Brown
                'indoor': (160, 82, 45),     # Sienna
                'deep': (139, 69, 19)        # Brown
            },
            TERRAIN_WATER: {
                'outdoor': (0, 105, 148),    # Deep blue
                'indoor': (0, 150, 200),     # Bright blue
                'deep': (0, 100, 180)        # Deep blue
            },
            TERRAIN_SAND: {
                'outdoor': (238, 214, 175),  # Sand
                'indoor': (255, 228, 196),   # Bisque
                'deep': (245, 222, 179)      # Wheat
            }
        }

        # Get the base color
        if is_outdoor:
            base = base_colors[terrain]['outdoor']
        elif level > 6:
            base = base_colors[terrain]['deep']
        else:
            base = base_colors[terrain]['indoor']

        # Apply visibility modifier
        if not is_visible:
            # Darken the color for unexplored areas
            return tuple(max(0, c // 3) for c in base)
        elif not is_outdoor and level > 0:
            # Add a slight tint based on level
            tint = min(40, level * 6)  # Increased maximum tint to 40
            return tuple(min(255, c + tint) for c in base)
        return base

    def get_outdoor_tile(self, terrain, visible):
        """Get the appropriate color and character for outdoor terrain"""
        if not visible:
            return COLOR_DARK_WALL, " "

        if terrain == TERRAIN_WALL:
            return (34, 139, 34), "#"  # Forest green for trees
        elif terrain == TERRAIN_GRASS:
            return (34, 139, 34), "."  # Green for grass
        elif terrain == TERRAIN_ROCK:
            return (169, 169, 169), "o"  # Dark gray for rocks
        elif terrain == TERRAIN_CAVE:
            return (139, 69, 19), "O"  # Brown for cave
        elif terrain == TERRAIN_WATER:
            return (0, 105, 148), "~"  # Deep blue for water
        elif terrain == TERRAIN_SAND:
            return (238, 214, 175), ","  # Sand color
        else:
            return COLOR_DARK_WALL, " "

    def get_dungeon_tile(self, terrain, visible, level=0):
        """Get the appropriate color and character for dungeon terrain"""
        if not visible:
            return COLOR_DARK_WALL, " "

        # Get the color based on terrain type, visibility, and level
        color = self.get_terrain_color(terrain, visible, False, level)

        if terrain == TERRAIN_WALL:
            return color, "#"  # Walls
        elif terrain == TERRAIN_GRASS:  # Used as floor in dungeon
            return color, "."  # Floor
        elif terrain == TERRAIN_ROCK:
            return color, "#"  # Rocks (now using wall character)
        elif terrain == TERRAIN_CAVE:
            return color, "C"  # Cave
        elif terrain == TERRAIN_WATER:
            return color, "~"  # Water
        elif terrain == TERRAIN_SAND:
            return color, ","  # Sand
        else:
            return COLOR_DARK_WALL, " "

    def render_player(self, player_x, player_y):
        """Render the player character"""
        self.console.print(player_x, player_y, "@", fg=COLOR_PLAYER)

    def render_level(self, level):
        """Render the current level number"""
        self.console.print(0, 0, f"Level: {level}", fg=COLOR_WHITE)

    def render_save_point(self, game_map):
        """Render save points on the map"""
        if game_map.save_point and game_map.visible[game_map.save_point]:
            self.console.print(game_map.save_point[0], game_map.save_point[1], "S", fg=(0, 255, 255))

    def render_messages(self, messages):
        """Render game messages"""
        if messages:
            self.ui_renderer.render_messages(messages) 