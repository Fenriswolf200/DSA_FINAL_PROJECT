class Card:
    def __init__(self, rank: int, suit: str, revealed=False):
        self.rank = rank  # 1-13 (Ace=1, Jack=11, Queen=12, King=13)
        self.suit = suit  # "H", "D", "C", "S"
        self.revealed = revealed   # revealed tracks if card is face-up (True) or face-down (False)

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
