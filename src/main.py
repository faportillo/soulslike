#!/usr/bin/env python3
import os
import sys
import tcod

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game import Game
from rendering.renderer import Renderer
from rendering.character_screen import CharacterScreenRenderer
from rendering.pause_screen import PauseScreenRenderer
from rendering.main_menu import MainMenuRenderer

def show_main_menu(console, context, renderer, character_screen, pause_screen, main_menu):
    """Show the main menu and return the selected game state"""
    while True:
        # Clear the console
        console.clear()

        # Check if there's a save file
        has_save = bool(Game().list_saves())

        # Render main menu
        main_menu.render(has_save)
        context.present(console)

        # Handle menu input
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                return None
            elif isinstance(event, tcod.event.KeyDown):
                if event.sym == tcod.event.KeySym.ESCAPE:
                    return None
                elif event.sym == tcod.event.KeySym.KP_1 or event.sym == tcod.event.KeySym.N1:
                    # Start new game
                    return Game()
                elif (event.sym == tcod.event.KeySym.KP_2 or event.sym == tcod.event.KeySym.N2) and has_save:
                    # Load last save
                    game = Game()
                    saves = game.list_saves()
                    if saves:
                        success, message = game.load_game(saves[0][0])
                        return game
                elif event.sym == tcod.event.KeySym.KP_3 or event.sym == tcod.event.KeySym.N3:
                    return None

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

    # Initialize renderers
    renderer = Renderer(console)
    character_screen = CharacterScreenRenderer(console)
    pause_screen = PauseScreenRenderer(console)
    main_menu = MainMenuRenderer(console)

    # Main game loop
    while True:
        # Show main menu and get game state
        game = show_main_menu(console, context, renderer, character_screen, pause_screen, main_menu)
        if game is None:
            return

        # Game loop
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
            
            # Render pause screen if game is paused
            if game.is_paused:
                pause_screen.render()

            # Display the rendered frame
            context.present(console)

            # Handle input and check for quit
            for event in tcod.event.wait():
                result = game.handle_input(event)
                if result == 'menu':
                    break
                elif not result:
                    return
            else:
                continue
            break

if __name__ == "__main__":
    main() 