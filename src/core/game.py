# Main game file that handles game initialization, input, and the game loop
import tcod
import numpy as np
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
        self.initialize_level(self.current_level)  # Set up the first level

    def initialize_level(self, level):
        """Initialize a new level and place the player appropriately"""
        # Create the level if it doesn't exist
        if level not in self.levels:
            self.levels[level] = Map(self.width, self.height, level)
        
        # Place player at appropriate position based on level type
        if level == 0:  # Outdoor level - use spawn point
            if self.levels[level].spawn_point:
                self.player_x, self.player_y = self.levels[level].spawn_point
        elif level > 0 and self.levels[level].stairs_up:  # Dungeon level with up stairs
            self.player_x, self.player_y = self.levels[level].stairs_up
        elif level < MAX_LEVELS - 1 and self.levels[level].stairs_down:  # Dungeon level with down stairs
            self.player_x, self.player_y = self.levels[level].stairs_down
        else:  # Fallback to center if no special position
            self.player_x = self.width // 2
            self.player_y = self.height // 2

    def handle_input(self, event):
        """Handle player input and return False if game should quit"""
        # Handle quit events
        if isinstance(event, tcod.event.Quit):
            return False
        elif isinstance(event, tcod.event.KeyDown):
            # Handle escape key
            if event.sym == tcod.event.KeySym.ESCAPE:
                return False

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
            self.current_level -= 1  # Go up one level
            self.initialize_level(self.current_level)
        elif stairs == "down" and self.current_level < MAX_LEVELS - 1:
            self.current_level += 1  # Go down one level
            self.initialize_level(self.current_level)
        else:
            # Normal movement
            self.player_x = new_x
            self.player_y = new_y

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