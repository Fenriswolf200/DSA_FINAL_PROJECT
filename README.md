# Rummy Card Game - Pygame Visual Interface

## Quick Start

Install pygame:
```bash
pip install pygame
```

Run the game:
```bash
python3 pygame_rummy.py
```

The game starts immediately with 2 players!

## How to Play

### Controls
- **Click cards** in your hand to select/deselect them (they turn gold and lift up)
- **SORT** - Organize your hand by rank
- **PLAY** - Play selected cards to the board
- **DRAW** - Draw a card from the deck (ends your turn)
- **DONE** - End your turn (win if you have no cards left)

### Gameplay
1. Game starts with Player 1's turn
2. Each player has 7 cards initially
3. Select cards by clicking them (gold border = selected)
4. Play sets or runs to the board
5. First player to play all cards wins!

## Features

- ✅ Beautiful poker table aesthetic
- ✅ 2 player support
- ✅ Interactive card selection with visual feedback
- ✅ Sort button (automatically clears selections)
- ✅ Clean, simple interface
- ✅ Instant game start (no menu)
- ✅ Professional card design with suits (♥♦♣♠)
- ✅ Smooth 60 FPS gameplay

## File Structure

- `pygame_rummy.py` - Visual interface (319 lines, simplified!)
- `cards.py` - Card, Hand, and Deck classes
- `player.py` - Player class
- `spaces.py` - Board/CardSpace class
- `main.py` - Original text-based game logic

## Running the Game

To run the visual version of the game:
```bash
python3 pygame_rummy.py
```

To run the original text-based version:
```bash
python3 main.py
```

