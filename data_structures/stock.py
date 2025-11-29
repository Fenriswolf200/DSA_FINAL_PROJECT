# stock pile - simple stack for drawing cards

class StockPile:
    def __init__(self):
        self.cards = []  # stack (list)
    
    def draw(self) -> Card:
        # remove and return top card
        if len(self.cards) > 0:
            return self.cards.pop()
        return None
    
    def add(self, card: Card):
        # add card to stock
        card.revealed = False  # cards in stock are face-down
        self.cards.append(card)
    
    def is_empty(self) -> bool:
        return len(self.cards) == 0
    
    def size(self) -> int:
        return len(self.cards)
