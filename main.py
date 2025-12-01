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
from game_logic.best_move_tree import find_best_move, search_best_move
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

        # ||
        # ||
        # ||
        # \/

    # This function
    def deal_cards(self):
        deck = create_deck()
        deck_index = 0

        for i in range(BOARD_COLUMNS):
            for j in range(i + 1):
                card = deck[deck_index]
                card.revealed = (j == i)
                self.Board[i].cards.append(card)
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



def list_all_legal_moves(game):
    moves = []

    moves.append(("draw", None))

    if game.waste.peek():
        c = game.waste.peek()
        if game.foundations[c.suit].can_add(c):
            moves.append(("w->f", c))

    if game.waste.peek():
        c = game.waste.peek()
        for i, pile in enumerate(game.Board):
            if pile.can_add(c):
                moves.append((f"w->t{i}", c))

    for i, pile in enumerate(game.Board):
        c = pile.peek()
        if c and game.foundations[c.suit].can_add(c):
            moves.append((f"t{i}->f", c))

    for i, src in enumerate(game.Board):
        c = src.peek()
        if c:
            for j, dst in enumerate(game.Board):
                if i != j and dst.can_add(c):
                    moves.append((f"t{i}->t{j}", c))

    return moves



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



def parse_move_input(text, legal_moves):
    text = text.strip().lower()

    for mv in legal_moves:
        if text == mv[0].lower():
            return mv
    return None



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


# ---------------- AUTO-PLAY FUNCTIONS ----------------
def get_best_move_tree_object(game, depth=4):
    """get the actual Move object from tree algorithm"""
    from game_logic.best_move_tree import search_best_move
    score, move = search_best_move(game, depth)
    return move

def get_best_move_graph_object(game, max_depth=4):
    """get the actual Move object from graph algorithm"""
    from game_logic.best_move_graph import get_legal_moves as graph_get_legal_moves, apply_move as graph_apply_move, score_state, serialize_state
    from collections import deque
    visited = set()
    queue = deque()
    best_move = None
    best_score = -float("inf")
    root_state = serialize_state(game)
    queue.append((game, 0, None))
    visited.add(root_state)
    while queue:
        current_game, depth, first_move = queue.popleft()
        if depth > max_depth:
            continue
        legal_moves = graph_get_legal_moves(current_game)
        for move in legal_moves:
            new_game = graph_apply_move(current_game, move)
            state_key = serialize_state(new_game)
            if state_key in visited:
                continue
            visited.add(state_key)
            score = score_state(new_game)
            move_to_use = first_move if first_move else move
            if score > best_score:
                best_score = score
                best_move = move_to_use
            queue.append((new_game, depth+1, move_to_use))
    return best_move

