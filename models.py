import random


class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self): #to display the card in the console like "A♠"
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int):
        return [self.cards.pop() for _ in range(num_cards)]


class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card: Card):
        self.cards.append(card)
    
    def remove_card(self, card: Card):
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False
    
    def __repr__(self): #display hand as a string like "[A♠, 2♥, 3♦, 4♣]"
        return str(self.cards)


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand()
    
    def draw_card(self, card: Card):
        self.hand.add_card(card)
    
    def discard_card(self, card: Card):
        return self.hand.remove_card(card)

