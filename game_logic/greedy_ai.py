"""
Simple greedy AI for Solitaire - makes obvious best moves without deep search.
This avoids getting stuck in cycles by always taking the best immediate action.
"""

from game_logic.move_utils import Move

def get_greedy_move(game):
    """
    Get the best move using simple greedy strategy:
    1. Always move to foundation if possible (HIGHEST priority)
    2. Reveal hidden cards (HIGH priority)
    3. Build sequences in tableau (MEDIUM priority)
    4. Draw from stock (LOW priority)
    """
    
    # PRIORITY 1: Move to foundation (ALWAYS do this first)
    # Check waste pile
    if game.waste.size() > 0:
        card = game.waste.peek()
        if game.foundations[card.suit].can_add(card):
            return Move("waste_to_foundation", {"card": card})
    
    # Check tableau piles (top cards only)
    for i, pile in enumerate(game.Board):
        if pile.size() > 0:
            top_card = pile.peek()
            if top_card.revealed and game.foundations[top_card.suit].can_add(top_card):
                return Move("Board_to_foundation", {"from": i, "card": top_card, "start_idx": len(pile.cards) - 1})
    
    # PRIORITY 2: Reveal hidden cards (very important for progress)
    # Move cards to empty piles to reveal underneath
    for i, pile in enumerate(game.Board):
        if pile.size() > 0 and len(pile.cards) > 1:
            # check if moving top card would reveal a hidden card
            for j in range(len(pile.cards) - 1, -1, -1):
                if not pile.cards[j].revealed:
                    # found a hidden card - try to move cards above it
                    if j < len(pile.cards) - 1:
                        card_to_move = pile.cards[j + 1]
                        if card_to_move.revealed:
                            # try to move this card somewhere to reveal the hidden one
                            for k, dst_pile in enumerate(game.Board):
                                if k != i and dst_pile.can_add(card_to_move):
                                    return Move("Board_to_Board", {
                                        "from": i, "to": k, "card": card_to_move, "start_idx": j + 1
                                    })
                    break
    
    # PRIORITY 3: Move from waste to tableau (better than just sitting in waste)
    if game.waste.size() > 0:
        card = game.waste.peek()
        for i, pile in enumerate(game.Board):
            if pile.can_add(card):
                return Move("waste_to_Board", {"column": i, "card": card})
    
    # PRIORITY 4: Build sequences in tableau (move kings to empty piles)
    for i, pile in enumerate(game.Board):
        if pile.size() == 0:
            # found empty pile - look for a king to move there
            for j, src_pile in enumerate(game.Board):
                if j != i and src_pile.size() > 0:
                    # find the first revealed king
                    for idx in range(len(src_pile.cards)):
                        card = src_pile.cards[idx]
                        if card.revealed and card.rank == 13 and idx > 0:
                            # found a king that's not at the bottom - move it
                            return Move("Board_to_Board", {
                                "from": j, "to": i, "card": card, "start_idx": idx
                            })
    
    # PRIORITY 5: Make any valid tableau move to try new configurations
    for i, src_pile in enumerate(game.Board):
        if src_pile.size() > 0:
            for start_idx in range(len(src_pile.cards) - 1, -1, -1):
                card = src_pile.cards[start_idx]
                if card.revealed:
                    for j, dst_pile in enumerate(game.Board):
                        if i != j and dst_pile.can_add(card):
                            return Move("Board_to_Board", {
                                "from": i, "to": j, "card": card, "start_idx": start_idx
                            })
    
    # PRIORITY 6: Draw from stock (last resort)
    if game.stock.size() > 0:
        return Move("draw_stock", {})
    
    # PRIORITY 7: Reset stock if needed
    if game.waste.size() > 0:
        return Move("reset_stock", {})
    
    # No moves available
    return None

