import random


class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self): # to display the card in the console like "A♠"
        return f"{self.rank}{self.suit}"
    
    def __eq__(self, other): # called when we use == to compare two cards
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False


class Queue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)


class Deck:
    def __init__(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(cards) # maybe we can change this for our own shuffle algorithm
        self.cards = Queue() # uses a queue to store the cards
        for card in cards:
            self.cards.enqueue(card)
    
    def shuffle(self): # enqueue to list and then shuffle and then enqueue again
        cards_list = []
        while not self.cards.is_empty():
            cards_list.append(self.cards.dequeue())
        random.shuffle(cards_list) # maybe we can change this for our own shuffle algorithm
        for card in cards_list:
            self.cards.enqueue(card)
    
    def draw(self):
        return self.cards.dequeue()
    
    def deal(self, num_cards: int):
        dealt = []
        for _ in range(num_cards):
            if not self.cards.is_empty():
                dealt.append(self.cards.dequeue())
        return dealt


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
    
    def __repr__(self): # to display the hand in the console like "[A♠, 2♥, 3♦, 4♣]"
        return str(self.cards)


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand()
    
    def draw_card(self, card: Card):
        self.hand.add_card(card)
    
    def discard_card(self, card: Card):
        return self.hand.remove_card(card)

