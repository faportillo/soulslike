import tcod
from utils.colors import *

class UIRenderer:
    def __init__(self, console):
        """Initialize the UI renderer with a console"""
        self.console = console

    def render_level(self, level):
        """Render the current level number"""
        self.console.print(0, 0, f"Level: {level}", fg=COLOR_WHITE)

    def render_status(self, player):
        """Render player status information"""
        # Render health bar
        health_percent = player.hp / player.max_hp
        bar_width = 20
        filled_width = int(bar_width * health_percent)
        
        # Health bar background
        for x in range(bar_width):
            self.console.print(x, 1, " ", bg=COLOR_DARK_RED)
        
        # Health bar fill
        for x in range(filled_width):
            color = COLOR_RED if health_percent < 0.3 else COLOR_GREEN
            self.console.print(x, 1, " ", bg=color)
        
        # Health text
        health_text = f"HP: {player.hp}/{player.max_hp}"
        self.console.print(0, 2, health_text, fg=COLOR_WHITE)
        
        # Defense and damage reduction
        defense_text = f"DEF: {player.defense} ({int(player.damage_reduction * 100)}%)"
        self.console.print(len(health_text) + 2, 2, defense_text, fg=COLOR_WHITE)
        
        # Status effects
        if player.status_effects:
            status_y = 3
            for effect_name, duration in player.get_status_effects():
                effect_text = f"{effect_name}: {duration}"
                color = self._get_effect_color(effect_name)
                self.console.print(0, status_y, effect_text, fg=color)
                status_y += 1

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

    def render_messages(self, messages, y_offset=1):
        """Render game messages"""
        for i, message in enumerate(messages):
            self.console.print(0, y_offset + i, message, fg=COLOR_WHITE) 