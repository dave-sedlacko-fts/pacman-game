# Pacman Game

A classic Pacman game built with Python and Pygame featuring:
- Four ghosts with different AI behaviors (Blinky, Pinky, Inky, Clyde)
- Power pellets that let you eat ghosts
- Local high score tracking by name
- Customizable Pacman colors (Yellow, Blue, Pink, Purple, Green)

## Installation

### Prerequisites

You need Python 3.7 or higher installed on your system.

#### Windows

1. **Install Python** (if not already installed):
   - Download Python from https://www.python.org/downloads/
   - During installation, **check the box "Add Python to PATH"**
   - Click "Install Now"

2. **Install Pygame**:
   Open Command Prompt (search for "cmd" in Start menu) and run:
   ```
   pip install pygame
   ```

#### Mac

1. **Install Python** (if not already installed):
   - Option A: Download from https://www.python.org/downloads/
   - Option B: Install via Homebrew (recommended):
     ```
     brew install python
     ```

2. **Install Pygame**:
   Open Terminal and run:
   ```
   pip3 install pygame
   ```

### Running the Game

#### Windows
```
cd path\to\pacman_game
python pacman.py
```

#### Mac
```
cd path/to/pacman_game
python3 pacman.py
```

## How to Play

### Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move Pacman |
| ESC | Return to menu |
| ENTER | Select menu options |
| C | Change Pacman color (from menu) |
| H | View high scores (from menu) |
| Q | Quit (from menu) |
| R | Retry (from game over screen) |

### Gameplay

1. **Objective**: Eat all the pellets in the maze while avoiding ghosts
2. **Pellets**: Small dots worth 10 points each
3. **Power Pellets**: Large flashing dots worth 50 points - eating one makes ghosts vulnerable (turn blue) for a short time
4. **Ghosts**:
   - When normal: Avoid them! Touching a ghost costs you a life
   - When vulnerable (blue): Eat them for bonus points (200, 400, 800, 1600)
5. **Lives**: You start with 3 lives
6. **Levels**: Complete a level by eating all pellets. The maze resets with all pellets restored.

### Ghost Behaviors

- **Blinky (Red)**: Directly chases Pacman
- **Pinky (Pink)**: Tries to ambush by aiming ahead of Pacman
- **Inky (Cyan)**: Unpredictable mix of chasing and random movement
- **Clyde (Orange)**: Moves randomly

### High Scores

- High scores are saved locally in `highscores.json`
- Top 10 scores are kept
- Enter your name (up to 10 characters) when you achieve a high score
- Scores are based on total pellets and ghosts eaten

## Customization

### Pacman Colors

From the main menu, press **C** to access the color selection screen:
- Yellow (default)
- Blue
- Pink
- Purple
- Green

Use UP/DOWN arrows to select, ENTER to confirm.

## Troubleshooting

### "pygame not found" error
Make sure you installed pygame with the correct pip:
- Windows: `pip install pygame`
- Mac: `pip3 install pygame`

### "python not found" error
- Windows: Reinstall Python and make sure "Add to PATH" is checked
- Mac: Use `python3` instead of `python`

### Game window doesn't appear
- Make sure no other application is blocking the display
- Try running from a terminal/command prompt to see error messages

### Performance issues
- Close other applications
- The game runs at 60 FPS and should work on most systems

## File Structure

```
pacman_game/
├── pacman.py        # Main game file
├── highscores.json  # High scores (created after first game)
└── README.md        # This file
```
