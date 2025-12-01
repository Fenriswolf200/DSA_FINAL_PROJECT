# We start off by importing all of our necessary libraries.

from random import shuffle # We use this function to shuffle our deck of cards

# From config we import the ranks and suits that are available for the 
# cards and the number of columns that are in the board.
from config import RANKS, SUITS, BOARD_COLUMNS 

# Here we import various data structures that we have predefined 
# to access various functionalities
from data_structures.cards import Card # This class represents a single card element
# These Classes will create different piles that store the cards that the 
# user plays with.
from data_structures.foundation import FoundationPile 
from data_structures.board import BoardPile
from data_structures.stock import StockPile
from data_structures.waste import WastePile

# These functions manage the logic for the hints that are provided to the user
from game_logic.best_move_tree import find_best_move
from game_logic.best_move_graph import find_best_move_graph

# Here we import pygame to handle the graphics
import pygame 

# We create ui functions that actually render the game
# We import __Board_card_index_at_pos separately from the rest of the 
# library because for some reason otherwise the game was breaking
from ui import _Board_card_index_at_pos
from ui import *



# This is the SolitaireGame class which stores all of the 
# active states of the game. Here we store the piles that 
# the user plays on
class SolitaireGame:
    def __init__(self):
        # decks that handle everything that has to do with drawing cards
        self.stock = StockPile()
        self.waste = WastePile()

        # one foundation per suit of card
        self.foundations = {
            "H": FoundationPile("H"),
            "D": FoundationPile("D"),
            "C": FoundationPile("C"),
            "S": FoundationPile("S")
        }


        # This creates a list with the number of Board columns defined in config
        self.Board = [BoardPile() for _ in range(BOARD_COLUMNS)] # 

        self.deal_cards() 


    # This function creates a deck of cards :|
    def create_deck(self) -> list[Card]:
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append(Card(rank, suit))
        shuffle(deck)
        return deck

    # This function deals an x amount of cards increasing from 1 to 8 
    # to each of the board columns and adds the remaining cards to the 
    # stock
    def deal_cards(self):
        deck = self.create_deck()
        deck_index = 0

        for i in range(BOARD_COLUMNS):
            for j in range(i + 1):
                card = deck[deck_index]
                card.revealed = (j == i)
                self.Board[i].cards.append(card)
                deck_index += 1

        for i in range(deck_index, len(deck)):
            self.stock.add(deck[i])


# This function executes a move that moves a card in the game.
# draw takes the top card from the stock and moves it to the waste
# w->f moves the top card from waste and adds it to the matching foundation pile
# w->tX moves the top card from waste and adds it to column x
# tX->f moves the top card from column x and adds it to the suit's foundation
# tX->tY moves the top card from column x to column y
def apply_move(game, move):
    name, card = move

    if name == "draw":
        drawn = game.stock.draw()
        if drawn:
            drawn.revealed = True
            game.waste.add(drawn)
        return

    if name == "w->f":
        c = game.waste.pop()
        game.foundations[c.suit].add(c)
        return

    if name.startswith("w->t"):
        idx = int(name[4:])
        c = game.waste.pop()
        game.Board[idx].add(c)
        return

    if "->f" in name:
        src = int(name[1])
        c = game.Board[src].pop()
        game.foundations[c.suit].add(c)
        return

    if "->t" in name:
        src = int(name[1])
        dst = int(name[4])
        c = game.Board[src].pop()
        game.Board[dst].add(c)
        return




# This function identifies what area of the board a mouse click targets and returns a descriptor for it
def hit_test(layout: dict, pos, Board: list):
    x, y = pos
    if layout["stock"].collidepoint(x, y):
        return ("stock", -1, -1)
    if layout["waste"].collidepoint(x, y):
        return ("waste", -1, -1)
    for i, r in enumerate(layout["foundations"]):
        if r.collidepoint(x, y):
            return ("foundation", i, -1)
    for i, r in enumerate(layout["Board"]):
        card_idx = _Board_card_index_at_pos(Board[i], r, pos)
        if card_idx != -1 or Rect(r.x, r.y, r.w, max(r.h, WINDOW_H - r.y - MARGIN)).collidepoint(x, y):
            return ("Board", i, card_idx)
    return ("none", -1, -1)


def _is_valid_Board_sequence(pile: BoardPile, start_idx: int) -> bool:
    if start_idx < 0 or start_idx >= len(pile.cards):
        return False
    for i in range(start_idx, len(pile.cards)):
        if not pile.cards[i].revealed:
            return False
    for i in range(start_idx, len(pile.cards) - 1):
        a = pile.cards[i]
        b = pile.cards[i + 1]
        if a.rank != b.rank + 1:
            return False
        if a.is_red() == b.is_red():
            return False
    return True


