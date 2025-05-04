import tcod
from utils.colors import *

class CharacterScreenRenderer:
    def __init__(self, console):
        """Initialize the character screen renderer"""
        self.console = console
        self.width = 40
        self.height = 25
        self.x = (console.width - self.width) // 2
        self.y = (console.height - self.height) // 2

    def render(self, player):
        """Render the character screen"""
        # Draw the background
        for x in range(self.width):
            for y in range(self.height):
                self.console.print(
                    self.x + x,
                    self.y + y,
                    " ",
                    fg=COLOR_WHITE,
                    bg=COLOR_BLACK
                )

        # Draw the border
        for x in range(self.width):
            self.console.print(self.x + x, self.y, "-", fg=COLOR_WHITE)
            self.console.print(self.x + x, self.y + self.height - 1, "-", fg=COLOR_WHITE)
        for y in range(self.height):
            self.console.print(self.x, self.y + y, "|", fg=COLOR_WHITE)
            self.console.print(self.x + self.width - 1, self.y + y, "|", fg=COLOR_WHITE)
        
        # Draw corners
        self.console.print(self.x, self.y, "+", fg=COLOR_WHITE)
        self.console.print(self.x + self.width - 1, self.y, "+", fg=COLOR_WHITE)
        self.console.print(self.x, self.y + self.height - 1, "+", fg=COLOR_WHITE)
        self.console.print(self.x + self.width - 1, self.y + self.height - 1, "+", fg=COLOR_WHITE)

        # Draw title
        title = "Character Sheet"
        self.console.print(
            self.x + (self.width - len(title)) // 2,
            self.y + 1,
            title,
            fg=COLOR_WHITE
        )

        # Draw level and experience
        self.console.print(
            self.x + 2,
            self.y + 3,
            f"Level: {player.level}",
            fg=COLOR_WHITE
        )
        self.console.print(
            self.x + 2,
            self.y + 4,
            f"Experience: {player.experience}/{player.experience_to_level}",
            fg=COLOR_WHITE
        )

        # Draw attributes
        self.console.print(
            self.x + 2,
            self.y + 6,
            "Attributes:",
            fg=COLOR_WHITE
        )
        y_offset = 7
        for attr in player.attributes:
            value = player.attributes[attr]
            modifier = player.get_attribute_modifier(attr)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            self.console.print(
                self.x + 4,
                self.y + y_offset,
                f"{attr.value}: {value} ({modifier_str})",
                fg=COLOR_WHITE
            )
            y_offset += 1

        # Draw skills
        self.console.print(
            self.x + 2,
            self.y + y_offset + 1,
            "Skills:",
            fg=COLOR_WHITE
        )
        y_offset += 2
        for skill in player.skills:
            level = player.get_skill_level(skill)
            self.console.print(
                self.x + 4,
                self.y + y_offset,
                f"{skill.value}: {level}",
                fg=COLOR_WHITE
            )
            y_offset += 1

        # Draw combat stats
        self.console.print(
            self.x + 2,
            self.y + y_offset + 1,
            "Combat Stats:",
            fg=COLOR_WHITE
        )
        y_offset += 2
        stats = [
            f"HP: {player.hp}/{player.max_hp}",
            f"Defense: {player.defense}",
            f"Attack Power: {player.attack_power}",
            f"Critical Chance: {player.critical_chance*100:.1f}%",
            f"Dodge Chance: {player.dodge_chance*100:.1f}%"
        ]
        for stat in stats:
            self.console.print(
                self.x + 4,
                self.y + y_offset,
                stat,
                fg=COLOR_WHITE
            )
            y_offset += 1

        # Draw available points
        if player.attribute_points > 0 or player.skill_points > 0:
            self.console.print(
                self.x + 2,
                self.y + self.height - 3,
                f"Available Points:",
                fg=COLOR_WHITE
            )
            if player.attribute_points > 0:
                self.console.print(
                    self.x + 4,
                    self.y + self.height - 2,
                    f"Attribute Points: {player.attribute_points}",
                    fg=COLOR_WHITE
                )
            if player.skill_points > 0:
                self.console.print(
                    self.x + 4,
                    self.y + self.height - 1,
                    f"Skill Points: {player.skill_points}",
                    fg=COLOR_WHITE
                )

        # Draw help text
        help_text = "Press 'c' to close"
        self.console.print(
            self.x + (self.width - len(help_text)) // 2,
            self.y + self.height - 1,
            help_text,
            fg=COLOR_WHITE
        ) 