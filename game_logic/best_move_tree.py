import copy
import time

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
    Board_ser = tuple(tuple((c.rank, c.suit, c.revealed) for c in pile.cards) for pile in game.Board)
    foundation_ser = tuple(tuple((c.rank, c.suit) for c in game.foundations[suit].cards) for suit in ["H", "D", "C", "S"])
    stock_ser = tuple((c.rank, c.suit) for c in game.stock.cards)
    waste_ser = tuple((c.rank, c.suit) for c in game.waste.cards)
    return (Board_ser, foundation_ser, stock_ser, waste_ser)

# ---------------- SCORING ----------------
def score_state(game):
    score = 0
    for suit in ["H", "D", "C", "S"]:
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
        card = g.Board[col].pop()
        g.foundations[card.suit].add(card)
        if g.Board[col].size() > 0:
            g.Board[col].cards[-1].revealed = True
        return g
    if m.move_type == "Board_to_Board":
        src = m.details["from"]
        dst = m.details["to"]
        card = g.Board[src].pop()
        g.Board[dst].add(card)
        if g.Board[src].size() > 0:
            g.Board[src].cards[-1].revealed = True
        return g
    return g

# ---------------- LEGAL MOVES ----------------
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
        card = pile.peek()
        if game.foundations[card.suit].can_add(card):
            moves.append(Move("Board_to_foundation", {"from": i, "card": card}))
        for j, dst in enumerate(game.Board):
            if i == j or dst.size() == 0:
                continue
            if dst.can_add(card):
                moves.append(Move("Board_to_Board", {"from": i, "to": j, "card": card}))
    if game.stock.size() > 0:
        moves.append(Move("draw_stock", {}))
    elif game.waste.size() > 0:
        moves.append(Move("reset_stock", {}))
    return moves

# ---------------- SEARCH WITH PRUNING ----------------
def search_best_move(game, depth=4, memo=None, alpha=-10**9):
    if memo is None:
        memo = {}

    state_key = serialize_state(game)
    if state_key in memo:
        return memo[state_key]

    if depth == 0:
        score = score_state(game)
        memo[state_key] = (score, None)
        return score, None

    legal = get_legal_moves(game)
    if not legal:
        score = score_state(game)
        memo[state_key] = (score, None)
        return score, None

    # MOVE ORDERING
    def move_priority(m):
        if m.move_type in ["waste_to_foundation", "Board_to_foundation"]:
            return 3
        elif m.move_type in ["Board_to_Board", "waste_to_Board"]:
            return 2
        elif m.move_type in ["draw_stock"]:
            return 1
        else:
            return 0

    legal.sort(key=move_priority, reverse=True)

    best_score = -10**9
    best_move = None

    for move in legal:
        new_game = apply_move(game, move)
        score, _ = search_best_move(new_game, depth - 1, memo, alpha=best_score)

        if score > best_score:
            best_score = score
            best_move = move

        # EARLY PRUNING
        if best_score >= alpha:
            break

    memo[state_key] = (best_score, best_move)
    return best_score, best_move

# ---------------- FIND BEST MOVE ----------------
def find_best_move(game, depth=4):
    start_time = time.time()
    _, move = search_best_move(game, depth)
    elapsed_ms = (time.time() - start_time) * 1000

    if not move:
        print("No moves available")
        return None

    if move.move_type == "Board_to_Board":
        best_move = f"Move the {move.details['card']} from deck {move.details['from']} to {move.details['to']}"
    elif move.move_type == "Board_to_foundation":
        best_move = f"Move the {move.details['card']} in deck {move.details['from']} to the Foundation"
    elif move.move_type == "waste_to_Board":
        best_move = f"Move the {move.details['card']} from the waste to the deck {move.details['column']}"
    elif move.move_type == "waste_to_foundation":
        best_move = f"Move the {move.details['card']} from the waste to the foundation"
    elif move.move_type == "draw_stock":
        best_move = "Draw a card from the stock"
    elif move.move_type == "reset_stock":
        best_move = "Reset the stock"
    else:
        best_move = f"Best move: {move}"

    print(f"Best move computed in {elapsed_ms:.0f}ms: {best_move}")
    return best_move
