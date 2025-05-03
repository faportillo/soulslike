import tcod
from utils.colors import *

class UIRenderer:
    def __init__(self, console):
        """Initialize the UI renderer with a console"""
        self.console = console

    def render_level(self, level):
        """Render the current level number"""
        self.console.print(0, 0, f"Level: {level}", fg=COLOR_WHITE)

    def render_messages(self, messages, y_offset=1):
        """Render game messages"""
        for i, message in enumerate(messages):
            self.console.print(0, y_offset + i, message, fg=COLOR_WHITE)

    def render_status(self, player):
        """Render player status information"""
        # Render health
        health_text = f"HP: {player.hp}/{player.max_hp}"
        self.console.print(0, self.console.height - 2, health_text, fg=COLOR_WHITE)

        # Render other status effects or information as needed
        # Example: if player.has_effect("poison"):
        #     self.console.print(len(health_text) + 2, self.console.height - 2, "POISONED", fg=COLOR_RED) 