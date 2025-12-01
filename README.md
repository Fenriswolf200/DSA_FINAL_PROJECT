# Solitaire Game - DSA Final Project

A classic Solitaire (Klondike) card game implementation with AI-powered move suggestions using advanced data structures and algorithms.

## Installation

```bash
pip install pygame
```

## Run

```bash
python main.py
```

## Features

- **Interactive Gameplay**: Click-and-drag card movements with visual feedback
- **AI Move Suggestions**: Two algorithms to help you win
  - Tree-based DFS with memoization
  - Graph-based BFS for shortest winning path
- **Professional UI**: Clean poker table aesthetic with proper suit symbols (♥♦♣♠)
- **Undo/Redo**: Unlimited undo and redo capabilities
- **Move Counter**: Track your efficiency

## How to Play

### Objective
Move all cards to the four foundation piles (one per suit) in ascending order from Ace to King.

### Controls
- **Click** stock pile to draw cards
- **Click** and hold to drag cards
- **U** key: Undo last move
- **R** key: Redo move
- **H** key: Get AI hint (Tree-based)
- **G** key: Get AI hint (Graph-based)

### Rules
- **Tableau (Board)**: Descending rank, alternating colors
- **Foundation**: Same suit, ascending from Ace to King
- **Only Kings** can be placed on empty tableau piles
- **Only Aces** can start foundation piles

## Data Structures Used

### Stacks (LIFO)
- **FoundationPile**: Stack for Ace→King sequences
- **StockPile**: Draw pile
- **WastePile**: Discard pile

### Lists (Dynamic Arrays)
- **BoardPile**: Tableau columns with indexed access
- **Card sequences**: For moving multiple cards

### Queue (BFS)
- **Graph search**: Uses deque for breadth-first exploration

### Hash Sets
- **Memoization**: Visited states tracking to avoid cycles

### Trees
- **DFS search tree**: Explores game states recursively

## Algorithms Implemented

### 1. Depth-First Search (Tree)
- Recursive exploration of game states
- Memoization to avoid revisiting states
- Heuristic scoring for move prioritization
- Time limit: 2 seconds

### 2. Breadth-First Search (Graph)
- Level-by-level state exploration
- Finds shortest path to winning state
- Visited set for cycle detection
- Time limit: 2 seconds

### 3. State Serialization
- Canonical state representation
- Handles board position normalization
- Enables efficient state comparison

### 4. Move Validation
- Color alternation checking
- Rank sequence validation
- Rule enforcement for all pile types

## Project Structure

```
DSA_FINAL_PROJECT/
├── config.py                      # Game constants and settings
├── main.py                        # Main game loop and logic
├── ui.py                          # Pygame rendering functions
├── data_structures/
│   ├── cards.py                   # Card class
│   ├── board.py                   # Tableau pile (list-based)
│   ├── foundation.py              # Foundation pile (stack)
│   ├── stock.py                   # Stock pile (stack)
│   └── waste.py                   # Waste pile (stack)
└── game_logic/
    ├── move_utils.py              # Shared move utilities
    ├── best_move_tree.py          # DFS AI implementation
    └── best_move_graph.py         # BFS AI implementation
```

## Technical Details

### Complexity Analysis

**Tree Search (DFS):**
- Time: O(b^d) where b=branching factor, d=depth
- Space: O(d) for recursion stack + O(n) for memoization
- Optimized with state caching

**Graph Search (BFS):**
- Time: O(V + E) where V=states, E=transitions
- Space: O(V) for visited set and queue
- Guaranteed to find shortest solution

**State Serialization:**
- Time: O(n) where n=total cards
- Space: O(n) for tuple creation

### Scoring Heuristic
- Foundation cards: +10 points each
- Revealed tableau cards: +2 points each
- Empty tableau piles: +3 points each

## Game Statistics

- **52 cards** total (standard deck)
- **7 tableau columns** (28 cards initially)
- **4 foundation piles** (one per suit)
- **24 cards** in stock initially

## Contributors

Team members working on this DSA Final Project.

## Technologies

- **Python 3.9+**
- **Pygame 2.6+**
- Built-in libraries: `copy`, `collections`, `time`
