import tcod
from utils.colors import *

class CharacterScreenRenderer:
    def __init__(self, console):
        """Initialize the character screen renderer"""
        self.console = console
        self.width = 60  # Increased width
        self.height = 35  # Increased height
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

        # Draw health and stamina
        self.console.print(
            self.x + 2,
            self.y + 6,
            f"Health: {player.hp}/{player.max_hp}",
            fg=COLOR_HEALTH
        )
        self.console.print(
            self.x + 2,
            self.y + 7,
            f"Stamina: {player.stamina}/{player.max_stamina}",
            fg=COLOR_STAMINA
        )

        # Draw attributes in two columns
        self.console.print(
            self.x + 2,
            self.y + 9,
            "Attributes:",
            fg=COLOR_WHITE
        )
        y_offset = 10
        attributes = list(player.attributes.items())
        mid_point = len(attributes) // 2
        
        # Left column
        for i, (attr, value) in enumerate(attributes[:mid_point]):
            modifier = player.get_attribute_modifier(attr)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            self.console.print(
                self.x + 4,
                self.y + y_offset + i,
                f"{attr.value}: {value} ({modifier_str})",
                fg=COLOR_WHITE
            )
        
        # Right column
        for i, (attr, value) in enumerate(attributes[mid_point:]):
            modifier = player.get_attribute_modifier(attr)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            self.console.print(
                self.x + self.width // 2 + 4,
                self.y + y_offset + i,
                f"{attr.value}: {value} ({modifier_str})",
                fg=COLOR_WHITE
            )

        # Draw skills in two columns
        skills_y = y_offset + mid_point + 2
        self.console.print(
            self.x + 2,
            self.y + skills_y,
            "Skills:",
            fg=COLOR_WHITE
        )
        skills_y += 1
        skills = list(player.skills.items())
        mid_point = len(skills) // 2
        
        # Left column
        for i, (skill, level) in enumerate(skills[:mid_point]):
            self.console.print(
                self.x + 4,
                self.y + skills_y + i,
                f"{skill.value}: {level}",
                fg=COLOR_WHITE
            )
        
        # Right column
        for i, (skill, level) in enumerate(skills[mid_point:]):
            self.console.print(
                self.x + self.width // 2 + 4,
                self.y + skills_y + i,
                f"{skill.value}: {level}",
                fg=COLOR_WHITE
            )

        # Draw combat stats
        combat_y = skills_y + mid_point + 2
        self.console.print(
            self.x + 2,
            self.y + combat_y,
            "Combat Stats:",
            fg=COLOR_WHITE
        )
        combat_y += 1
        stats = [
            f"Defense: {player.defense}",
            f"Damage Reduction: {player.damage_reduction*100:.1f}%",
            f"Attack Power: {player.attack_power}",
            f"Critical Chance: {player.critical_chance*100:.1f}%",
            f"Dodge Chance: {player.dodge_chance*100:.1f}%"
        ]
        
        # Left column
        for i, stat in enumerate(stats[:len(stats)//2]):
            self.console.print(
                self.x + 4,
                self.y + combat_y + i,
                stat,
                fg=COLOR_WHITE
            )
        
        # Right column
        for i, stat in enumerate(stats[len(stats)//2:]):
            self.console.print(
                self.x + self.width // 2 + 4,
                self.y + combat_y + i,
                stat,
                fg=COLOR_WHITE
            )

        # Draw available points
        if player.attribute_points > 0 or player.skill_points > 0:
            points_y = combat_y + len(stats)//2 + 2
            self.console.print(
                self.x + 2,
                self.y + points_y,
                f"Available Points:",
                fg=COLOR_WHITE
            )
            if player.attribute_points > 0:
                self.console.print(
                    self.x + 4,
                    self.y + points_y + 1,
                    f"Attribute Points: {player.attribute_points}",
                    fg=COLOR_WHITE
                )
            if player.skill_points > 0:
                self.console.print(
                    self.x + 4,
                    self.y + points_y + 2,
                    f"Skill Points: {player.skill_points}",
                    fg=COLOR_WHITE
                )

        # Draw help text
        help_text = "Press 'c' to close"
        self.console.print(
            self.x + (self.width - len(help_text)) // 2,
            self.y + self.height - 2,
            help_text,
            fg=COLOR_WHITE
        )

        # Present the console
        tcod.console_flush() 