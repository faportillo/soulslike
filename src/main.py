#!/usr/bin/env python3
import tcod
from core.game import Game
from rendering.renderer import Renderer

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