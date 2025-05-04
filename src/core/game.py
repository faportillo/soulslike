# Main game file that handles game initialization, input, and the game loop
import tcod
import numpy as np
import pickle
import os
from datetime import datetime
from core.map import Map
from core.player import Player
from utils.constants import *
from rendering.renderer import Renderer

class Game:
    def __init__(self):
        # Initialize game dimensions and state
        self.width = 80  # Width of the game window in tiles
        self.height = 50  # Height of the game window in tiles
        self.levels = {}  # Dictionary to store all game levels
        self.current_level = 0  # Start at level 0 (outdoor level)
        self.player = None  # Will be initialized in initialize_level
        self.show_character_screen = False  # Track if character screen is visible
        self.is_paused = False  # Track if game is paused
        self.last_save_point = None  # Store the last save point coordinates
        self.last_save_level = None  # Store the level of the last save point
        self.message = None  # Store the current message to display
        self.message_timer = 0  # Timer for message display
        self.initialize_level(self.current_level)  # Set up the first level

    def save_game(self):
        """Save the current game state to a file"""
        # Create saves directory if it doesn't exist
        os.makedirs("saves", exist_ok=True)
        
        # Create a timestamp for the save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"saves/save_{timestamp}.sav"
        
        # Prepare save data
        save_data = {
            'width': self.width,
            'height': self.height,
            'current_level': self.current_level,
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'hp': self.player.hp,
                'max_hp': self.player.max_hp,
                'defense': self.player.defense,
                'level': self.player.level,
                'experience': self.player.experience,
                'experience_to_level': self.player.experience_to_level,
                'inventory': [(item.item_type.value, item.x, item.y) for item in self.player.inventory]
            },
            'levels': {}  # We'll save level data separately
        }
        
        # Save each level's data
        for level_num, level in self.levels.items():
            save_data['levels'][level_num] = {
                'tiles': level.tiles,
                'visible': level.visible,
                'explored': level.explored,
                'stairs_up': level.stairs_up,
                'stairs_down': level.stairs_down,
                'stairs_discovered': level.stairs_discovered,
                'is_outdoor': level.is_outdoor,
                'spawn_point': level.spawn_point
            }
        
        # Save to file
        try:
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            return True, f"Game saved to {save_path}"
        except Exception as e:
            return False, f"Failed to save game: {str(e)}"

    def load_game(self, save_path):
        """Load a game state from a file"""
        try:
            with open(save_path, 'rb') as f:
                save_data = pickle.load(f)
            
            # Restore basic game state
            self.width = save_data['width']
            self.height = save_data['height']
            self.current_level = save_data['current_level']
            
            # Restore player data
            player_data = save_data['player']
            self.player = Player(player_data['x'], player_data['y'])
            self.player.hp = player_data['hp']
            self.player.max_hp = player_data['max_hp']
            self.player.defense = player_data['defense']
            self.player.level = player_data['level']
            self.player.experience = player_data['experience']
            self.player.experience_to_level = player_data['experience_to_level']
            
            # Restore levels
            self.levels = {}
            for level_num, level_data in save_data['levels'].items():
                level = Map(self.width, self.height, int(level_num))
                level.tiles = level_data['tiles']
                level.visible = level_data['visible']
                level.explored = level_data['explored']
                level.stairs_up = level_data['stairs_up']
                level.stairs_down = level_data['stairs_down']
                level.stairs_discovered = level_data['stairs_discovered']
                level.is_outdoor = level_data['is_outdoor']
                level.spawn_point = level_data['spawn_point']
                self.levels[int(level_num)] = level
            
            # Update FOV for current position
            self.levels[self.current_level].update_fov(self.player.x, self.player.y)
            return True, "Game loaded successfully"
        except Exception as e:
            return False, f"Failed to load game: {str(e)}"

    def list_saves(self):
        """List all available save files"""
        if not os.path.exists("saves"):
            return []
        
        saves = []
        for filename in os.listdir("saves"):
            if filename.endswith(".sav"):
                save_path = os.path.join("saves", filename)
                timestamp = filename[5:-4]  # Remove 'save_' prefix and '.sav' suffix
                saves.append((save_path, timestamp))
        
        return sorted(saves, key=lambda x: x[1], reverse=True)  # Sort by timestamp, newest first

    def initialize_level(self, level):
        """Initialize a new level and place the player appropriately"""
        # Create the level if it doesn't exist
        if level not in self.levels:
            self.levels[level] = Map(self.width, self.height, level)
        
        # Initialize player if not exists
        if self.player is None:
            self.player = Player(self.width // 2, self.height // 2)
        
        # Place player at appropriate position based on level type and transition
        if level == 0:  # Outdoor level
            if self.levels[level].spawn_point:
                self.player.x, self.player.y = self.levels[level].spawn_point
            else:
                # Find a walkable position near the center
                center_x, center_y = self.width // 2, self.height // 2
                for dx in range(-5, 6):
                    for dy in range(-5, 6):
                        x, y = center_x + dx, center_y + dy
                        if self.levels[level].is_walkable(x, y):
                            self.player.x, self.player.y = x, y
                            break
        else:  # Dungeon level
            # If coming from above (down stairs), place near up stairs
            if level > 0 and self.levels[level].stairs_up:
                self.player.x, self.player.y = self.levels[level].stairs_up
                # Move one tile away from stairs if possible
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = self.player.x + dx, self.player.y + dy
                    if self.levels[level].is_walkable(new_x, new_y):
                        self.player.x, self.player.y = new_x, new_y
                        break
            # If coming from below (up stairs), place near down stairs
            elif level < MAX_LEVELS - 1 and self.levels[level].stairs_down:
                self.player.x, self.player.y = self.levels[level].stairs_down
                # Move one tile away from stairs if possible
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = self.player.x + dx, self.player.y + dy
                    if self.levels[level].is_walkable(new_x, new_y):
                        self.player.x, self.player.y = new_x, new_y
                        break
            else:
                # If no stairs are available, find a walkable position near the center
                center_x, center_y = self.width // 2, self.height // 2
                for dx in range(-5, 6):
                    for dy in range(-5, 6):
                        x, y = center_x + dx, center_y + dy
                        if self.levels[level].is_walkable(x, y):
                            self.player.x, self.player.y = x, y
                            break

        # Update field of view for the new position
        self.levels[level].update_fov(self.player.x, self.player.y)

    def handle_input(self, event):
        """Handle player input and return False if game should quit, 'menu' if should return to menu"""
        # Handle quit events
        if isinstance(event, tcod.event.Quit):
            return 'menu'
        elif isinstance(event, tcod.event.KeyDown):
            # Handle escape key
            if event.sym == tcod.event.KeySym.ESCAPE:
                if self.show_character_screen:
                    self.show_character_screen = False
                    return True
                self.is_paused = not self.is_paused
                return True
            
            # Handle quit key when paused
            if self.is_paused and event.sym == tcod.event.KeySym.q:
                return 'menu'
            
            # If game is paused, ignore other inputs
            if self.is_paused:
                return True
            
            # Handle character screen toggle
            if event.sym == tcod.event.KeySym.c:
                self.show_character_screen = not self.show_character_screen
                return True
            
            # If character screen is open, ignore other inputs
            if self.show_character_screen:
                return True
            
            # Handle save point interaction
            if event.sym == tcod.event.KeySym.SPACE:
                current_map = self.levels[self.current_level]
                if current_map.is_save_point(self.player.x, self.player.y):
                    success, message = self.save_game()
                    self.last_save_point = (self.player.x, self.player.y)
                    self.last_save_level = self.current_level
                    self.message = "Game saved!"
                    self.message_timer = 60  # Show message for 60 frames
                    return True

            # Handle movement keys
            # Arrow keys and numpad for 8-directional movement
            if event.sym == tcod.event.KeySym.UP or event.sym == tcod.event.KeySym.KP_8:
                self.try_move(0, -1)  # Move up
            elif event.sym == tcod.event.KeySym.DOWN or event.sym == tcod.event.KeySym.KP_2:
                self.try_move(0, 1)   # Move down
            elif event.sym == tcod.event.KeySym.LEFT or event.sym == tcod.event.KeySym.KP_4:
                self.try_move(-1, 0)  # Move left
            elif event.sym == tcod.event.KeySym.RIGHT or event.sym == tcod.event.KeySym.KP_6:
                self.try_move(1, 0)   # Move right
            elif event.sym == tcod.event.KeySym.KP_7:
                self.try_move(-1, -1) # Move up-left
            elif event.sym == tcod.event.KeySym.KP_9:
                self.try_move(1, -1)  # Move up-right
            elif event.sym == tcod.event.KeySym.KP_1:
                self.try_move(-1, 1)  # Move down-left
            elif event.sym == tcod.event.KeySym.KP_3:
                self.try_move(1, 1)   # Move down-right

            # Handle inventory keys
            elif event.sym == tcod.event.KeySym.i:  # Inventory
                self.player.select_next_item()
            elif event.sym == tcod.event.KeySym.u:  # Use item
                result = self.player.use_selected_item()
                print(result)  # You might want to show this in the game UI

        return True

    def try_move(self, dx, dy):
        """Try to move the player and handle level transitions"""
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # Check if the new position is walkable
        if not self.levels[self.current_level].is_walkable(new_x, new_y):
            return

        # Check for stairs and handle level transitions
        stairs = self.levels[self.current_level].is_stairs(new_x, new_y)
        if stairs == "up" and self.current_level > 0:
            # Store current position before changing levels
            old_x, old_y = self.player.x, self.player.y
            self.current_level -= 1  # Go up one level
            self.initialize_level(self.current_level)
            # Place player near the down stairs
            if self.levels[self.current_level].stairs_down:
                self.player.x, self.player.y = self.levels[self.current_level].stairs_down
                # Move one tile away from stairs if possible
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = self.player.x + dx, self.player.y + dy
                    if self.levels[self.current_level].is_walkable(new_x, new_y):
                        self.player.x, self.player.y = new_x, new_y
                        break
        elif stairs == "down" and self.current_level < MAX_LEVELS - 1:
            # Store current position before changing levels
            old_x, old_y = self.player.x, self.player.y
            self.current_level += 1  # Go down one level
            self.initialize_level(self.current_level)
            # Place player near the up stairs
            if self.levels[self.current_level].stairs_up:
                self.player.x, self.player.y = self.levels[self.current_level].stairs_up
                # Move one tile away from stairs if possible
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = self.player.x + dx, self.player.y + dy
                    if self.levels[self.current_level].is_walkable(new_x, new_y):
                        self.player.x, self.player.y = new_x, new_y
                        break
        else:
            # Normal movement
            self.player.x = new_x
            self.player.y = new_y

        # Update field of view after movement
        self.levels[self.current_level].update_fov(self.player.x, self.player.y)
        
        # Update player state
        self.player.update()

    def respawn_player(self):
        """Respawn the player at the last save point"""
        if self.last_save_point and self.last_save_level is not None:
            # Change to the saved level if needed
            if self.current_level != self.last_save_level:
                self.current_level = self.last_save_level
                self.initialize_level(self.current_level)
            
            # Move player to save point
            self.player.x, self.player.y = self.last_save_point
            self.player.hp = self.player.max_hp  # Restore health
            self.levels[self.current_level].update_fov(self.player.x, self.player.y)
        else:
            # If no save point, use the level's spawn point
            self.initialize_level(self.current_level)

    def update(self):
        """Update game state"""
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = None

        # Check if player is dead and respawn if needed
        if not self.player.is_alive:
            self.respawn_player()

def main():
    # Initialize the game window and console
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    console = tcod.console.Console(80, 50)
    context = tcod.context.new_terminal(
        columns=80,
        rows=50,
        tileset=tileset,
        title="Roguelike",
        vsync=True,
    )

    # Initialize game objects
    game = Game()
    renderer = Renderer(console)

    # Main game loop
    while True:
        # Clear the console for new frame
        console.clear()

        # Render all game elements
        renderer.render_map(game.levels[game.current_level], game.player.x, game.player.y)
        renderer.render_stairs(game.levels[game.current_level])
        renderer.render_player(game.player.x, game.player.y)
        renderer.render_level(game.current_level)

        # Display the rendered frame
        context.present(console)

        # Handle input and check for quit
        for event in tcod.event.wait():
            if not game.handle_input(event):
                return

if __name__ == "__main__":
    main() 