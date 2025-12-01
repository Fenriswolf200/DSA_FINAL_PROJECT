import copy
from collections import deque
import time

class Move:
    def __init__(self, move_type, details):
        self.move_type = move_type
        self.details = details
    def __repr__(self):
        card = self.details.get("card")
        card_str = repr(card) if card else None
        details_copy = self.details.copy()
        if card:
            details_copy["card"] = card_str
        return f"Move({self.move_type}, {details_copy})"

def serialize_state(game):
    Board_ser = tuple(tuple((c.rank, c.suit, c.revealed) for c in pile.cards) for pile in game.Board)
    foundation_ser = tuple(tuple((c.rank, c.suit) for c in game.foundations[suit].cards) for suit in ["H","D","C","S"])
    stock_ser = tuple((c.rank, c.suit) for c in game.stock.cards)
    waste_ser = tuple((c.rank, c.suit) for c in game.waste.cards)
    return (Board_ser, foundation_ser, stock_ser, waste_ser)

def score_state(game):
    score = 0
    for suit in ["H","D","C","S"]:
        score += 10 * len(game.foundations[suit].cards)
    for pile in game.Board:
        for card in pile.cards:
            if card.revealed:
                score += 2
    for pile in game.Board:
        if pile.size() == 0:
            score += 3
    return score

def apply_move(game, move):
    g = copy.deepcopy(game)
    m = move
    if m.move_type == "draw_stock":
        g.waste.add(g.stock.draw())
        return g
    if m.move_type == "reset_stock":
        g.stock.recycle_from(g.waste)
        return g
    if m.move_type == "waste_to_foundation":
        card = g.waste.pop()
        g.foundations[card.suit].add(card)
        return g
    if m.move_type == "waste_to_Board":
        card = g.waste.pop()
        g.Board[m.details["column"]].add(card)
        return g
    if m.move_type == "Board_to_foundation":
        col = m.details["from"]
        start_idx = m.details.get("start_idx", len(g.Board[col].cards) - 1)
        # only top card can go to foundation
        if start_idx == len(g.Board[col].cards) - 1:
            card = g.Board[col].pop()
            g.foundations[card.suit].add(card)
            if g.Board[col].size() > 0:
                g.Board[col].cards[-1].revealed = True
        return g
    if m.move_type == "Board_to_Board":
        src = m.details["from"]
        dst = m.details["to"]
        start_idx = m.details.get("start_idx", len(g.Board[src].cards) - 1)
        # move sequence from start_idx to end
        sequence = g.Board[src].cards[start_idx:]
        del g.Board[src].cards[start_idx:]
        for c in sequence:
            c.revealed = True
            g.Board[dst].add(c)
        if g.Board[src].size() > 0:
            g.Board[src].cards[-1].revealed = True
        return g
    return g

def _is_valid_sequence(pile, start_idx):
    """check if cards from start_idx to end form a valid sequence"""
    if start_idx < 0 or start_idx >= len(pile.cards):
        return False
    # all cards in sequence must be revealed
    for i in range(start_idx, len(pile.cards)):
        if not pile.cards[i].revealed:
            return False
    # check ordering: descending rank, alternating colors
    for i in range(start_idx, len(pile.cards) - 1):
        a = pile.cards[i]
        b = pile.cards[i + 1]
        if a.rank != b.rank + 1:
            return False
        if a.is_red() == b.is_red():
            return False
    return True

def get_legal_moves(game):
    moves = []
    if game.waste.size() > 0:
        card = game.waste.peek()
        if game.foundations[card.suit].can_add(card):
            moves.append(Move("waste_to_foundation", {"card": card}))
        for i, pile in enumerate(game.Board):
            if pile.can_add(card):
                moves.append(Move("waste_to_Board", {"column": i, "card": card}))
    for i, pile in enumerate(game.Board):
        if pile.size() == 0:
            continue
        # find all valid sequences starting from each revealed card
        for start_idx in range(len(pile.cards)):
            if not pile.cards[start_idx].revealed:
                continue
            if not _is_valid_sequence(pile, start_idx):
                continue
            card = pile.cards[start_idx]
            # can move to foundation (only if it's the top card)
            if start_idx == len(pile.cards) - 1 and game.foundations[card.suit].can_add(card):
                moves.append(Move("Board_to_foundation", {"from": i, "card": card, "start_idx": start_idx}))
            # can move sequence to another Board pile (including empty piles)
            for j, dst in enumerate(game.Board):
                if i == j:
                    continue
                if dst.can_add(card):
                    moves.append(Move("Board_to_Board", {"from": i, "to": j, "card": card, "start_idx": start_idx}))
    if game.stock.size() > 0:
        moves.append(Move("draw_stock", {}))
    elif game.waste.size() > 0:
        moves.append(Move("reset_stock", {}))
    return moves

def describe_move(move):
    if not move:
        return "No move found"
    if move.move_type == "Board_to_Board":
        return f"Move {move.details['card']} from column {move.details['from']} to column {move.details['to']}"
    if move.move_type == "Board_to_foundation":
        return f"Move {move.details['card']} from column {move.details['from']} to the foundation"
    if move.move_type == "waste_to_Board":
        return f"Move {move.details['card']} from waste to column {move.details['column']}"
    if move.move_type == "waste_to_foundation":
        return f"Move {move.details['card']} from waste to the foundation"
    if move.move_type == "draw_stock":
        return "Draw a card from the stock"
    if move.move_type == "reset_stock":
        return "Reset the stock"
    return f"Move: {move}"



def find_best_move_graph(game, max_depth=4):
    start_time = time.time()
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
        legal_moves = get_legal_moves(current_game)
        for move in legal_moves:
            new_game = apply_move(current_game, move)
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
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"Best move using graph: {best_move} | Computed in {elapsed_ms:.0f}ms")

    move_text = describe_move(best_move)

    return move_text
