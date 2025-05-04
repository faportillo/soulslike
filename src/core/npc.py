from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

@dataclass
class DialogueOption:
    text: str
    next_dialogue: Optional[str] = None
    action: Optional[Callable] = None

class Dialogue:
    def __init__(self, id: str, text: str, options: List[DialogueOption] = None):
        self.id = id
        self.text = text
        self.options = options or []

class NPC:
    def __init__(self, x: int, y: int, name: str, char: str, color: tuple, dialogues: dict):
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.dialogues = dialogues
        self.current_dialogue_id = None
        self.is_talking = False

    def start_dialogue(self, dialogue_id: str):
        """Start a dialogue with the given ID"""
        if dialogue_id in self.dialogues:
            self.current_dialogue_id = dialogue_id
            self.is_talking = True

    def end_dialogue(self):
        """End the current dialogue"""
        self.current_dialogue_id = None
        self.is_talking = False

    def get_current_dialogue(self) -> Dialogue:
        """Get the current dialogue"""
        if self.current_dialogue_id and self.current_dialogue_id in self.dialogues:
            return self.dialogues[self.current_dialogue_id]
        return None

    def select_option(self, option_index: int) -> str:
        """Select a dialogue option and return the next dialogue ID"""
        current_dialogue = self.get_current_dialogue()
        if current_dialogue and 0 <= option_index < len(current_dialogue.options):
            option = current_dialogue.options[option_index]
            if option.action:
                option.action()
            return option.next_dialogue
        return None

# Example NPC creation function
def create_merchant(x: int, y: int) -> NPC:
    """Create a merchant NPC with dialogue"""
    dialogues = {
        "greeting": Dialogue(
            "greeting",
            "Welcome to my shop, traveler! How may I help you today?",
            [
                DialogueOption("What do you sell?", "shop"),
                DialogueOption("Tell me about yourself.", "about"),
                DialogueOption("Goodbye.", None)
            ]
        ),
        "shop": Dialogue(
            "shop",
            "I have many fine wares for sale. Would you like to see my inventory?",
            [
                DialogueOption("Yes, show me.", "inventory"),
                DialogueOption("No, thank you.", "greeting")
            ]
        ),
        "about": Dialogue(
            "about",
            "I've been trading in these parts for many years. The caves nearby are dangerous, but they hold many treasures.",
            [
                DialogueOption("Tell me about the caves.", "caves"),
                DialogueOption("Back to shop.", "greeting")
            ]
        ),
        "caves": Dialogue(
            "caves",
            "The caves are home to many creatures. Be careful if you venture inside. I can sell you some supplies if you need them.",
            [
                DialogueOption("Show me your supplies.", "shop"),
                DialogueOption("Thank you for the warning.", "greeting")
            ]
        ),
        "inventory": Dialogue(
            "inventory",
            "Here are my wares:",
            [
                DialogueOption("Buy Health Potion (10 gold)", "greeting", lambda: print("Bought health potion")),
                DialogueOption("Buy Stamina Potion (8 gold)", "greeting", lambda: print("Bought stamina potion")),
                DialogueOption("Back", "greeting")
            ]
        )
    }
    
    return NPC(x, y, "Merchant", "M", (255, 215, 0), dialogues)  # Gold color for merchant

def create_guide(x: int, y: int) -> NPC:
    """Create a guide NPC with dialogue"""
    dialogues = {
        "greeting": Dialogue(
            "greeting",
            "Ah, a new adventurer! Welcome to the caves. I can help guide you through these dangerous depths.",
            [
                DialogueOption("Tell me about the caves.", "caves"),
                DialogueOption("What should I know?", "tips"),
                DialogueOption("Goodbye.", None)
            ]
        ),
        "caves": Dialogue(
            "caves",
            "These caves are ancient and full of dangers. Each level gets progressively harder, with stronger enemies and better treasures. Be careful and always watch your health!",
            [
                DialogueOption("Any tips for survival?", "tips"),
                DialogueOption("Back", "greeting")
            ]
        ),
        "tips": Dialogue(
            "tips",
            "Here are some important tips:\n1. Save often at save points\n2. Use potions when needed\n3. Watch your stamina\n4. Explore thoroughly for hidden treasures",
            [
                DialogueOption("Tell me about the caves.", "caves"),
                DialogueOption("Back", "greeting")
            ]
        )
    }
    
    return NPC(x, y, "Guide", "G", (0, 255, 255), dialogues)  # Cyan color for guide

def create_healer(x: int, y: int) -> NPC:
    """Create a healer NPC that gives health potions"""
    def give_health_potion():
        """Give a health potion to the player"""
        from core.items import HealthPotion
        from core.game import Game
        # Get the current game instance instead of creating a new one
        game = Game.get_instance()
        game.player.add_to_inventory(HealthPotion())
        game.message = "Received a health potion!"
        game.message_timer = 60
        # Debug print
        print("\n=== Inventory Contents ===")
        for i, item in enumerate(game.player.inventory):
            print(f"{i}: {item.name} - {item.description}")
        print("=======================\n")

    dialogues = {
        "greeting": Dialogue(
            "greeting",
            "Greetings, traveler! I am a healer. Would you like a health potion?",
            [
                DialogueOption("Yes, please give me a health potion.", "give_potion", give_health_potion),
                DialogueOption("No, thank you.", None)
            ]
        ),
        "give_potion": Dialogue(
            "give_potion",
            "Here you go! Take this health potion. It will restore your health when you need it most.",
            [
                DialogueOption("Thank you!", None),
                DialogueOption("I need another one.", "greeting")
            ]
        )
    }
    
    return NPC(x, y, "Healer", "H", (0, 255, 0), dialogues)  # Green color for healer 