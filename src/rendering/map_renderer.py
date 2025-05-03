import tcod
from utils.colors import *

class MapRenderer:
    def __init__(self, console):
        """Initialize the map renderer with a console"""
        self.console = console

    def render_map(self, game_map, player_x, player_y):
        """Render the game map with proper colors based on visibility"""
        for x in range(game_map.width):
            for y in range(game_map.height):
                # Get the terrain type at this position
                terrain = game_map.tiles[x, y]
                
                # Determine if this tile is visible to the player
                is_visible = game_map.visible[x, y]
                is_explored = game_map.explored[x, y]

                # Get color and character based on terrain type and visibility
                if game_map.is_outdoor:
                    color, char = self.get_outdoor_tile(terrain, is_visible)
                else:
                    color, char = self.get_dungeon_tile(terrain, is_visible)

                # Only render if the tile is explored
                if is_explored:
                    self.console.print(x, y, char, fg=color)

    def get_outdoor_tile(self, terrain, visible):
        """Get the appropriate color and character for outdoor terrain"""
        if not visible:
            return COLOR_DARK_WALL, " "

        if terrain == 0:  # Wall
            return COLOR_OUTDOOR_WALL, "#"  # Trees
        elif terrain == 1:  # Grass
            return COLOR_OUTDOOR_GROUND, "."
        elif terrain == 2:  # Rock
            return COLOR_ROCK, "o"
        elif terrain == 3:  # Cave
            return COLOR_CAVE, "O"
        elif terrain == 4:  # Water
            return COLOR_WATER, "~"
        elif terrain == 5:  # Sand
            return COLOR_SAND, ","
        else:
            return COLOR_DARK_WALL, " "

    def get_dungeon_tile(self, terrain, visible):
        """Get the appropriate color and character for dungeon terrain"""
        if not visible:
            return COLOR_DARK_WALL, " "

        if terrain == 0:  # Wall
            return COLOR_WALL, "#"
        elif terrain == 1:  # Floor
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