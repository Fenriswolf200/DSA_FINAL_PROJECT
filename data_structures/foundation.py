"""
Foundation pile implementation for Solitaire.

Stack-based data structure for building suit sequences from Ace to King.
Each foundation pile is suit-specific and enforces ascending rank order.
"""

from data_structures.cards import Card
from config import ACE

class FoundationPile:
    def __init__(self, suit: str):
        self.suit = suit
        self.cards = []
    
    def can_add(self, card: Card) -> bool:
        if card.suit != self.suit:
            return False
        
        if len(self.cards) == 0:
            return card.rank == ACE
        
        # otherwise, must be next rank in sequence
        return card.rank == self.cards[-1].rank + 1
    
    def add(self, card: Card) -> bool:
        if self.can_add(card):
            self.cards.append(card)
            return True
        return False
    
    def peek(self) -> Card:
        # look at top card without removing
        if len(self.cards) > 0:
            return self.cards[-1]
        return None
    
    def pop(self) -> Card:
        # remove and return top card
        if len(self.cards) > 0:
            return self.cards.pop()
        return None
    
    def size(self) -> int:
        return len(self.cards)
