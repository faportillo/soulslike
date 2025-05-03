# Python Roguelike Game

A roguelike game written in Python using the libtcod library. The game currently features:

- Window-based graphics using libtcod
- Field of view and fog of war
- Player movement with collision detection
- Simple map generation
- Color-coded walls and floors

## Requirements

- Python 3.7 or higher
- libtcod
- numpy

## Installation

1. Create a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Running the Game

Simply run:

```bash
python3 game.py
```

## Controls

- Arrow keys: Move the player
- ESC: Quit the game

## Game Elements

- @ : Player (white)
- # : Walls (brown/blue)
- . : Floor (yellow/blue)

## Features

- Field of View: Areas you haven't seen are dark
- Explored Areas: Previously seen areas remain visible but dimmed
- Collision Detection: Can't walk through walls
- Color-coded tiles for better visibility

## Future Plans

- Add enemies and combat system
- Implement items and inventory
- Add more complex map generation with rooms and corridors
- Add game progression and levels
- Implement a proper UI with health, inventory, etc.
