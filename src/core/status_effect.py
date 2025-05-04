from enum import Enum, auto

class EffectType(Enum):
    POISON = auto()
    REGENERATION = auto()
    BLEEDING = auto()
    BURNING = auto()
    STUNNED = auto()

class StatusEffect:
    def __init__(self, effect_type, duration, magnitude=1):
        self.effect_type = effect_type
        self.duration = duration
        self.magnitude = magnitude
        self.is_active = True

    def update(self):
        """Update the effect duration and return if it should be removed"""
        self.duration -= 1
        if self.duration <= 0:
            self.is_active = False
        return self.is_active

    def apply_effect(self, target):
        """Apply the effect to the target"""
        if not self.is_active:
            return

        if self.effect_type == EffectType.POISON:
            target.take_damage(self.magnitude, "poison")
        elif self.effect_type == EffectType.REGENERATION:
            target.heal(self.magnitude)
        elif self.effect_type == EffectType.BLEEDING:
            target.take_damage(self.magnitude, "bleeding")
        elif self.effect_type == EffectType.BURNING:
            target.take_damage(self.magnitude, "fire")
        elif self.effect_type == EffectType.STUNNED:
            target.is_stunned = True 