def attempt_move(game: SolitaireGame, selected: Dict[str, Any], target: Tuple[str, int]) -> bool:
    src_type = selected["type"]
    src_idx = selected.get("index", -1)
    dst_type, dst_idx = target

    if src_type == "waste" and game.waste.size() > 0:
        card = game.waste.peek()
        if dst_type == "foundation":
            suit_order = ["H", "D", "C", "S"]
            suit = suit_order[dst_idx]
            if game.foundations[suit].can_add(card):
                game.foundations[suit].add(game.waste.pop())
                return True
        if dst_type == "Board":
            if game.Board[dst_idx].can_add(card):
                game.Board[dst_idx].add(game.waste.pop())
                return True
        return False

    if src_type == "Board" and game.Board[src_idx].size() > 0:
        src_card_index = selected.get("card_index", len(game.Board[src_idx].cards) - 1)
        if not _is_valid_Board_sequence(game.Board[src_idx], src_card_index):
            return False
        moving_card = game.Board[src_idx].cards[src_card_index]
        if dst_type == "foundation":
            suit_order = ["H", "D", "C", "S"]
            suit = suit_order[dst_idx]
            if src_card_index == len(game.Board[src_idx].cards) - 1 and game.foundations[suit].can_add(moving_card):
                moved = game.Board[src_idx].pop()
                game.foundations[suit].add(moved)
                if game.Board[src_idx].size() > 0:
                    game.Board[src_idx].cards[-1].revealed = True
                return True
        if dst_type == "Board":
            if src_idx != dst_idx and game.Board[dst_idx].can_add(moving_card):
                run = game.Board[src_idx].cards[src_card_index:]
                del game.Board[src_idx].cards[src_card_index:]
                for c in run:
                    c.revealed = True
                    game.Board[dst_idx].add(c)
                if game.Board[src_idx].size() > 0:
                    game.Board[src_idx].cards[-1].revealed = True
                return True
        return False

    return False



if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Solitaire (Pygame)")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('arial', 24)
    font_small = pygame.font.SysFont('arial', 18)

    game = SolitaireGame()
    layout = build_layout(WINDOW_W, WINDOW_H)
    selected: Optional[Dict[str, Any]] = None
    best_suggestion = None
    show_suggestion_ms = 0
    button_message = None
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                area, idx, card_idx = hit_test(layout, pos, game.Board)

                if layout.get("button") and layout["button"].collidepoint(pos):
                    best_move_tree = find_best_move(game)
                    best_move_graph = find_best_move_graph(game)
                    button_message = {
                        "graph_message": f"Best move from graph: {best_move_graph}",
                        "tree_message": f"Best move from tree: {best_move_tree}",
                    }
                    continue

                if area == "stock":
                    drawn = game.stock.draw()
                    if drawn:
                        drawn.revealed = True
                        game.waste.add(drawn)
                        button_message = None
                    else:
                        if game.waste.size() > 0:
                            game.stock.recycle_from(game.waste)
                            button_message = None
                    selected = None
                    continue

                if selected:
                    moved = attempt_move(game, selected, (area, idx))
                    if moved:
                        selected = None
                        button_message = None
                        continue
                    if selected.get("type") == area and selected.get("index", -1) == idx and selected.get("card_index", -1) == card_idx:
                        selected = None
                        continue

                if area == "waste" and game.waste.size() > 0:
                    selected = {"type": "waste"}
                elif area == "Board" and game.Board[idx].size() > 0 and card_idx != -1 and game.Board[idx].cards[card_idx].revealed:
                    selected = {"type": "Board", "index": idx, "card_index": card_idx}
                else:
                    selected = None

        screen.fill(BACKGROUND_COLOR)

        mouse_pos = pygame.mouse.get_pos()
        button_hover = layout.get("button") and layout["button"].collidepoint(mouse_pos)

        draw_stock(screen, game.stock, layout["stock"], font_small, selected)
        draw_waste(screen, game.waste, layout["waste"], font, font_small, selected)
        draw_foundations(screen, game.foundations, layout["foundations"], font, font_small, selected)
        draw_Board(screen, game.Board, layout["Board"], font, font_small, selected)
        if layout.get("button"):
            draw_button(screen, layout["button"], "Show Hint", font_small, bool(button_hover))

        if button_message:
            draw_text(screen, button_message["graph_message"], (MARGIN, WINDOW_H - MARGIN - MARGIN - 20 - 22), font_small, (255, 255, 255))
            draw_text(screen, button_message["tree_message"], (MARGIN, WINDOW_H - MARGIN - 20 - 22), font_small, (255, 255, 255))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)
