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

        # Create a larger, more visible cave entrance with a clear path
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 < cave_x + dx < self.width - 1 and 0 < cave_y + dy < self.height - 1:
                    if dx*dx + dy*dy <= 4:  # 5x5 cave entrance
                        self.tiles[cave_x + dx, cave_y + dy] = TERRAIN_CAVE
                        # Ensure the edges of the cave entrance are walkable
                        if dx*dx + dy*dy == 4:  # Outer edge
                            self.tiles[cave_x + dx, cave_y + dy] = TERRAIN_GRASS
        
        # Place stairs down in the center of the cave
        self.stairs_down = (cave_x, cave_y)
        
        # Mark everything as visible and explored in outdoor level
        self.visible.fill(True)
        self.explored.fill(True)
        self.stairs_discovered["down"] = True

    def generate_dungeon(self):
        """Generate a dungeon level with multiple rooms and corridors"""
        # Initialize the map with walls
        self.tiles.fill(TERRAIN_WALL)

        # Generate multiple rooms
        num_rooms = random.randint(5, 8)  # Number of rooms to generate
        rooms = []
        min_room_size = 5
        max_room_size = 12

        # Define room types with their probabilities
        room_types = {
            'normal': 0.4,    # Regular room
            'water': 0.15,    # Water pool room
            'sand': 0.15,     # Sandy room
            'rocky': 0.15,    # Rocky room
            'crystal': 0.1,   # Crystal formation room
            'mossy': 0.05    # Mossy room
        }

        for _ in range(num_rooms):
            # Try to place a room
            room_width = random.randint(min_room_size, max_room_size)
            room_height = random.randint(min_room_size, max_room_size)
            room_x = random.randint(1, self.width - room_width - 1)
            room_y = random.randint(1, self.height - room_height - 1)

            # Check if the room overlaps with existing rooms
            new_room = {
                'x': room_x,
                'y': room_y,
                'width': room_width,
                'height': room_height,
                'center_x': room_x + room_width // 2,
                'center_y': room_y + room_height // 2,
                'type': random.choices(list(room_types.keys()), list(room_types.values()))[0]
            }

            # Check for overlap with existing rooms
            overlap = False
            for room in rooms:
                if (new_room['x'] < room['x'] + room['width'] + 2 and
                    new_room['x'] + new_room['width'] + 2 > room['x'] and
                    new_room['y'] < room['y'] + room['height'] + 2 and
                    new_room['y'] + new_room['height'] + 2 > room['y']):
                    overlap = True
                    break

            if not overlap:
                # Create the room with its specific terrain type
                for x in range(room_x, room_x + room_width):
                    for y in range(room_y, room_y + room_height):
                        if new_room['type'] == 'normal':
                            self.tiles[x, y] = TERRAIN_GRASS
                        elif new_room['type'] == 'water':
                            # Create a water pool with some walkable edges
                            if (x == room_x or x == room_x + room_width - 1 or
                                y == room_y or y == room_y + room_height - 1):
                                self.tiles[x, y] = TERRAIN_GRASS
                            else:
                                self.tiles[x, y] = TERRAIN_WATER
                        elif new_room['type'] == 'sand':
                            self.tiles[x, y] = TERRAIN_SAND
                        elif new_room['type'] == 'rocky':
                            # Create a rocky room with scattered rocks
                            if random.random() < 0.2:  # 20% chance for rocks
                                self.tiles[x, y] = TERRAIN_ROCK
                            else:
                                self.tiles[x, y] = TERRAIN_GRASS
                        elif new_room['type'] == 'crystal':
                            # Create a crystal formation room
                            if random.random() < 0.3:  # 30% chance for crystal formations
                                self.tiles[x, y] = TERRAIN_ROCK
                            else:
                                self.tiles[x, y] = TERRAIN_GRASS
                        elif new_room['type'] == 'mossy':
                            # Create a mossy room with scattered rocks and grass
                            if random.random() < 0.15:  # 15% chance for rocks
                                self.tiles[x, y] = TERRAIN_ROCK
                            else:
                                self.tiles[x, y] = TERRAIN_GRASS
                rooms.append(new_room)

        # Connect rooms with corridors
        for i in range(len(rooms) - 1):
            # Get centers of current and next room
            current = rooms[i]
            next_room = rooms[i + 1]

            # Create L-shaped corridor with some variation
            if random.random() < 0.5:
                # Horizontal then vertical
                for x in range(min(current['center_x'], next_room['center_x']),
                             max(current['center_x'], next_room['center_x']) + 1):
                    self.tiles[x, current['center_y']] = TERRAIN_GRASS
                    # Add some random terrain features in corridors
                    if random.random() < 0.1:  # 10% chance for features
                        if random.random() < 0.5:
                            self.tiles[x, current['center_y']] = TERRAIN_SAND
                        else:
                            self.tiles[x, current['center_y']] = TERRAIN_ROCK
                for y in range(min(current['center_y'], next_room['center_y']),
                             max(current['center_y'], next_room['center_y']) + 1):
                    self.tiles[next_room['center_x'], y] = TERRAIN_GRASS
                    # Add some random terrain features in corridors
                    if random.random() < 0.1:  # 10% chance for features
                        if random.random() < 0.5:
                            self.tiles[next_room['center_x'], y] = TERRAIN_SAND
                        else:
                            self.tiles[next_room['center_x'], y] = TERRAIN_ROCK
            else:
                # Vertical then horizontal
                for y in range(min(current['center_y'], next_room['center_y']),
                             max(current['center_y'], next_room['center_y']) + 1):
                    self.tiles[current['center_x'], y] = TERRAIN_GRASS
                    # Add some random terrain features in corridors
                    if random.random() < 0.1:  # 10% chance for features
                        if random.random() < 0.5:
                            self.tiles[current['center_x'], y] = TERRAIN_SAND
                        else:
                            self.tiles[current['center_x'], y] = TERRAIN_ROCK
                for x in range(min(current['center_x'], next_room['center_x']),
                             max(current['center_x'], next_room['center_x']) + 1):
                    self.tiles[x, next_room['center_y']] = TERRAIN_GRASS
                    # Add some random terrain features in corridors
                    if random.random() < 0.1:  # 10% chance for features
                        if random.random() < 0.5:
                            self.tiles[x, next_room['center_y']] = TERRAIN_SAND
                        else:
                            self.tiles[x, next_room['center_y']] = TERRAIN_ROCK

        # Add some random pillars and decorations
        for _ in range(random.randint(3, 6)):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[x, y] == TERRAIN_GRASS:
                self.tiles[x, y] = TERRAIN_ROCK

        # Add some small water pools in corridors
        for _ in range(random.randint(2, 4)):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[x, y] == TERRAIN_GRASS:
                # Create a small water pool with varying shapes
                pool_shape = random.choice(['square', 'cross', 'plus'])
                if pool_shape == 'square':
                    # 2x2 water pool
                    for dx in range(2):
                        for dy in range(2):
                            if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                                self.tiles[x + dx, y + dy] = TERRAIN_WATER
                elif pool_shape == 'cross':
                    # Cross-shaped water pool
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_WATER
                else:  # plus
                    # Plus-shaped water pool
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_WATER

        # Add some sand patches in corridors
        for _ in range(random.randint(2, 4)):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[x, y] == TERRAIN_GRASS:
                # Create a small sand patch with varying shapes
                patch_shape = random.choice(['square', 'cross', 'plus'])
                if patch_shape == 'square':
                    # 2x2 sand patch
                    for dx in range(2):
                        for dy in range(2):
                            if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                                self.tiles[x + dx, y + dy] = TERRAIN_SAND
                elif patch_shape == 'cross':
                    # Cross-shaped sand patch
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_SAND
                else:  # plus
                    # Plus-shaped sand patch
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_SAND

        # Add some crystal formations
        for _ in range(random.randint(2, 4)):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[x, y] == TERRAIN_GRASS:
                # Create a crystal formation with varying shapes
                crystal_shape = random.choice(['single', 'cluster', 'line'])
                if crystal_shape == 'single':
                    self.tiles[x, y] = TERRAIN_ROCK
                elif crystal_shape == 'cluster':
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_ROCK
                else:  # line
                    direction = random.choice(['horizontal', 'vertical'])
                    length = random.randint(2, 4)
                    for i in range(length):
                        if direction == 'horizontal':
                            if 0 < x + i < self.width - 1:
                                self.tiles[x + i, y] = TERRAIN_ROCK
                        else:
                            if 0 < y + i < self.height - 1:
                                self.tiles[x, y + i] = TERRAIN_ROCK

        # Place stairs based on level
        if self.level > 0:  # Not the first level
            # Place up stairs in the first room
            if rooms:
                room = rooms[0]
                # Find a walkable spot in the room
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        x, y = room['center_x'] + dx, room['center_y'] + dy
                        if self.is_walkable(x, y):
                            self.stairs_up = (x, y)
                            break
                    if self.stairs_up:
                        break
        
        if self.level < 9:  # Not the last level
            # Place down stairs in the last room
            if rooms:
                room = rooms[-1]
                # Find a walkable spot in the room
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        x, y = room['center_x'] + dx, room['center_y'] + dy
                        if self.is_walkable(x, y):
                            self.stairs_down = (x, y)
                            break
                    if self.stairs_down:
                        break

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
        # Make cave terrain walkable only in outdoor level
        if self.is_outdoor:
            return self.tiles[x, y] not in [TERRAIN_WALL, TERRAIN_WATER, TERRAIN_ROCK] or self.tiles[x, y] == TERRAIN_CAVE
        else:
            return self.tiles[x, y] not in [TERRAIN_WALL, TERRAIN_WATER, TERRAIN_ROCK]

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