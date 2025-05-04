# Map generation and management module
import numpy as np
import random
import tcod
from tcod import libtcodpy
import math

# Terrain type constants
TERRAIN_WALL = 0    # Walls/trees that block movement
TERRAIN_GRASS = 1   # Walkable ground
TERRAIN_ROCK = 2    # Rock formations that block movement
TERRAIN_CAVE = 3    # Cave entrance/floor
TERRAIN_WATER = 4   # Water that blocks movement
TERRAIN_SAND = 5    # Walkable sand
TERRAIN_MOSS = 6    # Mossy ground

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
        self.save_point = None  # Save point for the level
        self.npcs = []  # List of NPCs in the level
        self.generate()  # Generate the map

    def generate(self):
        """Generate a map with rooms and corridors"""
        if self.is_outdoor:
            self.generate_outdoor()
        else:
            self.generate_dungeon(self.level)

    def generate_outdoor(self):
        """Generate an outdoor map with natural features"""
        # Initialize the map with grass
        self.tiles.fill(TERRAIN_GRASS)
        
        # Set spawn point at top left
        spawn_x = 2
        spawn_y = 2
        self.spawn_point = (spawn_x, spawn_y)
        self.tiles[spawn_x, spawn_y] = TERRAIN_GRASS
        
        # Set cave entrance position at bottom right
        cave_x = self.width - 8
        cave_y = self.height - 8
        self.stairs_down = (cave_x, cave_y)  # Set the stairs_down position
        
        # Create a large open area in the center
        center_x = self.width // 2
        center_y = self.height // 2
        open_radius = min(self.width, self.height) // 4
        
        for x in range(self.width):
            for y in range(self.height):
                # Create a more natural-looking open area
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance < open_radius:
                    # Add some variation to the center
                    if random.random() < 0.8:  # 80% chance to be grass
                        self.tiles[x, y] = TERRAIN_GRASS
                    else:
                        self.tiles[x, y] = TERRAIN_SAND
        
        # Create a large water body in the center
        water_radius = open_radius // 2
        for x in range(self.width):
            for y in range(self.height):
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance < water_radius:
                    self.tiles[x, y] = TERRAIN_WATER
        
        # Add rock formations
        for _ in range(20):  # Reduced number but larger formations
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            rock_size = random.randint(3, 6)  # Larger rock formations
            
            # Create more natural-looking rock clusters
            for dx in range(-rock_size, rock_size + 1):
                for dy in range(-rock_size, rock_size + 1):
                    if (0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1):
                        # Use a smoother falloff for more natural shapes
                        if random.random() < 0.7 * (1 - (dx*dx + dy*dy)/(rock_size*rock_size)):
                            self.tiles[x + dx, y + dy] = TERRAIN_ROCK
        
        # Add moss patches in natural clusters
        for _ in range(15):  # Reduced number but larger patches
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            moss_size = random.randint(2, 4)
            
            # Create more natural moss clusters
            for dx in range(-moss_size, moss_size + 1):
                for dy in range(-moss_size, moss_size + 1):
                    if (0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1):
                        # Higher density in center, fading out
                        if random.random() < 0.8 * (1 - (dx*dx + dy*dy)/(moss_size*moss_size)):
                            self.tiles[x + dx, y + dy] = TERRAIN_MOSS
        
        # Add sand patches in natural formations
        for _ in range(10):  # Reduced number but larger patches
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            sand_size = random.randint(2, 5)
            
            for dx in range(-sand_size, sand_size + 1):
                for dy in range(-sand_size, sand_size + 1):
                    if (0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1 and
                        dx*dx + dy*dy <= sand_size*sand_size):
                        # Create more natural sand patterns
                        if random.random() < 0.6 * (1 - (dx*dx + dy*dy)/(sand_size*sand_size)):
                            self.tiles[x + dx, y + dy] = TERRAIN_SAND
        
        # Add some small water features near the main water body
        water_center_x = self.width // 2
        water_center_y = self.height // 2
        for _ in range(3):  # Add a few small water features
            angle = random.uniform(0, 2 * 3.14159)  # Random angle
            distance = random.randint(8, 15)  # Distance from main water
            x = int(water_center_x + distance * math.cos(angle))
            y = int(water_center_y + distance * math.sin(angle))
            
            if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                # Create small water features
                water_size = random.randint(2, 3)
                for dx in range(-water_size, water_size + 1):
                    for dy in range(-water_size, water_size + 1):
                        if (0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1 and
                            dx*dx + dy*dy <= water_size*water_size):
                            if random.random() < 0.7:  # 70% chance to place water
                                self.tiles[x + dx, y + dy] = TERRAIN_WATER
        
        # Mark everything as visible and explored in outdoor level
        self.visible.fill(True)
        self.explored.fill(True)
        self.stairs_discovered["down"] = True
        
        # Create a winding path from spawn to cave
        path_points = []
        current_x, current_y = self.spawn_point
        
        while (current_x, current_y) != (cave_x, cave_y):
            path_points.append((current_x, current_y))
            
            # Calculate direction to target
            dx = cave_x - current_x
            dy = cave_y - current_y
            
            # Add some winding to the path
            if random.random() < 0.6:  # 60% chance to add a detour
                if abs(dx) > abs(dy):
                    current_x += 1 if dx > 0 else -1
                    if random.random() < 0.3:  # 30% chance to move vertically
                        current_y += random.choice([-1, 1])
                else:
                    current_y += 1 if dy > 0 else -1
                    if random.random() < 0.3:  # 30% chance to move horizontally
                        current_x += random.choice([-1, 1])
            else:
                # Move towards target
                if abs(dx) > abs(dy):
                    current_x += 1 if dx > 0 else -1
                else:
                    current_y += 1 if dy > 0 else -1
            
            # Ensure we don't go out of bounds
            current_x = max(1, min(current_x, self.width - 2))
            current_y = max(1, min(current_y, self.height - 2))
        
        # Add the final point
        path_points.append((cave_x, cave_y))
        
        # Create the path with varying width
        path_tiles = set()
        for x, y in path_points:
            # Calculate path width based on distance from cave
            distance = math.sqrt((x - cave_x) ** 2 + (y - cave_y) ** 2)
            max_width = 4  # Maximum width at the start
            min_width = 2  # Minimum width near the cave
            path_width = int(max_width - (max_width - min_width) * (1 - distance / (self.width + self.height)))
            
            for dx in range(-path_width, path_width + 1):
                for dy in range(-path_width, path_width + 1):
                    if (0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1):
                        if random.random() < 0.8:  # 80% chance to place path tile
                            self.tiles[x + dx, y + dy] = TERRAIN_SAND
                            path_tiles.add((x + dx, y + dy))
        
        # Fill non-path areas with rocks and trees
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) not in path_tiles:
                    if random.random() < 0.1:  # 10% chance for trees
                        self.tiles[x, y] = TERRAIN_WALL  # Trees
                    elif random.random() < 0.05:  # 5% chance for rocks
                        self.tiles[x, y] = TERRAIN_ROCK  # Rocks
        
        # Handle save point placement
        if hasattr(self, 'save_point') and self.save_point:
            # Use the existing save point
            save_x, save_y = self.save_point
            self.tiles[save_x, save_y] = TERRAIN_GRASS  # Clear the save point tile
            
            # Create a path to the save point if it's not already on a path
            if (save_x, save_y) not in path_tiles:
                # Find the closest point on the main path
                closest_point = min(path_points, key=lambda p: (p[0] - save_x)**2 + (p[1] - save_y)**2)
                
                # Create a path from the closest point to the save point
                current_x, current_y = closest_point
                save_path_points = []
                
                while (current_x, current_y) != (save_x, save_y):
                    save_path_points.append((current_x, current_y))
                    
                    # Calculate direction to save point
                    dx = save_x - current_x
                    dy = save_y - current_y
                    
                    # Move towards save point
                    if abs(dx) > abs(dy):
                        current_x += 1 if dx > 0 else -1
                    else:
                        current_y += 1 if dy > 0 else -1
                    
                    # Ensure we don't go out of bounds
                    current_x = max(1, min(current_x, self.width - 2))
                    current_y = max(1, min(current_y, self.height - 2))
                
                # Add the final point
                save_path_points.append((save_x, save_y))
                
                # Create the save point path
                for x, y in save_path_points:
                    path_width = 2
                    for dx in range(-path_width, path_width + 1):
                        for dy in range(-path_width, path_width + 1):
                            if (0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1):
                                if random.random() < 0.8:  # 80% chance to place path tile
                                    self.tiles[x + dx, y + dy] = TERRAIN_SAND
                                    path_tiles.add((x + dx, y + dy))
        else:
            # Create a new save point if none exists
            # Choose a point on the main path about 1/3 of the way from start
            branch_point = path_points[len(path_points) // 3]
            
            # Calculate direction towards bottom left
            target_x = max(5, branch_point[0] - random.randint(8, 12))  # Move left
            target_y = min(self.height - 5, branch_point[1] + random.randint(8, 12))  # Move down
            
            # Ensure the save point is within bounds
            save_x = max(5, min(target_x, self.width - 5))
            save_y = max(5, min(target_y, self.height - 5))
            
            # Create a path to the save point
            current_x, current_y = branch_point
            save_path_points = []
            
            while (current_x, current_y) != (save_x, save_y):
                save_path_points.append((current_x, current_y))
                
                # Calculate direction to save point
                dx = save_x - current_x
                dy = save_y - current_y
                
                # Add some winding to the path
                if random.random() < 0.6:  # 60% chance to add a detour
                    if abs(dx) > abs(dy):
                        current_x += 1 if dx > 0 else -1
                        if random.random() < 0.3:  # 30% chance to move vertically
                            current_y += random.choice([-1, 1])
                    else:
                        current_y += 1 if dy > 0 else -1
                        if random.random() < 0.3:  # 30% chance to move horizontally
                            current_x += random.choice([-1, 1])
                else:
                    # Move towards save point
                    if abs(dx) > abs(dy):
                        current_x += 1 if dx > 0 else -1
                    else:
                        current_y += 1 if dy > 0 else -1
                
                # Ensure we don't go out of bounds
                current_x = max(1, min(current_x, self.width - 2))
                current_y = max(1, min(current_y, self.height - 2))
            
            # Add the final point
            save_path_points.append((save_x, save_y))
            
            # Create the save point path
            for x, y in save_path_points:
                path_width = 2
                for dx in range(-path_width, path_width + 1):
                    for dy in range(-path_width, path_width + 1):
                        if (0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1):
                            if random.random() < 0.8:  # 80% chance to place path tile
                                self.tiles[x + dx, y + dy] = TERRAIN_SAND
                                path_tiles.add((x + dx, y + dy))
            
            # Place the save point
            self.save_point = (save_x, save_y)
            self.tiles[save_x, save_y] = TERRAIN_GRASS  # Clear the save point tile
        
        # Place the cave entrance and its markers
        self.tiles[cave_x, cave_y] = TERRAIN_CAVE
        
        # Add markers around the cave entrance
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                if 0 < cave_x + dx < self.width - 1 and 0 < cave_y + dy < self.height - 1:
                    self.tiles[cave_x + dx, cave_y + dy] = TERRAIN_MOSS

        # Add a merchant near the save point
        from core.npc import create_merchant, create_healer
        if self.save_point:
            save_x, save_y = self.save_point
            # Place merchant 2 tiles away from save point
            merchant_x = save_x + 2
            merchant_y = save_y
            if self.is_walkable(merchant_x, merchant_y):
                merchant = create_merchant(merchant_x, merchant_y)
                self.add_npc(merchant)

        # Add a healer near the spawn point
        healer_x = spawn_x + 3
        healer_y = spawn_y + 3
        if self.is_walkable(healer_x, healer_y):
            healer = create_healer(healer_x, healer_y)
            self.add_npc(healer)

    def path_exists(self, start, end):
        """Check if a path exists between two points using breadth-first search"""
        visited = set()
        queue = [(start, [start])]
        while queue:
            (x, y), path = queue.pop(0)
            if (x, y) == end:
                return True
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                if (0 <= next_x < self.width and 0 <= next_y < self.height and
                    self.is_walkable(next_x, next_y) and
                    (next_x, next_y) not in visited):
                    visited.add((next_x, next_y))
                    queue.append(((next_x, next_y), path + [(next_x, next_y)]))
        return False

    def create_direct_path(self, start, end):
        """Create a direct path between two points with clear areas around stairs"""
        x1, y1 = start
        x2, y2 = end

        # Store the cave entrance position and type if it's at the end point
        is_cave_end = (x2, y2) == self.stairs_down
        if is_cave_end:
            cave_center = (x2, y2)
            cave_tiles = []
            # Store the cave entrance tiles
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if 0 <= x2 + dx < self.width and 0 <= y2 + dy < self.height:
                        if dx*dx + dy*dy <= 4:  # 5x5 cave entrance
                            cave_tiles.append(((x2 + dx, y2 + dy), self.tiles[x2 + dx, y2 + dy]))

        # Clear a 3-tile radius around both stair positions
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                # Clear around start point
                if 0 <= x1 + dx < self.width and 0 <= y1 + dy < self.height:
                    self.tiles[x1 + dx, y1 + dy] = TERRAIN_GRASS
                # Clear around end point
                if 0 <= x2 + dx < self.width and 0 <= y2 + dy < self.height:
                    self.tiles[x2 + dx, y2 + dy] = TERRAIN_GRASS

        # Create L-shaped path
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.tiles[x, y1] = TERRAIN_GRASS
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.tiles[x2, y] = TERRAIN_GRASS
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.tiles[x1, y] = TERRAIN_GRASS
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.tiles[x, y2] = TERRAIN_GRASS

        # Restore the cave entrance if it was at the end point
        if is_cave_end:
            for (x, y), terrain in cave_tiles:
                self.tiles[x, y] = terrain

    def ensure_clear_stair_area(self, x, y):
        """Ensure a 3-tile radius around a position is clear"""
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                    self.tiles[x + dx, y + dy] = TERRAIN_GRASS

    def generate_dungeon(self, level):
        """Generate a dungeon level with rooms, corridors, and features"""
        # Initialize the map with walls
        self.tiles = np.full((self.width, self.height), TERRAIN_WALL)
        
        if level == 0:  # Starting area
            # Create a single large body of water in the center
            water_center_x = self.width // 2
            water_center_y = self.height // 2
            water_radius = 5
            
            # Create the water body
            for y in range(water_center_y - water_radius, water_center_y + water_radius + 1):
                for x in range(water_center_x - water_radius, water_center_x + water_radius + 1):
                    if (x - water_center_x) ** 2 + (y - water_center_y) ** 2 <= water_radius ** 2:
                        self.tiles[x, y] = TERRAIN_WATER
            
            # Create a maze-like pattern using recursive division
            def divide(x, y, width, height, orientation):
                if width < 3 or height < 3:
                    return
                
                # Choose a wall position
                if orientation == 'horizontal':
                    wall_y = y + random.randint(1, height - 2)
                    passage_x = x + random.randint(0, width - 1)
                    
                    # Create horizontal wall
                    for wall_x in range(x, x + width):
                        if wall_x != passage_x:
                            self.tiles[wall_x, wall_y] = TERRAIN_WALL
                    
                    # Recursively divide the two new sections
                    divide(x, y, width, wall_y - y, 'vertical')
                    divide(x, wall_y + 1, width, y + height - wall_y - 1, 'vertical')
                else:  # vertical
                    wall_x = x + random.randint(1, width - 2)
                    passage_y = y + random.randint(0, height - 1)
                    
                    # Create vertical wall
                    for wall_y in range(y, y + height):
                        if wall_y != passage_y:
                            self.tiles[wall_x, wall_y] = TERRAIN_WALL
                    
                    # Recursively divide the two new sections
                    divide(x, y, wall_x - x, height, 'horizontal')
                    divide(wall_x + 1, y, x + width - wall_x - 1, height, 'horizontal')
            
            # Start the division process
            divide(1, 1, self.width - 2, self.height - 2, 'horizontal' if random.random() < 0.5 else 'vertical')
            
            # Convert some walls to grass to create paths
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    if self.tiles[x, y] == TERRAIN_WALL:
                        # Count adjacent walls
                        wall_count = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                                      if 0 <= x + dx < self.width and 0 <= y + dy < self.height
                                      and self.tiles[x + dx, y + dy] == TERRAIN_WALL)
                        
                        # If this wall has 3 or 4 adjacent walls, make it grass
                        if wall_count >= 3:
                            self.tiles[x, y] = TERRAIN_GRASS
            
            # Place the cave entrance at the bottom of the map
            cave_x = self.width // 2
            cave_y = self.height - 2
            self.tiles[cave_x, cave_y] = TERRAIN_CAVE
            
            # Ensure there's a path to the cave entrance
            for y in range(cave_y - 1, 0, -1):
                if self.tiles[cave_x, y] == TERRAIN_WALL:
                    self.tiles[cave_x, y] = TERRAIN_GRASS
            
            # Place the spawn point at the top of the map
            spawn_x = self.width // 2
            spawn_y = 1
            self.tiles[spawn_x, spawn_y] = TERRAIN_GRASS
            self.spawn_point = (spawn_x, spawn_y)
            
            # Ensure there's a path from spawn to the first open area
            for y in range(spawn_y + 1, self.height // 3):
                if self.tiles[spawn_x, y] == TERRAIN_WALL:
                    self.tiles[spawn_x, y] = TERRAIN_GRASS
            
            # Add some decorative elements
            for _ in range(20):  # Add some rocks
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                if self.tiles[x, y] == TERRAIN_GRASS:
                    # Check surrounding tiles to ensure we don't block paths
                    if all(self.tiles[x + dx, y + dy] != TERRAIN_WALL 
                          for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                          if 0 <= x + dx < self.width and 0 <= y + dy < self.height):
                        self.tiles[x, y] = TERRAIN_ROCK
            
            # Add some moss patches
            for _ in range(15):
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                if self.tiles[x, y] == TERRAIN_GRASS:
                    self.tiles[x, y] = TERRAIN_MOSS
            
            # Add some sand patches
            for _ in range(10):
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                if self.tiles[x, y] == TERRAIN_GRASS:
                    self.tiles[x, y] = TERRAIN_SAND
            
            return
        
        # For other levels, use the existing dungeon generation code
        # Generate multiple rooms
        num_rooms = random.randint(5, 8)  # Number of rooms to generate
        rooms = []
        min_room_size = 5
        max_room_size = 12

        # Define room types with their probabilities, adjusted by level
        base_room_types = {
            'normal': 0.3,     # Regular room
            'water': 0.1,      # Water pool room
            'sand': 0.1,       # Sandy room
            'rocky': 0.1,      # Rocky room
            'crystal': 0.1,    # Crystal formation room
            'mossy': 0.05,    # Mossy room
            'lava': 0.05,     # Lava room (deeper levels)
            'fungal': 0.05,   # Fungal growth room
            'bone': 0.05,     # Bone room
            'treasure': 0.05,  # Treasure room
            'ritual': 0.05    # Ritual room
        }

        # Adjust probabilities based on level
        level_factor = min(1.0, level / 5.0)  # Increases with depth
        room_types = base_room_types.copy()
        
        # Increase chances of special rooms in deeper levels
        if level > 3:
            room_types['lava'] = 0.15
            room_types['crystal'] = 0.15
            room_types['ritual'] = 0.1
        if level > 6:
            room_types['bone'] = 0.15
            room_types['fungal'] = 0.15
            room_types['treasure'] = 0.1

        # Normalize probabilities
        total = sum(room_types.values())
        room_types = {k: v/total for k, v in room_types.items()}

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
                        elif new_room['type'] == 'lava':
                            # Create a lava room (represented as water for now)
                            if (x == room_x or x == room_x + room_width - 1 or
                                y == room_y or y == room_y + room_height - 1):
                                self.tiles[x, y] = TERRAIN_GRASS
                            else:
                                self.tiles[x, y] = TERRAIN_WATER
                        elif new_room['type'] == 'fungal':
                            # Create a fungal growth room
                            if random.random() < 0.4:  # 40% chance for fungal growth
                                self.tiles[x, y] = TERRAIN_ROCK
                            else:
                                self.tiles[x, y] = TERRAIN_GRASS
                        elif new_room['type'] == 'bone':
                            # Create a bone room
                            if random.random() < 0.25:  # 25% chance for bones
                                self.tiles[x, y] = TERRAIN_ROCK
                            else:
                                self.tiles[x, y] = TERRAIN_SAND
                        elif new_room['type'] == 'treasure':
                            # Create a treasure room with scattered rocks
                            if random.random() < 0.1:  # 10% chance for rocks
                                self.tiles[x, y] = TERRAIN_ROCK
                            else:
                                self.tiles[x, y] = TERRAIN_GRASS
                        elif new_room['type'] == 'ritual':
                            # Create a ritual room with a special pattern
                            if (x - room_x) % 3 == 0 and (y - room_y) % 3 == 0:
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
                pool_shape = random.choice(['square', 'cross', 'plus', 'diamond', 'zigzag'])
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
                elif pool_shape == 'plus':
                    # Plus-shaped water pool
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_WATER
                elif pool_shape == 'diamond':
                    # Diamond-shaped water pool
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_WATER
                else:  # zigzag
                    # Zigzag water pool
                    for i in range(3):
                        if 0 < x + i < self.width - 1:
                            self.tiles[x + i, y + (i % 2)] = TERRAIN_WATER

        # Add some sand patches in corridors
        for _ in range(random.randint(2, 4)):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[x, y] == TERRAIN_GRASS:
                # Create a small sand patch with varying shapes
                patch_shape = random.choice(['square', 'cross', 'plus', 'diamond', 'zigzag'])
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
                elif patch_shape == 'plus':
                    # Plus-shaped sand patch
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_SAND
                elif patch_shape == 'diamond':
                    # Diamond-shaped sand patch
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_SAND
                else:  # zigzag
                    # Zigzag sand patch
                    for i in range(3):
                        if 0 < x + i < self.width - 1:
                            self.tiles[x + i, y + (i % 2)] = TERRAIN_SAND

        # Add some crystal formations
        for _ in range(random.randint(2, 4)):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[x, y] == TERRAIN_GRASS:
                # Create a crystal formation with varying shapes
                crystal_shape = random.choice(['single', 'cluster', 'line', 'spiral', 'star'])
                if crystal_shape == 'single':
                    self.tiles[x, y] = TERRAIN_ROCK
                elif crystal_shape == 'cluster':
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_ROCK
                elif crystal_shape == 'line':
                    direction = random.choice(['horizontal', 'vertical'])
                    length = random.randint(2, 4)
                    for i in range(length):
                        if direction == 'horizontal':
                            if 0 < x + i < self.width - 1:
                                self.tiles[x + i, y] = TERRAIN_ROCK
                        else:
                            if 0 < y + i < self.height - 1:
                                self.tiles[x, y + i] = TERRAIN_ROCK
                elif crystal_shape == 'spiral':
                    # Create a spiral pattern
                    for i in range(4):
                        for j in range(i + 1):
                            if 0 < x + j < self.width - 1 and 0 < y + i < self.height - 1:
                                self.tiles[x + j, y + i] = TERRAIN_ROCK
                else:  # star
                    # Create a star pattern
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                            self.tiles[x + dx, y + dy] = TERRAIN_ROCK

        # Place stairs based on level
        if level > 0:  # Not the first level
            # Place up stairs in the first room
            if rooms:
                room = rooms[0]
                # Find a walkable spot in the room
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        x, y = room['center_x'] + dx, room['center_y'] + dy
                        if self.is_walkable(x, y):
                            self.stairs_up = (x, y)
                            # Ensure clear area around stairs
                            self.ensure_clear_stair_area(x, y)
                            # Add special features around stairs (outside the clear area)
                            for sx, sy in [(0, 4), (4, 0), (0, -4), (-4, 0)]:
                                if 0 < x + sx < self.width - 1 and 0 < y + sy < self.height - 1:
                                    if random.random() < 0.3:  # 30% chance for decorative features
                                        self.tiles[x + sx, y + sy] = TERRAIN_ROCK
                            break
                    if self.stairs_up:
                        break
        
        if level < 9:  # Not the last level
            # Place down stairs in the last room
            if rooms:
                room = rooms[-1]
                # Find a walkable spot in the room
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        x, y = room['center_x'] + dx, room['center_y'] + dy
                        if self.is_walkable(x, y):
                            self.stairs_down = (x, y)
                            # Ensure clear area around stairs
                            self.ensure_clear_stair_area(x, y)
                            # Add special features around stairs (outside the clear area)
                            for sx, sy in [(0, 4), (4, 0), (0, -4), (-4, 0)]:
                                if 0 < x + sx < self.width - 1 and 0 < y + sy < self.height - 1:
                                    if random.random() < 0.3:  # 30% chance for decorative features
                                        self.tiles[x + sx, y + sy] = TERRAIN_ROCK
                            break
                    if self.stairs_down:
                        break

        # Ensure there's a path between stairs
        if self.stairs_up and self.stairs_down:
            if not self.path_exists(self.stairs_up, self.stairs_down):
                # Create a direct path between stairs
                self.create_direct_path(self.stairs_up, self.stairs_down)

        # Add NPCs based on level
        if level == 1:
            # Add a guide NPC in the first room
            if rooms:
                room = rooms[0]
                guide_x = room['center_x']
                guide_y = room['center_y']
                if self.is_walkable(guide_x, guide_y):
                    from core.npc import create_guide
                    guide = create_guide(guide_x, guide_y)
                    self.add_npc(guide)

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
        # Check if there's an NPC at this position
        if self.get_npc_at(x, y):
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

    def is_save_point(self, x, y):
        """Check if the given coordinates are a save point"""
        return self.save_point and (x, y) == self.save_point

    def get_save_point(self):
        """Get the current save point coordinates"""
        return self.save_point

    def add_npc(self, npc):
        """Add an NPC to the map"""
        self.npcs.append(npc)

    def get_npc_at(self, x, y):
        """Get the NPC at the given coordinates, if any"""
        for npc in self.npcs:
            if npc.x == x and npc.y == y:
                return npc
        return None 