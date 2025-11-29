from game2dboard import Board

from game_logic.best_move_tree import find_best_move
from game_logic.best_move_graph import find_best_move_graph

from functools import partial
from random import shuffle

from data_structures.cards import Card
from data_structures.foundation import FoundationPile
from data_structures.tableau import TableauPile
from data_structures.stock import StockPile
from data_structures.waste import WastePile
from config import RANKS, SUITS, RANK_NAMES, TABLEAU_COLUMNS

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
        self.tableau = [TableauPile() for _ in range(TABLEAU_COLUMNS)]
        
        # undo stack - stores game states for undo functionality
        self.undo_stack = []
        
        # redo stack - stores game states for redo functionality
        self.redo_stack = []
        
        # track number of moves
        self.move_count = 0
        
        # initialize the game by dealing cards
        self.deal_cards()
    
    def deal_cards(self):
        """deal cards to tableau and stock pile at game start"""
        # create and shuffle a full deck
        deck = create_deck()
        
        # deal to tableau: pile i gets i+1 cards (pile 0 gets 1, pile 1 gets 2, etc.)
        deck_index = 0
        for i in range(TABLEAU_COLUMNS):
            for j in range(i + 1):
                card = deck[deck_index]
                # only the last card (top card) of each pile is face-up
                if j == i:
                    card.revealed = True
                else:
                    card.revealed = False
                self.tableau[i].cards.append(card)
                deck_index += 1
        
        # remaining cards go to stock pile (face-down)
        for i in range(deck_index, len(deck)):
            self.stock.add(deck[i])


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


    print("Solitaire game initialized and cards dealt!")

    best = find_best_move(game)
    best_graph_move = find_best_move_graph(game)

    print(f"\nStock pile: {game.stock.size()} cards")
    print(f"Waste pile: {game.waste.size()} cards")
    print(f"Foundation piles: {len(game.foundations)} (all empty)")
    
    print("\nTableau setup:")
    for i, pile in enumerate(game.tableau):
        face_down = sum(1 for card in pile.cards if not card.revealed)
        face_up = sum(1 for card in pile.cards if card.revealed)
        print(f"  Column {i+1}: {pile.size()} cards ({face_down} face-down, {face_up} face-up)")
        if pile.size() > 0:
            top_card = pile.peek()
            rank_name = RANK_NAMES[top_card.rank]
            print(f"    Top card: {rank_name}{top_card.suit}")
    
    print("\nTotal cards:")
    total = game.stock.size() + game.waste.size() + sum(pile.size() for pile in game.tableau)
    print(f"  {total}/52 cards (should be 52)")
