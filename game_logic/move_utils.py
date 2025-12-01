"""
Shared utilities for AI move generation in Solitaire.

Provides common functionality used by both tree-based and graph-based search:
- Move representation and state management
- Game state serialization for memoization
- Heuristic scoring for move prioritization
- Move application with deep copying
"""

import copy
from config import FOUNDATION_CARD_POINTS, REVEALED_CARD_POINTS, EMPTY_PILE_POINTS

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

def serialize_state(game):
    board_ser = []
    for pile in game.Board:
        pile_ser = tuple((c.rank, c.suit, c.revealed) for c in pile.cards)
        board_ser.append(pile_ser)
    board_ser_sorted = tuple(sorted(board_ser, key=lambda x: x[-1] if x else (0, 'X', False)))
    foundation_ser = tuple(tuple((c.rank, c.suit) for c in game.foundations[suit].cards) for suit in ["H","D","C","S"])
    stock_ser = tuple((c.rank, c.suit) for c in game.stock.cards)
    waste_ser = tuple((c.rank, c.suit) for c in game.waste.cards)
    return (board_ser_sorted, foundation_ser, stock_ser, waste_ser)

def score_state(game):
    score = 0
    
    # cards in foundation (MASSIVELY highest priority)
    total_foundation = 0
    for suit in ["H","D","C","S"]:
        foundation_size = len(game.foundations[suit].cards)
        total_foundation += foundation_size
        # exponential reward for foundation cards
        score += FOUNDATION_CARD_POINTS * foundation_size * 3
        score += foundation_size * foundation_size * 2
    
    # huge bonus for getting closer to winning
    if total_foundation > 40:
        score += 500
    elif total_foundation > 30:
        score += 200
    elif total_foundation > 20:
        score += 100
    
    # revealed cards (minor)
    for pile in game.Board:
        for card in pile.cards:
            if card.revealed:
                score += REVEALED_CARD_POINTS * 0.5
    
    # empty piles (but only if we have kings to put there)
    empty_count = 0
    has_king_to_move = False
    for pile in game.Board:
        if pile.size() == 0:
            empty_count += 1
        elif pile.size() > 0 and pile.cards[0].rank == 13 and len(pile.cards) > 1:
            has_king_to_move = True
    
    if has_king_to_move:
        score += EMPTY_PILE_POINTS * empty_count * 3
    else:
        score += EMPTY_PILE_POINTS * empty_count
    
    # bonus for longer revealed sequences (helps build plays)
    for pile in game.Board:
        sequence_length = 0
        for i in range(len(pile.cards)):
            if pile.cards[i].revealed:
                sequence_length += 1
        score += sequence_length * 0.3
    
    # penalty for having many cards in stock/waste (want to clear them)
    score -= game.stock.size() * 0.5
    score -= game.waste.size() * 1.0
    
    return score

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
        sequence = g.Board[src].cards[start_idx:]
        del g.Board[src].cards[start_idx:]
        for c in sequence:
            c.revealed = True
            g.Board[dst].add(c)
        if g.Board[src].size() > 0:
            g.Board[src].cards[-1].revealed = True
        return g
    return g