def apply_move_to_game(game, move):
    """apply a Move object to the actual game state"""
    if not move:
        return False
    
    if move.move_type == "draw_stock":
        drawn = game.stock.draw()
        if drawn:
            drawn.revealed = True
            game.waste.add(drawn)
        return True
    
    if move.move_type == "reset_stock":
        if game.waste.size() > 0:
            game.stock.recycle_from(game.waste)
        return True
    
    if move.move_type == "waste_to_foundation":
        if game.waste.size() == 0:
            return False
        card = game.waste.peek()
        if card and game.foundations[card.suit].can_add(card):
            game.foundations[card.suit].add(game.waste.pop())
            return True
        return False
    
    if move.move_type == "waste_to_Board":
        if game.waste.size() == 0:
            return False
        card = game.waste.peek()
        col = move.details.get("column")
        if col is not None and game.Board[col].can_add(card):
            game.Board[col].add(game.waste.pop())
            return True
        return False
    
    if move.move_type == "Board_to_foundation":
        col = move.details.get("from")
        if col is None or game.Board[col].size() == 0:
            return False
        start_idx = move.details.get("start_idx", len(game.Board[col].cards) - 1)
        # only top card can go to foundation
        if start_idx == len(game.Board[col].cards) - 1:
            card = game.Board[col].peek()
            if card and game.foundations[card.suit].can_add(card):
                moved = game.Board[col].pop()
                game.foundations[moved.suit].add(moved)
                if game.Board[col].size() > 0:
                    game.Board[col].cards[-1].revealed = True
                return True
        return False
    
    if move.move_type == "Board_to_Board":
        src = move.details.get("from")
        dst = move.details.get("to")
        if src is None or dst is None or src == dst:
            return False
        if game.Board[src].size() == 0:
            return False
        start_idx = move.details.get("start_idx", len(game.Board[src].cards) - 1)
        # validate sequence
        if start_idx < 0 or start_idx >= len(game.Board[src].cards):
            return False
        # check if sequence is valid
        valid = True
        for i in range(start_idx, len(game.Board[src].cards)):
            if not game.Board[src].cards[i].revealed:
                valid = False
                break
        if not valid:
            return False
        # check if can add the first card of sequence
        card = game.Board[src].cards[start_idx]
        if not game.Board[dst].can_add(card):
            return False
        # move the sequence
        sequence = game.Board[src].cards[start_idx:]
        del game.Board[src].cards[start_idx:]
        for c in sequence:
            c.revealed = True
            game.Board[dst].add(c)
        if game.Board[src].size() > 0:
            game.Board[src].cards[-1].revealed = True
        return True
    
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
    hints_enabled = False
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                area, idx, card_idx = hit_test(layout, pos, game.Board)

                # handle hint button
                if layout.get("button") and layout["button"].collidepoint(pos):
                    hints_enabled = not hints_enabled
                    if hints_enabled:
                        # calculate hints when toggled on
                        best_move_tree = find_best_move(game)
                        best_move_graph = find_best_move_graph(game)
                        button_message = {
                            "graph_message": f"Best move from graph: {best_move_graph}",
                            "tree_message": f"Best move from tree: {best_move_tree}",
                        }
                    else:
                        # clear hints when toggled off
                        button_message = None
                    continue
                
                # handle auto-play tree button
                if layout.get("auto_tree_button") and layout["auto_tree_button"].collidepoint(pos):
                    move = get_best_move_tree_object(game)
                    if move:
                        apply_move_to_game(game, move)
                        # recalculate hints if enabled
                        if hints_enabled:
                            best_move_tree = find_best_move(game)
                            best_move_graph = find_best_move_graph(game)
                            button_message = {
                                "graph_message": f"Best move from graph: {best_move_graph}",
                                "tree_message": f"Best move from tree: {best_move_tree}",
                            }
                    continue
                
                # handle auto-play graph button
                if layout.get("auto_graph_button") and layout["auto_graph_button"].collidepoint(pos):
                    move = get_best_move_graph_object(game)
                    if move:
                        apply_move_to_game(game, move)
                        # recalculate hints if enabled
                        if hints_enabled:
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
                    else:
                        if game.waste.size() > 0:
                            game.stock.recycle_from(game.waste)
                    # recalculate hints after drawing from stock if hints are enabled
                    if hints_enabled:
                        best_move_tree = find_best_move(game)
                        best_move_graph = find_best_move_graph(game)
                        button_message = {
                            "graph_message": f"Best move from graph: {best_move_graph}",
                            "tree_message": f"Best move from tree: {best_move_tree}",
                        }
                    selected = None
                    continue

                if selected:
                    moved = attempt_move(game, selected, (area, idx))
                    if moved:
                        selected = None
                        if hints_enabled:
                            best_move_tree = find_best_move(game)
                            best_move_graph = find_best_move_graph(game)
                            button_message = {
                                "graph_message": f"Best move from graph: {best_move_graph}",
                                "tree_message": f"Best move from tree: {best_move_tree}",
                            }
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
        auto_tree_hover = layout.get("auto_tree_button") and layout["auto_tree_button"].collidepoint(mouse_pos)
        auto_graph_hover = layout.get("auto_graph_button") and layout["auto_graph_button"].collidepoint(mouse_pos)

        draw_stock(screen, game.stock, layout["stock"], font_small, selected)
        draw_waste(screen, game.waste, layout["waste"], font, font_small, selected)
        draw_foundations(screen, game.foundations, layout["foundations"], font, font_small, selected)
        draw_Board(screen, game.Board, layout["Board"], font, font_small, selected)
        
        # draw buttons
        if layout.get("auto_tree_button"):
            draw_button(screen, layout["auto_tree_button"], "Auto Tree", font_small, bool(auto_tree_hover))
        if layout.get("auto_graph_button"):
            draw_button(screen, layout["auto_graph_button"], "Auto Graph", font_small, bool(auto_graph_hover))
        if layout.get("button"):
            button_label = "Hide Hint" if hints_enabled else "Show Hint"
            draw_button(screen, layout["button"], button_label, font_small, bool(button_hover))

        if button_message:
            draw_text(screen, button_message["graph_message"], (MARGIN, WINDOW_H - MARGIN - MARGIN - 20 - 22), font_small, (255, 255, 255))
            draw_text(screen, button_message["tree_message"], (MARGIN, WINDOW_H - MARGIN - 20 - 22), font_small, (255, 255, 255))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)
