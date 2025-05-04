import tcod
from tcod import libtcodpy

class InventoryScreenRenderer:
    def __init__(self, console, width=60, height=35):
        """Initialize the inventory screen renderer"""
        self.width = width
        self.height = height
        self.console = console
        self.visible = False
        self.selected_index = 0
        self.items_per_page = 20
        self.current_page = 0
        self._last_render = None  # Store last render state
        # Calculate position to center the inventory screen
        self.x_offset = (80 - width) // 2
        self.y_offset = (50 - height) // 2

    def render(self, player):
        """Render the inventory screen"""
        if not self.visible:
            return

        # Draw the border
        for x in range(self.width):
            self.console.print(self.x_offset + x, self.y_offset, "─", fg=(200, 200, 200))
            self.console.print(self.x_offset + x, self.y_offset + self.height - 1, "─", fg=(200, 200, 200))
        for y in range(self.height):
            self.console.print(self.x_offset, self.y_offset + y, "│", fg=(200, 200, 200))
            self.console.print(self.x_offset + self.width - 1, self.y_offset + y, "│", fg=(200, 200, 200))
        self.console.print(self.x_offset, self.y_offset, "┌", fg=(200, 200, 200))
        self.console.print(self.x_offset + self.width - 1, self.y_offset, "┐", fg=(200, 200, 200))
        self.console.print(self.x_offset, self.y_offset + self.height - 1, "└", fg=(200, 200, 200))
        self.console.print(self.x_offset + self.width - 1, self.y_offset + self.height - 1, "┘", fg=(200, 200, 200))

        # Draw the title
        title = "Inventory"
        self.console.print(self.x_offset + self.width // 2 - len(title) // 2, self.y_offset + 1, title, fg=(255, 255, 255))

        # Draw inventory contents
        start_y = self.y_offset + 3
        items = player.inventory
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(items))

        if not items:
            self.console.print(self.x_offset + 2, start_y, "Your inventory is empty.", fg=(150, 150, 150))
        else:
            for i, item in enumerate(items[start_idx:end_idx]):
                y = start_y + i * 2  # Double spacing for items
                # Highlight selected item
                if i + start_idx == self.selected_index:
                    self.console.print(self.x_offset + 2, y, ">", fg=(255, 255, 0))
                    self.console.print(self.x_offset + 4, y, item.name, fg=(255, 255, 0))
                    # Show item description
                    self.console.print(self.x_offset + 4, y + 1, item.description, fg=(200, 200, 200))
                else:
                    self.console.print(self.x_offset + 4, y, item.name, fg=(200, 200, 200))

        # Draw page navigation if needed
        if len(items) > self.items_per_page:
            page_info = f"Page {self.current_page + 1}/{(len(items) - 1) // self.items_per_page + 1}"
            self.console.print(self.x_offset + self.width - len(page_info) - 2, self.y_offset + self.height - 2, page_info, fg=(150, 150, 150))

        # Draw help text
        help_text = "↑/↓: Select  Enter: Use  D: Drop  Esc: Close"
        self.console.print(self.x_offset + self.width // 2 - len(help_text) // 2, self.y_offset + self.height - 2, help_text, fg=(150, 150, 150))

    def handle_input(self, event, player):
        """Handle input for the inventory screen"""
        if not self.visible:
            return False

        if event.type == "KEYDOWN":
            if event.sym == tcod.event.K_ESCAPE:
                self.visible = False
                self._last_render = None  # Reset render state
                return True
            elif event.sym == tcod.event.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                # Update page if needed
                if self.selected_index < self.current_page * self.items_per_page:
                    self.current_page = max(0, self.current_page - 1)
                return True
            elif event.sym == tcod.event.K_DOWN:
                self.selected_index = min(len(player.inventory) - 1, self.selected_index + 1)
                # Update page if needed
                if self.selected_index >= (self.current_page + 1) * self.items_per_page:
                    self.current_page = min((len(player.inventory) - 1) // self.items_per_page, self.current_page + 1)
                return True
            elif event.sym == tcod.event.K_RETURN:
                # Use selected item
                if 0 <= self.selected_index < len(player.inventory):
                    item = player.inventory[self.selected_index]
                    if item.use(player):
                        player.inventory.pop(self.selected_index)
                        if self.selected_index >= len(player.inventory):
                            self.selected_index = max(0, len(player.inventory) - 1)
                return True
            elif event.sym == tcod.event.K_d:
                # Drop selected item
                if 0 <= self.selected_index < len(player.inventory):
                    player.inventory.pop(self.selected_index)
                    if self.selected_index >= len(player.inventory):
                        self.selected_index = max(0, len(player.inventory) - 1)
                return True

        return False

    def toggle(self):
        """Toggle the inventory screen visibility"""
        self.visible = not self.visible
        if self.visible:
            self.selected_index = 0
            self.current_page = 0
            self._last_render = None  # Reset render state 