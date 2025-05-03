# Map generation and management module
import numpy as np
import random
import tcod
from tcod import libtcodpy

# Terrain type constants
TERRAIN_WALL = 0    # Walls/trees that block movement
TERRAIN_GRASS = 1   # Walkable ground
TERRAIN_ROCK = 2    # Rock formations that block movement
TERRAIN_CAVE = 3    # Cave entrance/floor
TERRAIN_WATER = 4   # Water that blocks movement
TERRAIN_SAND = 5    # Walkable sand

class Map:
    def __init__(self, width, height, level):
        """Initialize a new map with given dimensions and level number"""
        self.width = width
        self.height = height
        self.level = level
        # Initialize arrays for terrain, visibility, and exploration
        self.tiles = np.full((width, height), fill_value=TERRAIN_WALL, dtype=np.int8)  # Terrain type
        self.visible = np.full((width, height), fill_value=False, dtype=bool)  # Currently visible tiles
        self.explored = np.full((width, height), fill_value=False, dtype=bool)  # Previously seen tiles
        self.stairs_up = None  # Position of stairs going up
        self.stairs_down = None  # Position of stairs going down
        self.stairs_discovered = {"up": False, "down": False}  # Track discovered stairs
        self.is_outdoor = level == 0  # First level is outdoor
        self.spawn_point = None  # Player spawn point for outdoor level
        self.generate()  # Generate the map

    def generate(self):
        """Generate a map with rooms and corridors"""
        if self.is_outdoor:
            self.generate_outdoor()
        else:
            self.generate_dungeon()

    def generate_outdoor(self):
        """Generate an outdoor map with full illumination"""
        # Create a large open area with grass
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                self.tiles[x, y] = TERRAIN_GRASS

        # Add trees around the edges
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.tiles[x, y] = TERRAIN_WALL

        # Add some random rock formations
        for _ in range(8):  # Increased number of rock formations
            rock_x = random.randint(2, self.width - 3)
            rock_y = random.randint(2, self.height - 3)
            rock_size = random.randint(3, 6)  # Larger rock formations
            for dx in range(-rock_size, rock_size + 1):
                for dy in range(-rock_size, rock_size + 1):
                    if 0 < rock_x + dx < self.width - 1 and 0 < rock_y + dy < self.height - 1:
                        if random.random() < 0.7:  # 70% chance to place rock
                            self.tiles[rock_x + dx, rock_y + dy] = TERRAIN_ROCK

        # Add a larger lake
        lake_x = random.randint(10, self.width - 20)
        lake_y = random.randint(10, self.height - 20)
        lake_size = random.randint(5, 8)  # Larger lake
        for dx in range(-lake_size, lake_size + 1):
            for dy in range(-lake_size, lake_size + 1):
                if 0 < lake_x + dx < self.width - 1 and 0 < lake_y + dy < self.height - 1:
                    if dx*dx + dy*dy <= lake_size*lake_size:  # Circular lake
                        self.tiles[lake_x + dx, lake_y + dy] = TERRAIN_WATER

        # Add sand around the lake
        for dx in range(-lake_size-2, lake_size + 3):
            for dy in range(-lake_size-2, lake_size + 3):
                if 0 < lake_x + dx < self.width - 1 and 0 < lake_y + dy < self.height - 1:
                    if dx*dx + dy*dy <= (lake_size+2)*(lake_size+2):
                        if self.tiles[lake_x + dx, lake_y + dy] == TERRAIN_GRASS:
                            self.tiles[lake_x + dx, lake_y + dy] = TERRAIN_SAND

        # Create a cave entrance
        cave_x = random.randint(10, self.width - 11)
        cave_y = random.randint(10, self.height - 11)
        # Make sure cave is not in water
        while self.tiles[cave_x, cave_y] == TERRAIN_WATER:
            cave_x = random.randint(10, self.width - 11)
            cave_y = random.randint(10, self.height - 11)
        
        # Find a safe spawn point away from the cave
        min_distance = 20  # Minimum distance from cave
        max_attempts = 100
        for _ in range(max_attempts):
            spawn_x = random.randint(5, self.width - 6)
            spawn_y = random.randint(5, self.height - 6)
            # Check if spawn point is walkable and far enough from cave
            if (self.is_walkable(spawn_x, spawn_y) and 
                (spawn_x - cave_x)**2 + (spawn_y - cave_y)**2 >= min_distance**2):
                self.spawn_point = (spawn_x, spawn_y)
                break
        
        # If no suitable spawn point found, place in a corner
        if not self.spawn_point:
            self.spawn_point = (5, 5)

        # Create a larger, more visible cave entrance
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 < cave_x + dx < self.width - 1 and 0 < cave_y + dy < self.height - 1:
                    if dx*dx + dy*dy <= 4:  # 5x5 cave entrance
                        self.tiles[cave_x + dx, cave_y + dy] = TERRAIN_CAVE
        
        # Place stairs down in the center of the cave
        self.stairs_down = (cave_x, cave_y)
        
        # Mark everything as visible and explored in outdoor level
        self.visible.fill(True)
        self.explored.fill(True)
        self.stairs_discovered["down"] = True

    def generate_dungeon(self):
        """Generate a dungeon level with rooms and corridors"""
        # Create a simple room
        room_width = random.randint(10, 20)
        room_height = random.randint(10, 20)
        room_x = random.randint(1, self.width - room_width - 1)
        room_y = random.randint(1, self.height - room_height - 1)

        # Create the main room
        for x in range(room_x, room_x + room_width):
            for y in range(room_y, room_y + room_height):
                self.tiles[x, y] = TERRAIN_GRASS  # Using TERRAIN_GRASS as floor in dungeon

        # Place stairs based on level
        if self.level > 0:  # Not the first level
            self.stairs_up = (room_x + 1, room_y + 1)
        
        if self.level < 9:  # Not the last level
            self.stairs_down = (room_x + room_width - 2, room_y + room_height - 2)

    def is_stairs(self, x, y):
        """Check if a position contains stairs and mark them as discovered"""
        if self.stairs_up and (x, y) == self.stairs_up:
            self.stairs_discovered["up"] = True
            return "up"
        if self.stairs_down and (x, y) == self.stairs_down:
            self.stairs_discovered["down"] = True
            return "down"
        return None

    def check_stairs_discovery(self):
        """Check if stairs are in the current field of view and mark them as discovered"""
        if self.stairs_up and self.visible[self.stairs_up]:
            self.stairs_discovered["up"] = True
        if self.stairs_down and self.visible[self.stairs_down]:
            self.stairs_discovered["down"] = True

    def is_walkable(self, x, y):
        """Check if a position is walkable"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tiles[x, y] not in [TERRAIN_WALL, TERRAIN_WATER, TERRAIN_ROCK] or self.tiles[x, y] == TERRAIN_CAVE

    def update_fov(self, player_x, player_y):
        """Update the field of view based on player position"""
        if self.is_outdoor:
            return  # No need to update FOV for outdoor level
        
        # Create a new FOV map
        fov_map = tcod.map.Map(self.width, self.height)
        
        # Set the walls in the FOV map
        for x in range(self.width):
            for y in range(self.height):
                fov_map.transparent[y, x] = self.is_walkable(x, y)
                fov_map.walkable[y, x] = self.is_walkable(x, y)
        
        # Compute the FOV
        fov_map.compute_fov(
            player_x,
            player_y,
            radius=6,  # FOV radius
            light_walls=True,  # Light up walls in FOV
            algorithm=libtcodpy.FOV_BASIC
        )
        
        # Update the visible tiles (transpose to match our coordinate system)
        self.visible = fov_map.fov.T
        self.explored |= self.visible  # Mark visible tiles as explored
        self.check_stairs_discovery()  # Check for discovered stairs 