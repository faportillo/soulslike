import tcod
from core.npc import NPC, Dialogue

class DialogueScreenRenderer:
    def __init__(self, console, width=60, height=20):
        """Initialize the dialogue screen renderer"""
        self.console = console
        self.width = width
        self.height = height
        self.visible = False
        self.selected_option = 0
        # Calculate position to center the dialogue screen
        self.x_offset = (80 - width) // 2
        self.y_offset = (50 - height) // 2
        # Space for character portrait (future use)
        self.portrait_width = 0  # Will be used when portraits are implemented
        self.portrait_height = 0

    def render(self, npc: NPC):
        """Render the dialogue screen"""
        if not self.visible or not npc.is_talking:
            return

        current_dialogue = npc.get_current_dialogue()
        if not current_dialogue:
            return

        # Draw the main dialogue box
        # Top border
        self.console.print(self.x_offset, self.y_offset, "╔" + "═" * (self.width - 2) + "╗", fg=(200, 200, 200))
        
        # Left and right borders
        for y in range(1, self.height - 1):
            self.console.print(self.x_offset, self.y_offset + y, "║", fg=(200, 200, 200))
            self.console.print(self.x_offset + self.width - 1, self.y_offset + y, "║", fg=(200, 200, 200))
        
        # Bottom border
        self.console.print(self.x_offset, self.y_offset + self.height - 1, "╚" + "═" * (self.width - 2) + "╝", fg=(200, 200, 200))

        # Draw NPC name in a title bar
        name_text = f" {npc.name} "
        name_x = self.x_offset + (self.width - len(name_text)) // 2
        self.console.print(name_x - 1, self.y_offset, "║", fg=(200, 200, 200))
        self.console.print(name_x, self.y_offset, name_text, fg=(255, 255, 255), bg=(50, 50, 50))
        self.console.print(name_x + len(name_text), self.y_offset, "║", fg=(200, 200, 200))

        # Draw dialogue text in a text box at the bottom
        text_box_height = 6
        text_box_y = self.y_offset + self.height - text_box_height - 2
        
        # Draw text box border
        self.console.print(self.x_offset + 2, text_box_y, "╔" + "═" * (self.width - 6) + "╗", fg=(150, 150, 150))
        for y in range(1, text_box_height - 1):
            self.console.print(self.x_offset + 2, text_box_y + y, "║" + " " * (self.width - 6) + "║", fg=(150, 150, 150))
        self.console.print(self.x_offset + 2, text_box_y + text_box_height - 1, "╚" + "═" * (self.width - 6) + "╝", fg=(150, 150, 150))

        # Draw dialogue text with word wrapping
        text_y = text_box_y + 1
        words = current_dialogue.text.split()
        current_line = ""
        line_y = text_y

        for word in words:
            if len(current_line) + len(word) + 1 <= self.width - 8:  # Account for borders
                current_line += word + " "
            else:
                self.console.print(self.x_offset + 4, line_y, current_line, fg=(200, 200, 200))
                current_line = word + " "
                line_y += 1
        if current_line:
            self.console.print(self.x_offset + 4, line_y, current_line, fg=(200, 200, 200))

        # Draw options below the text box
        options_start_y = text_box_y + text_box_height + 1
        for i, option in enumerate(current_dialogue.options):
            y = options_start_y + i
            if i == self.selected_option:
                self.console.print(self.x_offset + 4, y, ">", fg=(255, 255, 0))
                self.console.print(self.x_offset + 6, y, option.text, fg=(255, 255, 0))
            else:
                self.console.print(self.x_offset + 6, y, option.text, fg=(200, 200, 200))

        # Draw help text at the bottom
        help_text = "↑/↓: Select  Space: Choose  Esc: Close"
        self.console.print(self.x_offset + self.width // 2 - len(help_text) // 2, 
                          self.y_offset + self.height - 2, 
                          help_text, fg=(150, 150, 150))

    def handle_input(self, event, npc: NPC) -> bool:
        """Handle input for the dialogue screen"""
        if not self.visible or not npc.is_talking:
            return False

        if event.type == "KEYDOWN":
            if event.sym == tcod.event.K_ESCAPE:
                self.visible = False
                npc.end_dialogue()
                return True
            elif event.sym == tcod.event.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
                return True
            elif event.sym == tcod.event.K_DOWN:
                current_dialogue = npc.get_current_dialogue()
                if current_dialogue:
                    self.selected_option = min(len(current_dialogue.options) - 1, self.selected_option + 1)
                return True
            elif event.sym == tcod.event.K_SPACE:
                current_dialogue = npc.get_current_dialogue()
                if current_dialogue:
                    next_dialogue = npc.select_option(self.selected_option)
                    if next_dialogue:
                        npc.start_dialogue(next_dialogue)
                    else:
                        self.visible = False
                        npc.end_dialogue()
                    self.selected_option = 0
                return True

        return False

    def show(self, npc: NPC):
        """Show the dialogue screen and start dialogue with the NPC"""
        self.visible = True
        self.selected_option = 0
        npc.start_dialogue("greeting") 