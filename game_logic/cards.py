
# Origin is used to track the previous position of the card
# -1 is the deck
# 0-3 are player numbers
# 3< is the position of the hand in the board + 3
class Card:
    def __init__(self, rank: int, suit: int):
        self.rank = rank
        self.suit = suit

    def get_rank(self) -> int:
        return self.rank

    def get_suit(self) -> int:
        return self.suit



class Hand:
    def __init__(self, hand_number=None):
        self.hand = []
        self.hand_number = hand_number
        
    def add_card(self, new_card: Card):
        self.hand.append(new_card)

    def get_card(self, idx:int):
        return self.hand[idx]
    
    def extract_card(self, idx:int):
        return self.hand.pop(idx)
    
    
    def add_hand(self, new_hand:list):
        self.hand = self.hand + new_hand

    def get_hand_list(self):
        return self.hand


    def print_hand(self):
        hand_str = ""
        for card in self.hand:
            hand_str = hand_str + f"{card.rank}{card.suit} "
        print(hand_str)

    def sort_hand(self):

        for i in range(1,len(self.hand)):


            key = self.hand[i]
            j = i-1

            while j >= 0 and key.get_rank() < self.hand[j].get_rank():
                self.hand[j+1] = self.hand[j]
                j -= 1
            self.hand[j + 1] = key





class DeckCard:
    def __init__(self, card: Card, next=None):
        self.card = card
        self.next = next

    def draw_card(self) -> Card:
        if self.next is None:
            return None
        temp = self.card
        self.card = self.next.card
        self.next = self.next.next
        return temp