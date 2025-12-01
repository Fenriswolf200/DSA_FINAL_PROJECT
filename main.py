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
    
    def is_won(self) -> bool:
        for suit in ["H", "D", "C", "S"]:
            if len(self.foundations[suit].cards) != 13:
                return False
        return True
    
    def has_valid_moves(self) -> bool:
        if self.stock.size() > 0 or self.waste.size() > 0:
            return True
        for pile in self.Board:
            if pile.size() > 0:
                for other_pile in self.Board:
                    if pile is not other_pile and other_pile.can_add(pile.peek()):
                        return True
        return False


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


# ---------------- AUTO-PLAY FUNCTIONS ----------------
def detect_move_cycle(move_history, threshold=8):
    """detect if the same moves are being reversed repeatedly or stuck in patterns"""
    if len(move_history) < 16:
        return False
    
    # check for immediate reversals (A->B, B->A) - must be consecutive
    reversal_count = 0
    i = len(move_history) - 1
    
    while i >= 1 and reversal_count < threshold:
        current = move_history[i]
        previous = move_history[i - 1]
        
        if (current.get("from") == previous.get("to") and 
            current.get("to") == previous.get("from") and
            current.get("type") == previous.get("type")):
            reversal_count += 1
            i -= 2
        else:
            break
    
    # only trigger if we have 8+ consecutive reversals
    if reversal_count >= threshold:
        return True
    
    # check for repeated move patterns (same move made many times)
    recent_moves = move_history[-30:]
    if len(recent_moves) >= 20:
        # count how many times the last move appears in recent history
        last_move = recent_moves[-1]
        last_move_str = f"{last_move.get('type')}_{last_move.get('from')}_{last_move.get('to')}"
        
        count = 0
        for move in recent_moves:
            move_str = f"{move.get('type')}_{move.get('from')}_{move.get('to')}"
            if move_str == last_move_str:
                count += 1
        
        # only trigger if same move made 10+ times in last 30 moves
        if count >= 10:
            return True
    
    # check for state oscillation (last 4 moves repeat 3+ times)
    if len(move_history) >= 24:
        pattern = move_history[-4:]
        pattern_str = [f"{m.get('type')}_{m.get('from')}_{m.get('to')}" for m in pattern]
        
        # check if this 4-move pattern has repeated at least 3 times
        repeat_count = 0
        for i in range(len(move_history) - 4, -4, -4):
            if i < 0:
                break
            check_pattern = move_history[i:i+4]
            check_pattern_str = [f"{m.get('type')}_{m.get('from')}_{m.get('to')}" for m in check_pattern]
            if check_pattern_str == pattern_str:
                repeat_count += 1
            else:
                break
        
        if repeat_count >= 3:
            return True
    
    return False


