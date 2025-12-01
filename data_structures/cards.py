"""
Card representation for Solitaire game.

Provides the fundamental Card class with rank, suit, and visibility state.
Includes helper methods for color checking and string representation.
"""

class Card:
    def __init__(self, rank: int, suit: str, revealed=False):
        self.rank = rank
        self.suit = suit
        self.revealed = revealed

    def get_rank(self) -> int:
        return self.rank

    def get_suit(self) -> str:
        return self.suit
    
    def flip(self):
        # flip card face-up or face-down
        self.revealed = not self.revealed
    
    def is_red(self) -> bool:
        # check if card is red (hearts or diamonds)
        return self.suit in ["H", "D"]
    
    def is_black(self) -> bool:
        # check if card is black (clubs or spades)
        return self.suit in ["C", "S"]
    
    def __repr__(self):
        suit_symbols = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
        rank_names = {1: "A", 11: "J", 12: "Q", 13: "K"}
        rank_str = rank_names.get(self.rank, str(self.rank))
        return f"{rank_str}{suit_symbols[self.suit]}"
