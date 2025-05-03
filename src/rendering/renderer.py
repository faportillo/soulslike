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

        # Present the console
        self.console.present()

    def render_map(self, game_map, player_x, player_y):
        """Render the game map with proper colors based on visibility"""
        for x in range(game_map.width):
            for y in range(game_map.height):
                # Get the terrain type at this position
                terrain = game_map.tiles[x, y]
                
                # Determine if this tile is visible to the player
                is_visible = game_map.visible[x, y]
                is_explored = game_map.explored[x, y]

                # Choose color based on terrain type and visibility
                if game_map.is_outdoor:
                    # Outdoor level colors
                    if terrain == 0:  # Wall
                        color = COLOR_OUTDOOR_WALL
                    elif terrain == 1:  # Grass
                        color = COLOR_OUTDOOR_GROUND
                    elif terrain == 2:  # Rock
                        color = COLOR_ROCK
                    elif terrain == 3:  # Cave
                        color = COLOR_CAVE
                    elif terrain == 4:  # Water
                        color = COLOR_WATER
                    elif terrain == 5:  # Sand
                        color = COLOR_SAND
                else:
                    # Indoor level colors
                    if terrain == 0:  # Wall
                        color = COLOR_WALL if is_visible else COLOR_DARK_WALL
                    elif terrain == 1:  # Grass/Floor
                        color = COLOR_FLOOR if is_visible else COLOR_DARK_FLOOR
                    elif terrain == 2:  # Rock
                        color = (100, 100, 100) if is_visible else (50, 50, 50)  # Gray
                    elif terrain == 3:  # Cave
                        color = (139, 69, 19) if is_visible else (69, 34, 9)  # Brown
                    elif terrain == 4:  # Water
                        color = (0, 105, 148) if is_visible else (0, 52, 74)  # Deep blue
                    elif terrain == 5:  # Sand
                        color = (238, 214, 175) if is_visible else (119, 107, 87)  # Sand color

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

    def get_dungeon_tile(self, terrain, visible):
        """Get the appropriate color and character for dungeon terrain"""
        if not visible:
            return COLOR_DARK_WALL, " "

        if terrain == TERRAIN_WALL:
            return (50, 50, 50), "#"  # Dark gray for walls
        elif terrain == TERRAIN_GRASS:  # Used as floor in dungeon
            return (100, 100, 100), "."  # Light gray for floor
        elif terrain == TERRAIN_ROCK:
            return (169, 169, 169), "O"  # Dark gray for rocks
        elif terrain == TERRAIN_CAVE:
            return (139, 69, 19), "C"  # Brown for cave
        elif terrain == TERRAIN_WATER:
            return (0, 105, 148), "~"  # Deep blue for water
        elif terrain == TERRAIN_SAND:
            return (238, 214, 175), ","  # Sand color
        else:
            return COLOR_DARK_WALL, " "

    def render_stairs(self, game_map):
        """Render the stairs with proper colors based on discovery"""
        # Render up stairs
        if game_map.stairs_up:
            x, y = game_map.stairs_up
            if game_map.visible[x, y]:
                self.console.print(x, y, "^", fg=(255, 215, 0))  # Gold color for visible stairs
            elif game_map.stairs_discovered["up"]:
                self.console.print(x, y, "^", fg=(128, 107, 0))  # Dark gold for discovered stairs

        # Render down stairs
        if game_map.stairs_down:
            x, y = game_map.stairs_down
            if game_map.visible[x, y]:
                self.console.print(x, y, "v", fg=(255, 215, 0))  # Gold color for visible stairs
            elif game_map.stairs_discovered["down"]:
                self.console.print(x, y, "v", fg=(128, 107, 0))  # Dark gold for discovered stairs

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