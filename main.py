from game2dboard import Board
from functools import partial
from random import shuffle

from data_structures.cards import Card
from data_structures.foundation import FoundationPile
from data_structures.tableau import TableauPile
from data_structures.stock import StockPile
from data_structures.waste import WastePile


# solitaire uses ranks 1-13 (Ace through King)
RANKS = list(range(1, 14))  # 1=Ace, 11=Jack, 12=Queen, 13=King
SUITS = ["H", "D", "C", "S"]  # Hearts, Diamonds, Clubs, Spades

# solitaire game class with data structures
class SolitaireGame:
    def __init__(self):
        # stock pile (draw pile) - stack for cards to draw from
        self.stock = StockPile()
        
        # waste pile (discard pile) - stack for drawn cards
        self.waste = WastePile()
        
        # foundation piles (4 stacks, one per suit: H, D, C, S)
        # cards must be placed in ascending order (Ace to King)
        self.foundations = {
            "H": FoundationPile("H"),  # hearts
            "D": FoundationPile("D"),  # diamonds
            "C": FoundationPile("C"),  # clubs
            "S": FoundationPile("S")   # spades
        }
        
        # tableau piles (7 columns)
        # each column can contain face-down and face-up cards
        self.tableau = [TableauPile() for _ in range(7)]
        
        # undo stack - stores game states for undo functionality
        self.undo_stack = []
        
        # redo stack - stores game states for redo functionality
        self.redo_stack = []
        
        # track number of moves
        self.move_count = 0


# helper function to create a full deck of 52 cards
def create_deck() -> list[Card]:
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append(Card(rank, suit))
    
    # shuffle the deck
    shuffle(deck)
    return deck


if __name__ == "__main__":
    # initialize solitaire game
    game = SolitaireGame()
    print("Solitaire game initialized")
    print(f"Stock pile: {game.stock.size()} cards")
    print(f"Waste pile: {game.waste.size()} cards")
    print(f"Tableau columns: {len(game.tableau)}")
    print(f"Foundation piles: {len(game.foundations)}")
    print("\nData structures:")
    print(f"  - Stock: StockPile (stack)")
    print(f"  - Waste: WastePile (stack)")
    print(f"  - Foundations: 4 FoundationPile objects (stacks)")
    print(f"  - Tableau: 7 TableauPile objects (lists)")
