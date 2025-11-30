# card ranks (1-13)
RANKS = list(range(1, 14))  # 1=ace, 11=jack, 12=queen, 13=king

# card suits
SUITS = ["H", "D", "C", "S"]  # hearts, diamonds, clubs, spades

# rank display names
RANK_NAMES = {
    1: "A",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "J",
    12: "Q",
    13: "K"
}

# suit symbols for display
SUIT_SYMBOLS = {
    "H": "H",  # hearts (red)
    "D": "D",  # diamonds (red)
    "C": "C",  # clubs (black)
    "S": "S"   # spades (black)
}

# suit colors
SUIT_COLORS = {
    "H": "red",
    "D": "red",
    "C": "black",
    "S": "black"
}

# game settings
DRAW_COUNT = 1  # number of cards to draw from stock at once (1 or 3)
MAX_RECYCLES = None  # max times waste can be recycled to stock (None = unlimited)

# Board settings
BOARD_COLUMNS = 7  # number of Board piles

# foundation settings
FOUNDATION_PILES = 4  # one for each suit
