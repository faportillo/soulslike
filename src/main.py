#!/usr/bin/env python3
import os
import sys
import tcod
from tcod import libtcodpy

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game import Game
from core.player import Player
from core.map import Map
from rendering.renderer import Renderer
from rendering.character_screen import CharacterScreenRenderer
from rendering.pause_screen import PauseScreenRenderer
from rendering.main_menu import MainMenuRenderer
from utils.colors import *

def show_main_menu(console, game, renderer, character_screen, pause_screen, main_menu):
    """Show the main menu and handle menu options"""
    # Create a new game instance if none exists
    if not game:
        game = Game()
    
    # Check for save files
    has_save = bool(game.list_saves())
    
    while True:
        # Clear the console
        console.clear()
        
        # Render the main menu
        main_menu.render(has_save)
        
        # Present the console
        tcod.console_flush()
        
        # Handle input
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                return None
            elif isinstance(event, tcod.event.KeyDown):
                if event.sym == tcod.event.KeySym.KP_1 or event.sym == tcod.event.KeySym.N1:
                    # Start new game
                    return game
                elif event.sym == tcod.event.KeySym.KP_2 or event.sym == tcod.event.KeySym.N2:
                    # Load game
                    if has_save:
                        saves = game.list_saves()
                        if saves:
                            save_path, _ = saves[0]  # Get the most recent save
                            success, message = game.load_game(save_path)
                            if success:
                                return game
                            else:
                                print(f"Failed to load game: {message}")
                                return None
                    return None
                elif event.sym == tcod.event.KeySym.KP_3 or event.sym == tcod.event.KeySym.N3:
                    # Quit game
                    return None

def main():
    # Initialize the console
    console = tcod.console_init_root(80, 50, "Soulslike", False)
    
    # Create game instance
    game = Game()
    
    # Create renderers
    renderer = Renderer(console)
    pause_screen = PauseScreenRenderer(console)
    character_screen = CharacterScreenRenderer(console)
    main_menu = MainMenuRenderer(console)
    
    # Show main menu first
    game = show_main_menu(console, None, renderer, character_screen, pause_screen, main_menu)
    if not game:
        return
    
    # Main game loop
    while True:
        # Clear the console for new frame
        console.clear()
        
        # Update game state if not paused
        if not game.is_paused:
            game.update()
        
        # Render everything
        renderer.render_all(game, game.player, None)
        
        # Render pause screen if game is paused
        if game.is_paused:
            pause_screen.render()
        
        # Present the console
        tcod.console_flush()
        
        # Handle input
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                return
            elif isinstance(event, tcod.event.KeyDown):
                if event.sym == tcod.event.KeySym.ESCAPE:
                    # Toggle pause state
                    game.is_paused = not game.is_paused
                    continue
                
                # If game is paused, handle pause menu options
                if game.is_paused:
                    if event.sym == tcod.event.KeySym.KP_1 or event.sym == tcod.event.KeySym.N1:
                        # Resume game
                        game.is_paused = False
                    elif event.sym == tcod.event.KeySym.KP_2 or event.sym == tcod.event.KeySym.N2:
                        # Return to main menu
                        game = show_main_menu(console, None, renderer, character_screen, pause_screen, main_menu)
                        if not game:
                            return
                        continue
                    elif event.sym == tcod.event.KeySym.KP_3 or event.sym == tcod.event.KeySym.N3:
                        # Quit game
                        return
                    continue
                
                # Handle character screen toggle
                if event.sym == tcod.event.KeySym.c:
                    game.show_character_screen = not game.show_character_screen
                    continue
                
                # If character screen is open, ignore other inputs
                if game.show_character_screen:
                    continue
                
                # Handle movement keys when not paused
                if event.sym == tcod.event.KeySym.UP or event.sym == tcod.event.KeySym.KP_8:
                    game.try_move(0, -1)  # Move up
                elif event.sym == tcod.event.KeySym.DOWN or event.sym == tcod.event.KeySym.KP_2:
                    game.try_move(0, 1)   # Move down
                elif event.sym == tcod.event.KeySym.LEFT or event.sym == tcod.event.KeySym.KP_4:
                    game.try_move(-1, 0)  # Move left
                elif event.sym == tcod.event.KeySym.RIGHT or event.sym == tcod.event.KeySym.KP_6:
                    game.try_move(1, 0)   # Move right
                elif event.sym == tcod.event.KeySym.KP_7:
                    game.try_move(-1, -1) # Move up-left
                elif event.sym == tcod.event.KeySym.KP_9:
                    game.try_move(1, -1)  # Move up-right
                elif event.sym == tcod.event.KeySym.KP_1:
                    game.try_move(-1, 1)  # Move down-left
                elif event.sym == tcod.event.KeySym.KP_3:
                    game.try_move(1, 1)   # Move down-right
                elif event.sym == tcod.event.KeySym.SPACE:
                    # Handle save point interaction
                    current_map = game.levels[game.current_level]
                    if current_map.is_save_point(game.player.x, game.player.y):
                        success, message = game.save_game()
                        game.last_save_point = (game.player.x, game.player.y)
                        game.last_save_level = game.current_level
                        game.message = "Game saved!"
                        game.message_timer = 60  # Show message for 60 frames

if __name__ == "__main__":
    main() 