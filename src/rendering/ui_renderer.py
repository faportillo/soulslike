import tcod
from utils.colors import *

class UIRenderer:
    def __init__(self, console):
        """Initialize the UI renderer with a console"""
        self.console = console

    def render_ui(self, game, player, game_map):
        """Render all UI elements"""
        # Render level
        self.render_level(game_map.level)
        
        # Render status
        self.render_status(player)
        
        # Render messages
        if game.message:
            self.render_messages([game.message])

    def render_level(self, level):
        """Render the current level number"""
        level_text = f"Level: {level}"
        self.console.print(0, 0, level_text, fg=COLOR_WHITE)

    def render_status(self, player):
        """Render player status information"""
        # Health bar
        health_text = f"HP: {player.hp}/{player.max_hp}"
        self.console.print(0, 1, health_text, fg=COLOR_HEALTH)
        
        # Stamina bar
        stamina_text = f"SP: {player.stamina}/{player.max_stamina}"
        self.console.print(0, 2, stamina_text, fg=COLOR_STAMINA)

    def render_messages(self, messages):
        """Render game messages"""
        if not messages:
            return

        # Get the last message
        message = messages[-1]
        
        # Calculate position (bottom of screen)
        y = self.console.height - 1
        
        # Clear the message line
        for x in range(self.console.width):
            self.console.print(x, y, " ", fg=COLOR_WHITE)
        
        # Print the message
        self.console.print(0, y, message, fg=COLOR_MESSAGE)

    def _get_effect_color(self, effect_name):
        """Get the appropriate color for a status effect"""
        colors = {
            "POISON": COLOR_GREEN,
            "REGENERATION": COLOR_BLUE,
            "BLEEDING": COLOR_RED,
            "BURNING": COLOR_ORANGE,
            "STUNNED": COLOR_YELLOW
        }
        return colors.get(effect_name, COLOR_WHITE) 