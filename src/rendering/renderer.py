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
                    else:  # Floor
                        color = COLOR_FLOOR if is_visible else COLOR_DARK_FLOOR

                # Choose character based on terrain type
                if terrain == 0:  # Wall
                    char = "#"
                elif terrain == 1:  # Grass
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
            return COLOR_OUTDOOR_WALL, "#"  # Trees
        elif terrain == TERRAIN_GRASS:
            return COLOR_OUTDOOR_GROUND, "."
        elif terrain == TERRAIN_ROCK:
            return COLOR_ROCK, "o"
        elif terrain == TERRAIN_CAVE:
            return COLOR_CAVE, "O"
        elif terrain == TERRAIN_WATER:
            return COLOR_WATER, "~"
        elif terrain == TERRAIN_SAND:
            return COLOR_SAND, ","
        else:
            return COLOR_DARK_WALL, " "

    def get_dungeon_tile(self, terrain, visible):
        """Get the appropriate color and character for dungeon terrain"""
        if not visible:
            return COLOR_DARK_WALL, " "

        if terrain == TERRAIN_WALL:
            return COLOR_WALL, "#"
        elif terrain == TERRAIN_GRASS:  # Used as floor in dungeon
            return COLOR_FLOOR, "."
        else:
            return COLOR_DARK_WALL, " "

    def render_stairs(self, game_map):
        """Render the stairs with proper colors based on discovery"""
        # Render up stairs
        if game_map.stairs_up:
            x, y = game_map.stairs_up
            if game_map.visible[x, y]:
                self.console.print(x, y, "^", fg=COLOR_STAIRS)
            elif game_map.stairs_discovered["up"]:
                self.console.print(x, y, "^", fg=COLOR_DARK_STAIRS)

        # Render down stairs
        if game_map.stairs_down:
            x, y = game_map.stairs_down
            if game_map.visible[x, y]:
                self.console.print(x, y, "v", fg=COLOR_STAIRS)
            elif game_map.stairs_discovered["down"]:
                self.console.print(x, y, "v", fg=COLOR_DARK_STAIRS)

    def render_player(self, player_x, player_y):
        """Render the player character"""
        self.console.print(player_x, player_y, "@", fg=COLOR_PLAYER)

    def render_level(self, level):
        """Render the current level number"""
        self.console.print(0, 0, f"Level: {level}", fg=COLOR_WHITE) 