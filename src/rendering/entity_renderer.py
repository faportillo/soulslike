import tcod
from utils.colors import *

class EntityRenderer:
    def __init__(self, console):
        """Initialize the entity renderer with a console"""
        self.console = console

    def render_player(self, player_x, player_y):
        """Render the player character"""
        self.console.print(player_x, player_y, "@", fg=COLOR_PLAYER)

    def render_entity(self, entity):
        """Render a single entity"""
        if entity.visible:
            self.console.print(entity.x, entity.y, entity.char, fg=entity.color)

    def render_entities(self, entities):
        """Render all entities in the game"""
        for entity in entities:
            self.render_entity(entity) 