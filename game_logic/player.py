from .cards import Hand, Card
class Player:
    def __init__(self, order: int):
        self.order = order
        self.hand = Hand()
        self.started = False



    def add_to_hand(self, card: Card):
        card.origin = self.order
        self.hand.add_card(card)

    def remove_from_hand(self, idx:int):
        return self.hand.extract_card(idx)
    
    def create_move(self, idx_arr:list[int]) -> list[Card]:
        move = []
        for i in idx_arr: 
            move.append(self.hand.hand[i])

        return move
    
    def print_hand(self):
        hand_str = ""
        for card in self.hand.hand:
            hand_str = hand_str + f" {card.rank}{card.suit}"
        print(hand_str)

        


    def has_finished(self) -> bool:
        if len(self.hand) == 0:
            return True
        else:
            return False
        


