RANKS = list(range(1, 14))
ACE = 1
JACK = 11
QUEEN = 12
KING = 13

SUITS = ["H", "D", "C", "S"]

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

SUIT_SYMBOLS = {
    "H": "♥",
    "D": "♦",
    "C": "♣",
    "S": "♠"
}

SUIT_COLORS = {
    "H": "red",
    "D": "red",
    "C": "black",
    "S": "black"
}

# game settings
DRAW_COUNT = 1
MAX_RECYCLES = None

BOARD_COLUMNS = 7
FOUNDATION_PILES = 4

# scoring constants for AI
FOUNDATION_CARD_POINTS = 10
REVEALED_CARD_POINTS = 2
EMPTY_PILE_POINTS = 3
