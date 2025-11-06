import random


class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self): #to display the card in the console like "A♠"
        return f"{self.rank}{self.suit}"
    
    def __eq__(self, other): #called when we use == to compare two cards
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False


class Deck:
    def __init__(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks] # uses an array to store the cards
        self.shuffle()
    
    def shuffle(self): # maybe we can change this for our own shuffle algorithm
        random.shuffle(self.cards)
    
    def draw(self):
        if self.cards:
            return self.cards.pop()
        return None
    
    def deal(self, num_cards: int):
        return [self.cards.pop() for _ in range(num_cards)]


class Node:
    def __init__(self, card: Card):
        self.card = card
        self.next = None


class Hand: #uses a linked list to store the cards in the hand
    def __init__(self):
        self.head = None
    
    def add_card(self, card: Card):
        new_node = Node(card)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
    
    def remove_card(self, card: Card):
        if self.head is None:
            return False
        
        if self.head.card == card:
            self.head = self.head.next
            return True
        
        current = self.head
        while current.next:
            if current.next.card == card:
                current.next = current.next.next
                return True
            current = current.next
        
        return False
    
    def __repr__(self):
        cards = []
        current = self.head
        while current:
            cards.append(str(current.card))
            current = current.next
        return str(cards)


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand()
    
    def draw_card(self, card: Card):
        self.hand.add_card(card)
    
    def discard_card(self, card: Card):
        return self.hand.remove_card(card)

