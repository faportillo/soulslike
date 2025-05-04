#!/usr/bin/env python3
import os
import sys
import tcod

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game import Game
from rendering.renderer import Renderer
from rendering.character_screen import CharacterScreenRenderer

def main():
    # Initialize the game window and console
    tileset = tcod.tileset.load_tilesheet(
        "src/assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
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
    character_screen = CharacterScreenRenderer(console)

    # Main game loop
    while True:
        # Clear the console for new frame
        console.clear()

        # Render all game elements
        renderer.render_all(
            game_map=game.levels[game.current_level],
            player=game.player,
            entities=[],  # Add entities when implemented
            level=game.current_level,
            messages=[]  # Add messages when implemented
        )

        # Render character screen if active
        if game.show_character_screen:
            character_screen.render(game.player)

        # Display the rendered frame
        context.present(console)

        # Handle input and check for quit
        for event in tcod.event.wait():
            if not game.handle_input(event):
                return

if __name__ == "__main__":
    main() 