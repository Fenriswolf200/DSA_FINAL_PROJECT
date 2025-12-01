import copy
import time

# ---------------- MOVE CLASS ----------------
class Move:
    def __init__(self, move_type: str, details: dict):
        self.move_type = move_type
        self.details = details

    def __repr__(self):
        card = self.details.get("card")
        card_str = repr(card) if card else None
        details_copy = self.details.copy()
        if card:
            details_copy["card"] = card_str
        return f"Move({self.move_type}, {details_copy})"

# ---------------- STATE SERIALIZATION ----------------
def serialize_state(game):
    """
    Canonical serialization: sort columns by top card to avoid swaps creating new states
    """
    board_ser = []
    for pile in game.Board:
        pile_ser = tuple((c.rank, c.suit, c.revealed) for c in pile.cards)
        board_ser.append(pile_ser)
    # Sort columns by top card (empty piles first) for canonical order
    board_ser_sorted = tuple(sorted(board_ser, key=lambda x: x[-1] if x else (0, 'X', False)))
    foundation_ser = tuple(tuple((c.rank, c.suit) for c in game.foundations[suit].cards) for suit in ["H","D","C","S"])
    stock_ser = tuple((c.rank, c.suit) for c in game.stock.cards)
    waste_ser = tuple((c.rank, c.suit) for c in game.waste.cards)
    return (board_ser_sorted, foundation_ser, stock_ser, waste_ser)

# ---------------- SCORING ----------------
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

# ---------------- APPLY MOVE ----------------
def apply_move(game, move):
    g = copy.deepcopy(game)
    m = move
    if m.move_type == "draw_stock":
        drawn = g.stock.draw()
        if drawn:
            drawn.revealed = True
            g.waste.add(drawn)
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

# ---------------- LEGAL MOVES ----------------
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
            # can move sequence to another Board pile
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

# ---------------- TREE SEARCH WITH CYCLE DETECTION ----------------
def search_best_move(game, depth=4, visited=None, alpha=-float("inf")):
    if visited is None:
        visited = set()
    state_key = serialize_state(game)
    if state_key in visited:
        return -float("inf"), None
    visited.add(state_key)

    if depth == 0:
        return score_state(game), None

    legal_moves = get_legal_moves(game)
    if not legal_moves:
        return score_state(game), None

    # Move ordering: foundation moves first
    def move_priority(m):
        if m.move_type in ["waste_to_foundation", "Board_to_foundation"]:
            return 3
        elif m.move_type in ["Board_to_Board", "waste_to_Board"]:
            return 2
        elif m.move_type == "draw_stock":
            return 1
        else:
            return 0
    legal_moves.sort(key=move_priority, reverse=True)

    best_score = -float("inf")
    best_move = None

    for move in legal_moves:
        new_game = apply_move(game, move)
        score, _ = search_best_move(new_game, depth - 1, visited.copy(), alpha=alpha)
        if score > best_score:
            best_score = score
            best_move = move
        # update alpha to track best score found so far
        # (no pruning in single-player - we explore all moves to find the best)
        if best_score > alpha:
            alpha = best_score

    return best_score, best_move

# ---------------- HUMAN-READABLE MOVE ----------------
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

# ---------------- FIND BEST MOVE ----------------
def find_best_move(game, depth=4):
    start_time = time.time()
    score, move = search_best_move(game, depth)
    elapsed_ms = (time.time() - start_time) * 1000
    move_str = describe_move(move)
    print(f"Tree search best move: {move_str} | Computed in {elapsed_ms:.0f}ms")
    return move_str
