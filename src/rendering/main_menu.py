import tcod
from utils.colors import *

class MainMenuRenderer:
    def __init__(self, console):
        """Initialize the main menu renderer"""
        self.console = console
        self.width = 40
        self.height = 15
        self.x = (console.width - self.width) // 2
        self.y = (console.height - self.height) // 2

    def render(self, has_save=False):
        """Render the main menu"""
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
        title = "SOULSLIKE"
        self.console.print(
            self.x + (self.width - len(title)) // 2,
            self.y + 1,
            title,
            fg=COLOR_WHITE
        )

        # Draw menu options
        options = [
            "1. New Game",
            "2. Load Last Save" if has_save else "2. No Save File Found",
            "3. Exit"
        ]
        
        for i, option in enumerate(options):
            color = COLOR_WHITE if i != 1 or has_save else COLOR_GRAY
            self.console.print(
                self.x + (self.width - len(option)) // 2,
                self.y + 4 + i,
                option,
                fg=color
            ) 