# Renderer module for handling all game rendering
import tcod
from utils.colors import *
from core.map import *
from .map_renderer import MapRenderer
from .entity_renderer import EntityRenderer
from .ui_renderer import UIRenderer

class Renderer:
    def __init__(self, console):
        """Initialize the main renderer with all sub-renderers"""
        self.console = console
        self.map_renderer = MapRenderer(console)
        self.entity_renderer = EntityRenderer(console)
        self.ui_renderer = UIRenderer(console)

    def render_all(self, game_map, player, entities, level, messages=None):
        """Render everything in the game"""
        # Clear the console
        self.console.clear()

        # Render the map and its features
        self.map_renderer.render_map(game_map, player.x, player.y)
        self.map_renderer.render_stairs(game_map)

        # Render all entities
        self.entity_renderer.render_entities(entities)
        self.entity_renderer.render_player(player.x, player.y)

        # Render UI elements
        self.ui_renderer.render_level(level)
        if messages:
            self.ui_renderer.render_messages(messages)
        self.ui_renderer.render_status(player)

    def get_terrain_color(self, terrain, is_visible, is_outdoor, level=0):
        """Get the appropriate color for terrain based on type, visibility, and level"""
        # Base colors for different terrain types
        base_colors = {
            TERRAIN_WALL: {
                'outdoor': (34, 139, 34),    # Forest green
                'indoor': (50, 50, 50),      # Dark gray
                'deep': (25, 25, 25)         # Very dark gray
            },
            TERRAIN_GRASS: {
                'outdoor': (34, 139, 34),    # Forest green
                'indoor': (100, 100, 100),   # Light gray
                'deep': (80, 80, 80)         # Darker gray
            },
            TERRAIN_ROCK: {
                'outdoor': (169, 169, 169),  # Dark gray
                'indoor': (169, 169, 169),   # Dark gray
                'deep': (139, 69, 19)        # Brown
            },
            TERRAIN_CAVE: {
                'outdoor': (139, 69, 19),    # Brown
                'indoor': (139, 69, 19),     # Brown
                'deep': (101, 67, 33)        # Dark brown
            },
            TERRAIN_WATER: {
                'outdoor': (0, 105, 148),    # Deep blue
                'indoor': (0, 105, 148),     # Deep blue
                'deep': (0, 0, 139)          # Dark blue
            },
            TERRAIN_SAND: {
                'outdoor': (238, 214, 175),  # Sand
                'indoor': (238, 214, 175),   # Sand
                'deep': (205, 133, 63)       # Peru
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
            tint = min(30, level * 5)  # Maximum tint of 30
            return tuple(min(255, c + tint) for c in base)
        return base

    def render_map(self, game_map, player_x, player_y):
        """Render the game map with proper colors based on visibility"""
        for x in range(game_map.width):
            for y in range(game_map.height):
                # Get the terrain type at this position
                terrain = game_map.tiles[x, y]
                
                # Determine if this tile is visible to the player
                is_visible = game_map.visible[x, y]
                is_explored = game_map.explored[x, y]

                # Get the color based on terrain type, visibility, and level
                color = self.get_terrain_color(terrain, is_visible, game_map.is_outdoor, game_map.level)

                # Choose character based on terrain type
                if terrain == 0:  # Wall
                    char = "#"
                elif terrain == 1:  # Grass/Floor
                    char = "."
                elif terrain == 2:  # Rock
                    char = "O"
                elif terrain == 3:  # Cave
                    char = "C"
                elif terrain == 4:  # Water
                    char = "~"
                elif terrain == 5:  # Sand
                    char = ","
                else:
                    char = "."

                # Only render if the tile is explored
                if is_explored:
                    self.console.print(x, y, char, fg=color)

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
            return color, "O"  # Rocks
        elif terrain == TERRAIN_CAVE:
            return color, "C"  # Cave
        elif terrain == TERRAIN_WATER:
            return color, "~"  # Water
        elif terrain == TERRAIN_SAND:
            return color, ","  # Sand
        else:
            return COLOR_DARK_WALL, " "

    def render_stairs(self, game_map):
        """Render the stairs with proper colors based on discovery and level"""
        # Get stair colors based on level
        if game_map.level > 6:
            visible_color = (255, 140, 0)  # Dark orange for deep levels
            discovered_color = (139, 69, 19)  # Brown for discovered in deep levels
        else:
            visible_color = (255, 215, 0)  # Gold for normal levels
            discovered_color = (128, 107, 0)  # Dark gold for discovered

        # Render up stairs
        if game_map.stairs_up:
            x, y = game_map.stairs_up
            if game_map.visible[x, y]:
                self.console.print(x, y, "^", fg=visible_color)
            elif game_map.stairs_discovered["up"]:
                self.console.print(x, y, "^", fg=discovered_color)

        # Render down stairs
        if game_map.stairs_down:
            x, y = game_map.stairs_down
            if game_map.visible[x, y]:
                self.console.print(x, y, "v", fg=visible_color)
            elif game_map.stairs_discovered["down"]:
                self.console.print(x, y, "v", fg=discovered_color)

        # Ensure there's a path between stairs
        if game_map.stairs_up and game_map.stairs_down:
            if not game_map.path_exists(game_map.stairs_up, game_map.stairs_down):
                game_map.create_direct_path(game_map.stairs_up, game_map.stairs_down)

    def render_player(self, player_x, player_y):
        """Render the player character"""
        self.console.print(player_x, player_y, "@", fg=COLOR_PLAYER)

    def render_level(self, level):
        """Render the current level number"""
        self.console.print(0, 0, f"Level: {level}", fg=COLOR_WHITE) 