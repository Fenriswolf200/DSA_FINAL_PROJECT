from cards import Hand, Card



class CardSpace:
    def __init__(self):
        self.card_space = []

    def add_new_hand(self, hand:Hand):
        self.card_space.append(hand)

    def remove_hand(self, idx:int):
        self.card_space.pop(idx)

    def print_space(self):
        for hand in self.card_space:
            hand.print_hand()

    def mix_hands(self, idx:int, new_hand:Hand):
        self.card_space[idx].add_hand(new_hand.get_hand_list())


    def get_hand(self, idx:int) -> Hand:
        return self.card_space[idx]
    
    def get_card_from_hand(self, hand_idx:int, card_idx:int) -> Card:
        return self.card_space[hand_idx].extract_card(card_idx)
    
    def add_card_to_hand(self, hand_idx:int, card:Card):
        self.card_space[hand_idx].add_card(card)
