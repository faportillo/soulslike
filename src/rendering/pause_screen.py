import tcod
from utils.colors import *

class PauseScreenRenderer:
    def __init__(self, console):
        """Initialize the pause screen renderer"""
        self.console = console
        self.width = 30
        self.height = 10
        self.x = (console.width - self.width) // 2
        self.y = (console.height - self.height) // 2

    def render(self):
        """Render the pause menu"""
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
        title = "PAUSED"
        self.console.print(
            self.x + (self.width - len(title)) // 2,
            self.y + 1,
            title,
            fg=COLOR_WHITE
        )

        # Draw menu options
        options = [
            "1. Resume Game",
            "2. Return to Main Menu",
            "3. Quit Game"
        ]
        
        for i, option in enumerate(options):
            self.console.print(
                self.x + (self.width - len(option)) // 2,
                self.y + 3 + i,
                option,
                fg=COLOR_WHITE
            ) 