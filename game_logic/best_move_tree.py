"""
Tree-based AI for Solitaire using Depth-First Search.

Implements a recursive DFS algorithm with memoization to find optimal moves.
Explores the game tree up to a specified depth, scoring each state and
selecting moves that lead to higher scores. Uses state serialization to
avoid revisiting previously explored positions.

Algorithm: DFS with memoization
Time Complexity: O(b^d) where b=branching factor, d=depth
Space Complexity: O(d) for recursion + O(n) for memo
"""

import time
import random
from .move_utils import Move, serialize_state, score_state, apply_move

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
def search_best_move(game, depth=6, visited=None, alpha=-float("inf"), recent_moves=None):
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

    # HARD FILTER: block recently repeated moves at root level
    if recent_moves and depth == 6:
        filtered_moves = []
        blocked_moves = []
        
        for move in legal_moves:
            move_str = f"{move.move_type}_{move.details.get('from')}_{move.details.get('to')}"
            
            # NEVER block foundation moves - they're always good
            if "foundation" in move.move_type:
                filtered_moves.append(move)
                continue
            
            # count how many times this exact move appears in recent history
            recent_count = 0
            for i, recent in enumerate(recent_moves[-10:]):
                recent_str = f"{recent.get('type')}_{recent.get('from')}_{recent.get('to')}"
                if recent_str == move_str:
                    recent_count += 1
            
            # check if this move was made in last 3 moves (immediate repeat)
            immediate_repeat = False
            if len(recent_moves) >= 3:
                last_three = recent_moves[-3:]
                for recent in last_three:
                    recent_str = f"{recent.get('type')}_{recent.get('from')}_{recent.get('to')}"
                    if recent_str == move_str:
                        immediate_repeat = True
                        break
            
            # block move if made 3+ times recently OR repeated in last 3 moves
            if recent_count >= 3 or immediate_repeat:
                blocked_moves.append(move)
            else:
                filtered_moves.append(move)
        
        # use filtered moves if we have any, otherwise fall back to all moves
        if filtered_moves:
            legal_moves = filtered_moves
        else:
            # all moves are blocked, so allow them but we're probably stuck
            legal_moves = legal_moves

    # ALWAYS PREFER FOUNDATION MOVES - they're always correct
    foundation_moves = [m for m in legal_moves if "foundation" in m.move_type]
    if foundation_moves and depth == 6:
        # at root level, if we can move to foundation, DO IT
        return 1000.0, random.choice(foundation_moves)
    
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
    best_moves = []

    for move in legal_moves:
        new_game = apply_move(game, move)
        # share visited set within the same branch to prevent cycles
        score, _ = search_best_move(new_game, depth - 1, visited, alpha=alpha, recent_moves=None)
        
        # MASSIVE bonus for foundation moves
        if "foundation" in move.move_type:
            score += 1000.0
        
        # add random noise to break ties and ensure variety
        score += random.uniform(0, 1.0)
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif abs(score - best_score) < 5.0:  # consider scores within 5.0 as ties
            best_moves.append(move)
        # update alpha to track best score found so far
        if best_score > alpha:
            alpha = best_score
    
    # if multiple moves have the same score, prefer foundation moves
    if len(best_moves) > 1:
        foundation_moves_best = [m for m in best_moves if "foundation" in m.move_type]
        if foundation_moves_best:
            best_move = random.choice(foundation_moves_best)
        else:
            # avoid drawing from stock if other options exist
            non_draw_moves = [m for m in best_moves if m.move_type not in ["draw_stock", "reset_stock"]]
            if non_draw_moves:
                best_move = random.choice(non_draw_moves)
            else:
                best_move = random.choice(best_moves)
    else:
        best_move = best_moves[0] if best_moves else None

    visited.remove(state_key)  # backtrack: allow revisiting this state in other branches
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
def find_best_move(game, depth=6, recent_moves=None):
    start_time = time.time()
    score, move = search_best_move(game, depth, recent_moves=recent_moves)
    elapsed_ms = (time.time() - start_time) * 1000
    move_str = describe_move(move)
    print(f"Tree search best move: {move_str} | Computed in {elapsed_ms:.0f}ms")
    return move_str
