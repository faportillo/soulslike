from core.entity import Entity
from core.status_effect import StatusEffect, EffectType
from utils.colors import COLOR_PLAYER

class Player(Entity):
    def __init__(self, x, y):
        """Initialize a new player"""
        super().__init__(
            x=x,
            y=y,
            char="@",
            color=COLOR_PLAYER
        )
        # Health attributes
        self.hp = 100
        self.max_hp = 100
        self.base_hp_regen = 1  # HP regenerated per turn
        self.hp_regen_cooldown = 0  # Cooldown for HP regeneration
        
        # Combat attributes
        self.defense = 10
        self.damage_reduction = 0.1  # 10% damage reduction
        
        # Status effects
        self.status_effects = []
        self.is_stunned = False
        
        # Level and experience
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100

        # Inventory
        self.inventory = []
        self.max_inventory_size = 10
        self.selected_item_index = 0

    def update(self):
        """Update player state each turn"""
        # Update status effects
        self.status_effects = [effect for effect in self.status_effects if effect.update()]
        for effect in self.status_effects:
            effect.apply_effect(self)
        
        # Handle HP regeneration
        if self.hp_regen_cooldown > 0:
            self.hp_regen_cooldown -= 1
        elif self.hp < self.max_hp:
            self.heal(self.base_hp_regen)
        
        # Reset stun status
        self.is_stunned = False

    def take_damage(self, amount, damage_type="physical"):
        """Take damage with damage type consideration"""
        # Apply damage reduction
        reduced_amount = amount * (1 - self.damage_reduction)
        
        # Apply damage type modifiers
        if damage_type == "poison":
            reduced_amount *= 0.8  # Poison deals 80% damage
        elif damage_type == "fire":
            reduced_amount *= 1.2  # Fire deals 120% damage
        elif damage_type == "bleeding":
            reduced_amount *= 0.9  # Bleeding deals 90% damage
        
        # Apply the damage
        self.hp = max(0, self.hp - int(reduced_amount))
        
        # Set HP regeneration cooldown
        self.hp_regen_cooldown = 3  # 3 turns before HP regen starts
        
        # Check if player died
        if self.hp == 0:
            self.is_alive = False
            return True  # Player died
        return False  # Player survived

    def heal(self, amount):
        """Heal the player by the given amount"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp  # Return actual amount healed

    def add_status_effect(self, effect_type, duration, magnitude=1):
        """Add a status effect to the player"""
        # Check if effect already exists
        for effect in self.status_effects:
            if effect.effect_type == effect_type:
                # Refresh duration and update magnitude if stronger
                effect.duration = max(effect.duration, duration)
                effect.magnitude = max(effect.magnitude, magnitude)
                return
        
        # Add new effect
        self.status_effects.append(StatusEffect(effect_type, duration, magnitude))

    def remove_status_effect(self, effect_type):
        """Remove a specific status effect"""
        self.status_effects = [effect for effect in self.status_effects 
                             if effect.effect_type != effect_type]

    def gain_experience(self, amount):
        """Gain experience and handle level ups"""
        self.experience += amount
        while self.experience >= self.experience_to_level:
            self.level_up()

    def level_up(self):
        """Handle level up mechanics"""
        self.level += 1
        self.experience -= self.experience_to_level
        self.experience_to_level = int(self.experience_to_level * 1.5)
        
        # Increase stats
        self.max_hp += 15
        self.hp = self.max_hp
        self.defense += 2
        self.damage_reduction += 0.02  # Increase damage reduction by 2%
        self.base_hp_regen += 0.5  # Increase HP regeneration

    def get_status_effects(self):
        """Get a list of active status effects"""
        return [(effect.effect_type.name, effect.duration) 
                for effect in self.status_effects if effect.is_active]

    # Inventory management methods
    def add_to_inventory(self, item):
        """Add an item to the inventory"""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False

    def remove_from_inventory(self, index):
        """Remove an item from the inventory"""
        if 0 <= index < len(self.inventory):
            return self.inventory.pop(index)
        return None

    def use_selected_item(self):
        """Use the currently selected item"""
        if 0 <= self.selected_item_index < len(self.inventory):
            item = self.inventory[self.selected_item_index]
            result = item.use(self)
            self.inventory.pop(self.selected_item_index)
            if self.selected_item_index >= len(self.inventory):
                self.selected_item_index = max(0, len(self.inventory) - 1)
            return result
        return "No item selected"

    def select_next_item(self):
        """Select the next item in the inventory"""
        if self.inventory:
            self.selected_item_index = (self.selected_item_index + 1) % len(self.inventory)

    def select_previous_item(self):
        """Select the previous item in the inventory"""
        if self.inventory:
            self.selected_item_index = (self.selected_item_index - 1) % len(self.inventory)

    def get_selected_item(self):
        """Get the currently selected item"""
        if 0 <= self.selected_item_index < len(self.inventory):
            return self.inventory[self.selected_item_index]
        return None 