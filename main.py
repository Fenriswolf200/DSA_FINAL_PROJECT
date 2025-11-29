from game_logic.best_move_tree import find_best_move
from game_logic.best_move_graph import find_best_move_graph

from random import shuffle

from data_structures.cards import Card
from data_structures.foundation import FoundationPile
from data_structures.tableau import TableauPile
from data_structures.stock import StockPile
from data_structures.waste import WastePile
from config import RANKS, SUITS, RANK_NAMES, TABLEAU_COLUMNS


# ----------------------------
#   SOLITAIRE GAME OBJECT
# ----------------------------

class SolitaireGame:
    def __init__(self):
        self.stock = StockPile()
        self.waste = WastePile()

        self.foundations = {
            "H": FoundationPile("H"),
            "D": FoundationPile("D"),
            "C": FoundationPile("C"),
            "S": FoundationPile("S")
        }

        self.tableau = [TableauPile() for _ in range(TABLEAU_COLUMNS)]

        self.undo_stack = []
        self.redo_stack = []
        self.move_count = 0

        self.deal_cards()

    def deal_cards(self):
        deck = create_deck()
        deck_index = 0

        for i in range(TABLEAU_COLUMNS):
            for j in range(i + 1):
                card = deck[deck_index]
                card.revealed = (j == i)
                self.tableau[i].cards.append(card)
                deck_index += 1

        for i in range(deck_index, len(deck)):
            self.stock.add(deck[i])


def create_deck() -> list[Card]:
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append(Card(rank, suit))
    shuffle(deck)
    return deck


# ----------------------------
#     LEGAL MOVE GENERATOR
# ----------------------------

def list_all_legal_moves(game):
    moves = []

    # DRAW
    moves.append(("draw", None))

    # WASTE -> FOUNDATION
    if game.waste.peek():
        c = game.waste.peek()
        if game.foundations[c.suit].can_add(c):
            moves.append(("w->f", c))

    # WASTE -> TABLEAU
    if game.waste.peek():
        c = game.waste.peek()
        for i, pile in enumerate(game.tableau):
            if pile.can_add(c):
                moves.append((f"w->t{i}", c))

    # TABLEAU -> FOUNDATION
    for i, pile in enumerate(game.tableau):
        c = pile.peek()
        if c and game.foundations[c.suit].can_add(c):
            moves.append((f"t{i}->f", c))

    # TABLEAU -> TABLEAU
    for i, src in enumerate(game.tableau):
        c = src.peek()
        if c:
            for j, dst in enumerate(game.tableau):
                if i != j and dst.can_add(c):
                    moves.append((f"t{i}->t{j}", c))

    return moves


# ----------------------------
#         APPLY MOVE
# ----------------------------

def apply_move(game, move):
    name, card = move

    if name == "draw":
        drawn = game.stock.draw()
        if drawn:
            drawn.revealed = True
            game.waste.add(drawn)
        return

    # WASTE → FOUNDATION
    if name == "w->f":
        c = game.waste.pop()
        game.foundations[c.suit].add(c)
        return

    # WASTE → TABLEAU
    if name.startswith("w->t"):
        idx = int(name[4:])
        c = game.waste.pop()
        game.tableau[idx].add(c)
        return

    # TABLEAU → FOUNDATION
    if "->f" in name:
        src = int(name[1])
        c = game.tableau[src].pop()
        game.foundations[c.suit].add(c)
        return

    # TABLEAU → TABLEAU
    if "->t" in name:
        src = int(name[1])
        dst = int(name[4])
        c = game.tableau[src].pop()
        game.tableau[dst].add(c)
        return


# ----------------------------
#   PLAYER MOVE PARSER
# ----------------------------

def parse_move_input(text, legal_moves):
    text = text.strip().lower()

    for mv in legal_moves:
        if text == mv[0].lower():
            return mv
    return None


# ----------------------------
#         MAIN LOOP
# ----------------------------

if __name__ == "__main__":
    game = SolitaireGame()

    print("\nSolitaire game initialized!")
    print("Commands: draw | w->f | w->tX | tX->f | tX->tY | quit\n")

    while True:
        best_tree = find_best_move(game)
        best_graph = find_best_move_graph(game)

        print(f"\nBest move using tree:  {best_tree}")
        print(f"Best move using graph: {best_graph}")

        legal = list_all_legal_moves(game)

        print("\nLegal moves:")
        for m in legal:
            name, c = m
            card_display = "" if c is None else f" ({RANK_NAMES[c.rank]}{c.suit})"
            print(" -", name + card_display)

        user = input("\nEnter ANY move: ").strip()

        if user == "quit":
            print("Game ended.")
            break

        chosen = parse_move_input(user, legal)

        if not chosen:
            print("Invalid move. Try again.")
            continue

        apply_move(game, chosen)
        print(f"Applied move: {chosen[0]}")
