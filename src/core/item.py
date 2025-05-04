from enum import Enum, auto
from core.status_effect import EffectType

class ItemType(Enum):
    HEALTH_POTION = auto()
    GREATER_HEALTH_POTION = auto()
    REGENERATION_POTION = auto()
    ANTIDOTE = auto()
    BANDAGE = auto()

class Item:
    def __init__(self, item_type, x, y, char="!", color=(255, 255, 255)):
        self.item_type = item_type
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = self._get_item_name()
        self.description = self._get_item_description()
        self.heal_amount = self._get_heal_amount()
        self.duration = self._get_duration()

    def _get_item_name(self):
        names = {
            ItemType.HEALTH_POTION: "Health Potion",
            ItemType.GREATER_HEALTH_POTION: "Greater Health Potion",
            ItemType.REGENERATION_POTION: "Regeneration Potion",
            ItemType.ANTIDOTE: "Antidote",
            ItemType.BANDAGE: "Bandage"
        }
        return names.get(self.item_type, "Unknown Item")

    def _get_item_description(self):
        descriptions = {
            ItemType.HEALTH_POTION: "Restores 25 HP",
            ItemType.GREATER_HEALTH_POTION: "Restores 50 HP",
            ItemType.REGENERATION_POTION: "Regenerates 5 HP per turn for 5 turns",
            ItemType.ANTIDOTE: "Cures poison and bleeding",
            ItemType.BANDAGE: "Stops bleeding and heals 10 HP"
        }
        return descriptions.get(self.item_type, "An unknown item")

    def _get_heal_amount(self):
        amounts = {
            ItemType.HEALTH_POTION: 25,
            ItemType.GREATER_HEALTH_POTION: 50,
            ItemType.REGENERATION_POTION: 5,
            ItemType.BANDAGE: 10
        }
        return amounts.get(self.item_type, 0)

    def _get_duration(self):
        durations = {
            ItemType.REGENERATION_POTION: 5
        }
        return durations.get(self.item_type, 0)

    def use(self, player):
        """Use the item on the player"""
        if self.item_type == ItemType.HEALTH_POTION:
            player.heal(self.heal_amount)
            return f"Restored {self.heal_amount} HP"
            
        elif self.item_type == ItemType.GREATER_HEALTH_POTION:
            player.heal(self.heal_amount)
            return f"Restored {self.heal_amount} HP"
            
        elif self.item_type == ItemType.REGENERATION_POTION:
            player.add_status_effect(EffectType.REGENERATION, self.duration, self.heal_amount)
            return f"Regenerating {self.heal_amount} HP per turn for {self.duration} turns"
            
        elif self.item_type == ItemType.ANTIDOTE:
            player.remove_status_effect(EffectType.POISON)
            player.remove_status_effect(EffectType.BLEEDING)
            return "Cured poison and bleeding"
            
        elif self.item_type == ItemType.BANDAGE:
            player.remove_status_effect(EffectType.BLEEDING)
            player.heal(self.heal_amount)
            return f"Stopped bleeding and restored {self.heal_amount} HP"
            
        return "Nothing happened" 