def get_best_move_tree_object(game, depth=6, recent_moves=None, force_draw=False):
    """get the actual Move object from tree algorithm"""
    from game_logic.best_move_tree import search_best_move, get_legal_moves
    from game_logic.move_utils import Move
    
    # if forced draw and stock has cards, draw immediately
    if force_draw and game.stock.size() > 0:
        return Move("draw_stock", {})
    
    score, move = search_best_move(game, depth, recent_moves=recent_moves)
    
    # if no good move found and we have stock, force draw
    if (not move or score < 0) and game.stock.size() > 0:
        return Move("draw_stock", {})
    
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
    game_state = "playing"
    move_history = []
    moves_without_foundation_progress = 0
    last_foundation_count = 0
    auto_playing = False
    auto_play_delay = 0
    

    running = True
    while running:
        if game_state == "won":
            restart_button_rect = pygame.Rect(WINDOW_W//2 - 75, WINDOW_H//2 + 20, 150, 40)
            mouse_pos = pygame.mouse.get_pos()
            restart_hover = restart_button_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button_rect.collidepoint(event.pos):
                        game = SolitaireGame()
                        selected = None
                        game_state = "playing"
                        move_history = []
                        moves_without_foundation_progress = 0
                        last_foundation_count = 0
                        auto_playing = False
                        button_message = None
            
            screen.fill(BACKGROUND_COLOR)
            overlay = pygame.Surface((WINDOW_W, WINDOW_H))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            win_text = font.render("YOU WIN!", True, (255, 215, 0))
            win_rect = win_text.get_rect(center=(WINDOW_W//2, WINDOW_H//2 - 30))
            screen.blit(win_text, win_rect)
            
            draw_button(screen, restart_button_rect, "Restart", font_small, restart_hover)
            
            pygame.display.flip()
            clock.tick(60)
            continue
        
        if game_state == "lost":
            restart_button_rect = pygame.Rect(WINDOW_W//2 - 75, WINDOW_H//2 + 20, 150, 40)
            mouse_pos = pygame.mouse.get_pos()
            restart_hover = restart_button_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button_rect.collidepoint(event.pos):
                        game = SolitaireGame()
                        selected = None
                        game_state = "playing"
                        move_history = []
                        moves_without_foundation_progress = 0
                        last_foundation_count = 0
                        auto_playing = False
                        button_message = None
            
            screen.fill(BACKGROUND_COLOR)
            overlay = pygame.Surface((WINDOW_W, WINDOW_H))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            lose_text = font.render("GAME STUCK - NO VALID MOVES", True, (255, 60, 60))
            lose_rect = lose_text.get_rect(center=(WINDOW_W//2, WINDOW_H//2 - 30))
            screen.blit(lose_text, lose_rect)
            
            draw_button(screen, restart_button_rect, "Restart", font_small, restart_hover)
            
            pygame.display.flip()
            clock.tick(60)
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                area, idx, card_idx = hit_test(layout, pos, game.Board)

                # handle hint button
                if layout.get("button") and layout["button"].collidepoint(pos):
                    best_move_tree = find_best_move(game)
                    best_move_graph = find_best_move_graph(game)
                    button_message = {
                        "graph_message": f"Best move from graph: {best_move_graph}",
                        "tree_message": f"Best move from tree: {best_move_tree}",
                    }
                    continue

                # handle auto-play tree button
                if layout.get("auto_tree_button") and layout["auto_tree_button"].collidepoint(pos):
                    move = get_best_move_tree_object(game, recent_moves=move_history)
                    if move:
                        apply_move_to_game(game, move)
                        
                        # track move for cycle detection
                        move_info = {
                            "type": move.move_type,
                            "from": move.details.get("from"),
                            "to": move.details.get("to")
                        }
                        move_history.append(move_info)
                        if len(move_history) > 30:
                            move_history.pop(0)
                        
                        current_foundation_count = sum(len(game.foundations[s].cards) for s in ["H", "D", "C", "S"])
                        if current_foundation_count > last_foundation_count:
                            moves_without_foundation_progress = 0
                            last_foundation_count = current_foundation_count
                        else:
                            moves_without_foundation_progress += 1
                        
                        if game.is_won():
                            game_state = "won"
                        elif detect_move_cycle(move_history, threshold=8):
                            game_state = "lost"
                        elif moves_without_foundation_progress > 120:
                            game_state = "lost"
                    continue

                # handle auto-play graph button
                if layout.get("auto_graph_button") and layout["auto_graph_button"].collidepoint(pos):
                    move = get_best_move_graph_object(game)
                    if move:
                        apply_move_to_game(game, move)
                        
                        # track move for cycle detection
                        move_info = {
                            "type": move.move_type,
                            "from": move.details.get("from"),
                            "to": move.details.get("to")
                        }
                        move_history.append(move_info)
                        if len(move_history) > 30:
                            move_history.pop(0)
                        
                        current_foundation_count = sum(len(game.foundations[s].cards) for s in ["H", "D", "C", "S"])
                        if current_foundation_count > last_foundation_count:
                            moves_without_foundation_progress = 0
                            last_foundation_count = current_foundation_count
                        else:
                            moves_without_foundation_progress += 1
                        
                        if game.is_won():
                            game_state = "won"
                        elif detect_move_cycle(move_history, threshold=8):
                            game_state = "lost"
                        elif moves_without_foundation_progress > 120:
                            game_state = "lost"
                    continue
                
                # handle auto-complete button
                if layout.get("auto_complete_button") and layout["auto_complete_button"].collidepoint(pos):
                    auto_playing = not auto_playing
                    continue

                if area == "stock":
                    drawn = game.stock.draw()
                    if drawn:
                        drawn.revealed = True
                        game.waste.add(drawn)
                    else:
                        if game.waste.size() > 0:
                            game.stock.recycle_from(game.waste)
                    selected = None
                    continue

                if selected:
                    moved = attempt_move(game, selected, (area, idx))
                    if moved:
                        # track move for cycle detection
                        move_info = {
                            "type": f"{selected.get('type')}_to_{area}",
                            "from": selected.get("index"),
                            "to": idx
                        }
                        move_history.append(move_info)
                        if len(move_history) > 30:
                            move_history.pop(0)
                        
                        selected = None
                        
                        current_foundation_count = sum(len(game.foundations[s].cards) for s in ["H", "D", "C", "S"])
                        if current_foundation_count > last_foundation_count:
                            moves_without_foundation_progress = 0
                            last_foundation_count = current_foundation_count
                        else:
                            moves_without_foundation_progress += 1
                        
                        if game.is_won():
                            game_state = "won"
                        elif detect_move_cycle(move_history, threshold=8):
                            game_state = "lost"
                        elif moves_without_foundation_progress > 120:
                            game_state = "lost"
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

        # auto-play logic
        if auto_playing and auto_play_delay <= 0:
            # use simple greedy AI instead of tree search
            from game_logic.greedy_ai import get_greedy_move
            move = get_greedy_move(game)
            if move:
                apply_move_to_game(game, move)
                
                # track move for cycle detection
                move_info = {
                    "type": move.move_type,
                    "from": move.details.get("from"),
                    "to": move.details.get("to")
                }
                move_history.append(move_info)
                if len(move_history) > 50:
                    move_history.pop(0)
                
                current_foundation_count = sum(len(game.foundations[s].cards) for s in ["H", "D", "C", "S"])
                if current_foundation_count > last_foundation_count:
                    moves_without_foundation_progress = 0
                    last_foundation_count = current_foundation_count
                else:
                    moves_without_foundation_progress += 1
                
                if game.is_won():
                    game_state = "won"
                    auto_playing = False
                elif detect_move_cycle(move_history, threshold=8):
                    game_state = "lost"
                    auto_playing = False
                elif moves_without_foundation_progress > 120:
                    game_state = "lost"
                    auto_playing = False
                auto_play_delay = 5
            else:
                # no move found, but check if we can still draw from stock
                if game.stock.size() > 0 or game.waste.size() > 0:
                    auto_play_delay = 5
                else:
                    game_state = "lost"
                    auto_playing = False
        
        if auto_play_delay > 0:
            auto_play_delay -= 1
        
        mouse_pos = pygame.mouse.get_pos()
        button_hover = layout.get("button") and layout["button"].collidepoint(mouse_pos)
        auto_tree_hover = layout.get("auto_tree_button") and layout["auto_tree_button"].collidepoint(mouse_pos)
        auto_graph_hover = layout.get("auto_graph_button") and layout["auto_graph_button"].collidepoint(mouse_pos)
        auto_complete_hover = layout.get("auto_complete_button") and layout["auto_complete_button"].collidepoint(mouse_pos)

        draw_stock(screen, game.stock, layout["stock"], font_small, selected)
        draw_waste(screen, game.waste, layout["waste"], font, font_small, selected)
        draw_foundations(screen, game.foundations, layout["foundations"], font, font_small, selected)
        draw_Board(screen, game.Board, layout["Board"], font, font_small, selected)
        
        # draw buttons
        if layout.get("auto_tree_button"):
            draw_button(screen, layout["auto_tree_button"], "Auto Tree", font_small, bool(auto_tree_hover))
        if layout.get("auto_graph_button"):
            draw_button(screen, layout["auto_graph_button"], "Auto Graph", font_small, bool(auto_graph_hover))
        if layout.get("auto_complete_button"):
            button_label = "Stop Auto" if auto_playing else "Auto Play"
            draw_button(screen, layout["auto_complete_button"], button_label, font_small, bool(auto_complete_hover))
        if layout.get("button"):
            draw_button(screen, layout["button"], "Get Hint", font_small, bool(button_hover))

        if button_message:
            draw_text(screen, button_message["graph_message"], (MARGIN, WINDOW_H - MARGIN - MARGIN - 20 - 22), font_small, (255, 255, 255))
            draw_text(screen, button_message["tree_message"], (MARGIN, WINDOW_H - MARGIN - 20 - 22), font_small, (255, 255, 255))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)
