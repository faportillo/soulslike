class Item:
    def __init__(self, name, description, value=0):
        self.name = name
        self.description = description
        self.value = value

    def use(self, player):
        """Use the item. Returns True if the item should be consumed."""
        return False

class HealthPotion(Item):
    def __init__(self):
        super().__init__("Health Potion", "Restores 30 health points", value=50)

    def use(self, player):
        heal_amount = 30
        if player.health < player.max_health:
            player.health = min(player.max_health, player.health + heal_amount)
            return True
        return False

class StaminaPotion(Item):
    def __init__(self):
        super().__init__("Stamina Potion", "Restores 50 stamina points", value=40)

    def use(self, player):
        restore_amount = 50
        if player.stamina < player.max_stamina:
            player.stamina = min(player.max_stamina, player.stamina + restore_amount)
            return True
        return False

class StrengthPotion(Item):
    def __init__(self):
        super().__init__("Strength Potion", "Temporarily increases strength by 5", value=75)

    def use(self, player):
        player.strength += 5
        return True

class DefensePotion(Item):
    def __init__(self):
        super().__init__("Defense Potion", "Temporarily increases defense by 5", value=75)

    def use(self, player):
        player.defense += 5
        return True 