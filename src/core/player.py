from core.entity import Entity
from core.status_effect import StatusEffect, EffectType
from utils.colors import COLOR_PLAYER
from enum import Enum
import random

class Attribute(Enum):
    STRENGTH = "Strength"
    DEXTERITY = "Dexterity"
    VITALITY = "Vitality"
    INTELLIGENCE = "Intelligence"
    FAITH = "Faith"

class Skill(Enum):
    SWORD_MASTERY = "Sword Mastery"
    SHIELD_BLOCK = "Shield Block"
    EVASION = "Evasion"
    SPELLCASTING = "Spellcasting"
    HEALING = "Healing"

class Player(Entity):
    def __init__(self, x, y):
        """Initialize a new player"""
        super().__init__(
            x=x,
            y=y,
            char="@",
            color=COLOR_PLAYER
        )
        # Core attributes
        self.attributes = {
            Attribute.STRENGTH: 10,
            Attribute.DEXTERITY: 10,
            Attribute.VITALITY: 10,
            Attribute.INTELLIGENCE: 10,
            Attribute.FAITH: 10
        }
        
        # Skills and their levels
        self.skills = {
            Skill.SWORD_MASTERY: 1,
            Skill.SHIELD_BLOCK: 1,
            Skill.EVASION: 1,
            Skill.SPELLCASTING: 1,
            Skill.HEALING: 1
        }
        
        # Health attributes (now based on VITALITY)
        self.max_hp = self.calculate_max_hp()
        self.hp = self.max_hp
        self.base_hp_regen = self.calculate_hp_regen()
        self.hp_regen_cooldown = 0
        
        # Stamina attributes (based on DEXTERITY)
        self.max_stamina = self.calculate_max_stamina()
        self.stamina = self.max_stamina
        self.stamina_regen = self.calculate_stamina_regen()
        self.stamina_regen_cooldown = 0
        
        # Combat attributes (now based on attributes)
        self.defense = self.calculate_defense()
        self.damage_reduction = self.calculate_damage_reduction()
        self.attack_power = self.calculate_attack_power()
        self.critical_chance = self.calculate_critical_chance()
        self.dodge_chance = self.calculate_dodge_chance()
        
        # Status effects
        self.status_effects = []
        self.is_stunned = False
        
        # Level and experience
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100
        self.attribute_points = 0
        self.skill_points = 0
        
        # Inventory
        self.inventory = []
        self.max_inventory_size = 10
        self.selected_item_index = 0

        # Equipment
        self.equipped_weapon = None
        self.equipped_armor = None
        
        # Combat state
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_direction = (0, 0)
        self.is_blocking = False
        self.block_cooldown = 0
        self.is_dodging = False
        self.dodge_cooldown = 0
        self.dodge_direction = (0, 0)
        
        # Movement state
        self.is_moving = False
        self.move_cooldown = 0
        self.move_direction = (0, 0)
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Combat history
        self.last_damage_taken = 0
        self.last_damage_dealt = 0
        self.last_heal_amount = 0
        
        # Death state
        self.is_dead = False
        self.death_timer = 0
        
        # Respawn state
        self.respawn_timer = 0
        self.respawn_point = None
        
        # Save state
        self.last_save_point = None
        self.last_save_level = None

    def calculate_max_hp(self):
        """Calculate max HP based on VITALITY"""
        base_hp = 100
        vitality_bonus = self.attributes[Attribute.VITALITY] * 10
        return base_hp + vitality_bonus

    def calculate_hp_regen(self):
        """Calculate HP regeneration based on VITALITY"""
        base_regen = 1
        vitality_bonus = self.attributes[Attribute.VITALITY] * 0.2
        return base_regen + vitality_bonus

    def calculate_max_stamina(self):
        """Calculate max stamina based on DEXTERITY"""
        base_stamina = 100
        dexterity_bonus = self.attributes[Attribute.DEXTERITY] * 5
        return base_stamina + dexterity_bonus

    def calculate_stamina_regen(self):
        """Calculate stamina regeneration rate based on DEXTERITY"""
        base_regen = 1
        dexterity_bonus = self.attributes[Attribute.DEXTERITY] * 0.2
        return base_regen + dexterity_bonus

    def calculate_defense(self):
        """Calculate defense based on attributes and skills"""
        base_defense = 10
        vitality_bonus = self.attributes[Attribute.VITALITY] * 2
        shield_bonus = self.skills[Skill.SHIELD_BLOCK] * 3
        return base_defense + vitality_bonus + shield_bonus

    def calculate_damage_reduction(self):
        """Calculate damage reduction based on defense"""
        base_reduction = 0.1
        defense_bonus = self.defense * 0.005
        return min(0.75, base_reduction + defense_bonus)  # Cap at 75%

    def calculate_attack_power(self):
        """Calculate attack power based on STRENGTH and skills"""
        base_power = 10
        strength_bonus = self.attributes[Attribute.STRENGTH] * 2
        sword_bonus = self.skills[Skill.SWORD_MASTERY] * 3
        return base_power + strength_bonus + sword_bonus

    def calculate_critical_chance(self):
        """Calculate critical hit chance based on DEXTERITY"""
        base_chance = 0.05
        dexterity_bonus = self.attributes[Attribute.DEXTERITY] * 0.005
        return min(0.5, base_chance + dexterity_bonus)  # Cap at 50%

    def calculate_dodge_chance(self):
        """Calculate dodge chance based on DEXTERITY and EVASION skill"""
        base_chance = 0.05
        dexterity_bonus = self.attributes[Attribute.DEXTERITY] * 0.003
        evasion_bonus = self.skills[Skill.EVASION] * 0.02
        return min(0.4, base_chance + dexterity_bonus + evasion_bonus)  # Cap at 40%

    def update(self):
        """Update player state"""
        # Update health regeneration
        if self.hp_regen_cooldown > 0:
            self.hp_regen_cooldown -= 1
        elif self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.base_hp_regen)
            self.hp_regen_cooldown = 10  # 10 frames cooldown

        # Update stamina regeneration
        if self.stamina_regen_cooldown > 0:
            self.stamina_regen_cooldown -= 1
        elif self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
            self.stamina_regen_cooldown = 5  # 5 frames cooldown

        # Update status effects
        for effect in self.status_effects[:]:
            effect.duration -= 1
            if effect.duration <= 0:
                self.status_effects.remove(effect)
                if effect.effect_type == "STUNNED":
                    self.is_stunned = False

    def take_damage(self, amount, damage_type="physical"):
        """Take damage with damage type consideration"""
        # Check for dodge
        if random.random() < self.dodge_chance:
            return False  # Dodged the attack
        
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
        self.hp_regen_cooldown = 3
        
        # Check if player died
        if self.hp == 0:
            self.is_alive = False
            return True
        return False

    def heal(self, amount):
        """Heal the player by the given amount"""
        # Apply healing bonus from FAITH
        faith_bonus = 1 + (self.attributes[Attribute.FAITH] * 0.05)
        healing_amount = amount * faith_bonus
        
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + healing_amount)
        return self.hp - old_hp

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
        
        # Grant attribute and skill points
        self.attribute_points += 2
        self.skill_points += 1
        
        # Update derived stats
        self.max_hp = self.calculate_max_hp()
        self.hp = self.max_hp
        self.base_hp_regen = self.calculate_hp_regen()
        self.defense = self.calculate_defense()
        self.damage_reduction = self.calculate_damage_reduction()
        self.attack_power = self.calculate_attack_power()
        self.critical_chance = self.calculate_critical_chance()
        self.dodge_chance = self.calculate_dodge_chance()

    def increase_attribute(self, attribute):
        """Increase an attribute if points are available"""
        if self.attribute_points > 0 and attribute in self.attributes:
            self.attributes[attribute] += 1
            self.attribute_points -= 1
            
            # Update derived stats
            self.max_hp = self.calculate_max_hp()
            self.base_hp_regen = self.calculate_hp_regen()
            self.defense = self.calculate_defense()
            self.damage_reduction = self.calculate_damage_reduction()
            self.attack_power = self.calculate_attack_power()
            self.critical_chance = self.calculate_critical_chance()
            self.dodge_chance = self.calculate_dodge_chance()
            return True
        return False

    def increase_skill(self, skill):
        """Increase a skill if points are available"""
        if self.skill_points > 0 and skill in self.skills:
            self.skills[skill] += 1
            self.skill_points -= 1
            
            # Update derived stats
            self.defense = self.calculate_defense()
            self.attack_power = self.calculate_attack_power()
            self.dodge_chance = self.calculate_dodge_chance()
            return True
        return False

    def get_attribute_modifier(self, attribute):
        """Get the modifier for an attribute (used for skill checks)"""
        value = self.attributes[attribute]
        return (value - 10) // 2

    def get_skill_level(self, skill):
        """Get the effective level of a skill including attribute modifiers"""
        base_level = self.skills[skill]
        if skill == Skill.SWORD_MASTERY:
            return base_level + self.get_attribute_modifier(Attribute.STRENGTH)
        elif skill == Skill.SHIELD_BLOCK:
            return base_level + self.get_attribute_modifier(Attribute.VITALITY)
        elif skill == Skill.EVASION:
            return base_level + self.get_attribute_modifier(Attribute.DEXTERITY)
        elif skill == Skill.SPELLCASTING:
            return base_level + self.get_attribute_modifier(Attribute.INTELLIGENCE)
        elif skill == Skill.HEALING:
            return base_level + self.get_attribute_modifier(Attribute.FAITH)
        return base_level

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

    def use_item(self, item):
        """Use an item from the inventory"""
        if item in self.inventory:
            if item.use(self):
                self.inventory.remove(item)
                return True
        return False 