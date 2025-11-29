import copy
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
    tableau_ser = tuple(tuple((c.rank, c.suit, c.revealed) for c in pile.cards) for pile in game.tableau)
    foundation_ser = tuple(tuple((c.rank, c.suit) for c in game.foundations[suit].cards) for suit in ["H", "D", "C", "S"])
    stock_ser = tuple((c.rank, c.suit) for c in game.stock.cards)
    waste_ser = tuple((c.rank, c.suit) for c in game.waste.cards)
    return (tableau_ser, foundation_ser, stock_ser, waste_ser)

def score_state(game):
    score = 0
    for suit in ["H", "D", "C", "S"]:
        score += 10 * len(game.foundations[suit].cards)
    for pile in game.tableau:
        for card in pile.cards:
            if card.revealed:
                score += 2
    for pile in game.tableau:
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
    if m.move_type == "waste_to_tableau":
        card = g.waste.pop()
        g.tableau[m.details["column"]].add(card)
        return g
    if m.move_type == "tableau_to_foundation":
        col = m.details["from"]
        card = g.tableau[col].pop()
        g.foundations[card.suit].add(card)
        if g.tableau[col].size() > 0:
            g.tableau[col].cards[-1].revealed = True
        return g
    if m.move_type == "tableau_to_tableau":
        src = m.details["from"]
        dst = m.details["to"]
        card = g.tableau[src].pop()
        g.tableau[dst].add(card)
        if g.tableau[src].size() > 0:
            g.tableau[src].cards[-1].revealed = True
        return g
    return g

def get_legal_moves(game):
    moves = []
    if game.waste.size() > 0:
        card = game.waste.peek()
        if game.foundations[card.suit].can_add(card):
            moves.append(Move("waste_to_foundation", {"card": card}))
        for i, pile in enumerate(game.tableau):
            if pile.can_add(card):
                moves.append(Move("waste_to_tableau", {"column": i, "card": card}))
    for i, pile in enumerate(game.tableau):
        if pile.size() == 0:
            continue
        card = pile.peek()
        if game.foundations[card.suit].can_add(card):
            moves.append(Move("tableau_to_foundation", {"from": i, "card": card}))
        for j, dst in enumerate(game.tableau):
            if i == j or dst.size() == 0:
                continue
            if dst.can_add(card):
                moves.append(Move("tableau_to_tableau", {"from": i, "to": j, "card": card}))
    if game.stock.size() > 0:
        moves.append(Move("draw_stock", {}))
    elif game.waste.size() > 0:
        moves.append(Move("reset_stock", {}))
    return moves

def search_best_move(game, depth=4):
    state_key = serialize_state(game)
    if state_key in search_best_move.memo:
        return search_best_move.memo[state_key]
    if depth == 0:
        return (score_state(game), None)
    legal = get_legal_moves(game)
    if not legal:
        return (score_state(game), None)
    best_score = -10**9
    best_move = None
    for move in legal:
        new_game = apply_move(game, move)
        score, _ = search_best_move(new_game, depth - 1)
        if score > best_score:
            best_score = score
            best_move = move
    search_best_move.memo[state_key] = (best_score, best_move)
    return (best_score, best_move)

search_best_move.memo = {}

def find_best_move(game, depth=4):
    start_time = time.time()
    _, move = search_best_move(game, depth)
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"Best move using tree: {move} | Computed in {elapsed_ms:.0f}ms")
    return move
