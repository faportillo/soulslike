import tcod
from utils.colors import *
from core.map import *

class MapRenderer:
    def __init__(self, console):
        """Initialize the map renderer with a console"""
        self.console = console
        self.game_map = None
        self.x = 0
        self.y = 0

    def render_map(self, game_map, player_x, player_y):
        """Render the game map"""
        self.game_map = game_map
        for x in range(game_map.width):
            for y in range(game_map.height):
                self.x = x
                self.y = y
                is_visible = game_map.visible[x, y]
                is_explored = game_map.explored[x, y]
                
                if not is_explored:
                    continue
                
                terrain = game_map.tiles[x, y]
                if game_map.is_outdoor:
                    color, char = self.get_outdoor_tile(terrain, is_visible)
                else:
                    color, char = self.get_dungeon_tile(terrain, is_visible, game_map.level)
                
                self.console.print(x, y, char, fg=color)

    def render_stairs(self, game_map):
        """Render stairs on the map"""
        if game_map.stairs_up and game_map.visible[game_map.stairs_up]:
            self.console.print(game_map.stairs_up[0], game_map.stairs_up[1], "<", fg=(255, 255, 0))
        if game_map.stairs_down and game_map.visible[game_map.stairs_down]:
            self.console.print(game_map.stairs_down[0], game_map.stairs_down[1], ">", fg=(255, 255, 0))

    def render_save_point(self, game_map):
        """Render save points on the map"""
        if game_map.save_point and game_map.visible[game_map.save_point]:
            self.console.print(game_map.save_point[0], game_map.save_point[1], "S", fg=(0, 255, 255))

    def get_outdoor_tile(self, terrain, visible):
        """Get the appropriate color and character for outdoor terrain"""
        if not visible:
            return COLOR_DARK_WALL, " "

        # First check if this is a cave marker
        if self.game_map and self.game_map.stairs_down:
            cave_x, cave_y = self.game_map.stairs_down
            if abs(self.x - cave_x) <= 1 and abs(self.y - cave_y) <= 1:
                if self.x == cave_x and self.y == cave_y:
                    return (139, 69, 19), "O"  # Brown 'O' for cave entrance
                else:
                    return (255, 0, 0), "0"  # Red '0' for markers

        # If not a cave marker, handle normal terrain
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
        elif terrain == TERRAIN_MOSS:
            return (34, 139, 34), "m"  # Green for moss
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