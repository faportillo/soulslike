class Entity:
    def __init__(self, x, y, char, color):
        """Initialize a new entity"""
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.is_alive = True
        self.visible = True

    def move(self, dx, dy):
        """Move the entity by the given delta"""
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y):
        """Move one step towards the target"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = max(abs(dx), abs(dy))
        
        if distance > 0:
            dx = int(round(dx / distance))
            dy = int(round(dy / distance))
            self.move(dx, dy)

    def move_away(self, target_x, target_y):
        """Move one step away from the target"""
        dx = self.x - target_x
        dy = self.y - target_y
        distance = max(abs(dx), abs(dy))
        
        if distance > 0:
            dx = int(round(dx / distance))
            dy = int(round(dy / distance))
            self.move(dx, dy)

    def distance_to(self, other):
        """Calculate the distance to another entity"""
        dx = other.x - self.x
        dy = other.y - self.y
        return max(abs(dx), abs(dy))  # Chebyshev distance 