# Main game file that handles game initialization, input, and the game loop
import tcod
import numpy as np
import pickle
import os
from datetime import datetime
from core.map import Map
from utils.constants import *
from rendering.renderer import Renderer

class Game:
    def __init__(self):
        # Initialize game dimensions and state
        self.width = 80  # Width of the game window in tiles
        self.height = 50  # Height of the game window in tiles
        self.levels = {}  # Dictionary to store all game levels
        self.current_level = 0  # Start at level 0 (outdoor level)
        self.player_x = self.width // 2  # Initial player X position
        self.player_y = self.height // 2  # Initial player Y position
        self.player_positions = {}  # Store player positions for each level
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
            'player_x': self.player_x,
            'player_y': self.player_y,
            'player_positions': self.player_positions,
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
            self.player_x = save_data['player_x']
            self.player_y = save_data['player_y']
            self.player_positions = save_data['player_positions']
            
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
            self.levels[self.current_level].update_fov(self.player_x, self.player_y)
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
        
        # Check if we have a stored position for this level
        if level in self.player_positions:
            # Restore the stored position
            self.player_x, self.player_y = self.player_positions[level]
        else:
            # Place player at appropriate position based on level type and transition
            if level == 0:  # Outdoor level
                if self.levels[level].spawn_point:
                    self.player_x, self.player_y = self.levels[level].spawn_point
                else:
                    # Find a walkable position near the center
                    center_x, center_y = self.width // 2, self.height // 2
                    for dx in range(-5, 6):
                        for dy in range(-5, 6):
                            x, y = center_x + dx, center_y + dy
                            if self.levels[level].is_walkable(x, y):
                                self.player_x, self.player_y = x, y
                                break
            else:  # Dungeon level
                # If coming from above (down stairs), place near up stairs
                if level > 0 and self.levels[level].stairs_up:
                    self.player_x, self.player_y = self.levels[level].stairs_up
                    # Move one tile away from stairs if possible
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_x, new_y = self.player_x + dx, self.player_y + dy
                        if self.levels[level].is_walkable(new_x, new_y):
                            self.player_x, self.player_y = new_x, new_y
                            break
                # If coming from below (up stairs), place near down stairs
                elif level < MAX_LEVELS - 1 and self.levels[level].stairs_down:
                    self.player_x, self.player_y = self.levels[level].stairs_down
                    # Move one tile away from stairs if possible
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_x, new_y = self.player_x + dx, self.player_y + dy
                        if self.levels[level].is_walkable(new_x, new_y):
                            self.player_x, self.player_y = new_x, new_y
                            break

        # Store the current position for this level
        self.player_positions[level] = (self.player_x, self.player_y)

        # Update field of view for the new position
        self.levels[level].update_fov(self.player_x, self.player_y)

    def handle_input(self, event):
        """Handle player input and return False if game should quit"""
        # Handle quit events
        if isinstance(event, tcod.event.Quit):
            return False
        elif isinstance(event, tcod.event.KeyDown):
            # Handle escape key
            if event.sym == tcod.event.KeySym.ESCAPE:
                return False
            
            # Handle save/load keys
            if event.sym == tcod.event.KeySym.s:  # Save game
                success, message = self.save_game()
                print(message)  # You might want to show this in the game UI
                return True
            elif event.sym == tcod.event.KeySym.l:  # Load game
                saves = self.list_saves()
                if saves:
                    success, message = self.load_game(saves[0][0])  # Load most recent save
                    print(message)  # You might want to show this in the game UI
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

        return True

    def try_move(self, dx, dy):
        """Try to move the player and handle level transitions"""
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # Check if the new position is walkable
        if not self.levels[self.current_level].is_walkable(new_x, new_y):
            return

        # Check for stairs and handle level transitions
        stairs = self.levels[self.current_level].is_stairs(new_x, new_y)
        if stairs == "up" and self.current_level > 0:
            # Store current position before level transition
            self.player_positions[self.current_level] = (self.player_x, self.player_y)
            self.current_level -= 1  # Go up one level
            self.initialize_level(self.current_level)
        elif stairs == "down" and self.current_level < MAX_LEVELS - 1:
            # Store current position before level transition
            self.player_positions[self.current_level] = (self.player_x, self.player_y)
            self.current_level += 1  # Go down one level
            self.initialize_level(self.current_level)
        else:
            # Normal movement
            self.player_x = new_x
            self.player_y = new_y
            # Update stored position
            self.player_positions[self.current_level] = (self.player_x, self.player_y)

        # Update field of view after movement
        self.levels[self.current_level].update_fov(self.player_x, self.player_y)

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
        renderer.render_map(game.levels[game.current_level], game.player_x, game.player_y)
        renderer.render_stairs(game.levels[game.current_level])
        renderer.render_player(game.player_x, game.player_y)
        renderer.render_level(game.current_level)

        # Display the rendered frame
        context.present(console)

        # Handle input and check for quit
        for event in tcod.event.wait():
            if not game.handle_input(event):
                return

if __name__ == "__main__":
    main() 