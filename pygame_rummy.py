import pygame
import sys
from game_logic.cards import Hand
from game_logic.player import Player
from game_logic.spaces import CardSpace
from main import create_deck, deal_cards
from ui.ui_components import Button, CardVisual, CARD_WIDTH, CARD_HEIGHT, CARD_CORNER_RADIUS, CARD_WHITE, TEXT_COLOR

pygame.init()

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
FPS = 60
CARD_SPACING = 15

BACKGROUND_COLOR = (34, 139, 34)
BOARD_AREA_COLOR = (25, 100, 25)

FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)


class RummyGameVisual:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Rummy Card Game - 2 Players")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.current_player_idx = 0
        self.selected_cards = []
        self.message = ""
        self.message_timer = 0
        
        self.deck = create_deck()
        self.board = CardSpace()
        self.players = [Player(1), Player(2)]
        deal_cards(self.players, self.deck)
        
        for player in self.players:
            player.hand.sort_hand()
        
        button_x_left = WINDOW_WIDTH - 330
        button_x_right = WINDOW_WIDTH - 160
        button_y_top = 495
        button_y_bottom = 555
        
        self.done_button = Button(button_x_left, button_y_top, 150, 50, "DONE")
        self.sort_button = Button(button_x_right, button_y_top, 150, 50, "SORT")
        self.play_button = Button(button_x_left, button_y_bottom, 150, 50, "PLAY")
        self.draw_button = Button(button_x_right, button_y_bottom, 150, 50, "DRAW")
        
        self.show_message(f"Player 1's turn")
        
    def draw_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        board_rect = pygame.Rect(50, 50, WINDOW_WIDTH - 100, 430)
        pygame.draw.rect(self.screen, BOARD_AREA_COLOR, board_rect, border_radius=10)
        pygame.draw.rect(self.screen, TEXT_COLOR, board_rect, 2, border_radius=10)
        
        board_label = FONT_MEDIUM.render("BOARD", True, TEXT_COLOR)
        self.screen.blit(board_label, (60, 20))
        
        self.draw_board()
        self.draw_deck()
        self.draw_player_hand()
        
        self.draw_button.draw(self.screen)
        self.play_button.draw(self.screen)
        self.sort_button.draw(self.screen)
        self.done_button.draw(self.screen)
        
        player_text = FONT_MEDIUM.render(f"Player {self.current_player_idx + 1}'s Turn", True, TEXT_COLOR)
        self.screen.blit(player_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 30))
        
        cards_text = FONT_SMALL.render(f"Cards in hand: {len(self.players[self.current_player_idx].hand.hand)}", True, TEXT_COLOR)
        self.screen.blit(cards_text, (20, WINDOW_HEIGHT - 30))
        
        if self.message and self.message_timer > 0:
            msg_surface = FONT_MEDIUM.render(self.message, True, TEXT_COLOR)
            msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH//2, 500))
            bg_rect = msg_rect.inflate(40, 20)
            s = pygame.Surface((bg_rect.width, bg_rect.height))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            self.screen.blit(s, bg_rect)
            self.screen.blit(msg_surface, msg_rect)
            self.message_timer -= 1
    
    def draw_deck(self):
        deck_x, deck_y = WINDOW_WIDTH - 180, 70
        deck_label = FONT_SMALL.render("DECK", True, TEXT_COLOR)
        self.screen.blit(deck_label, (deck_x, deck_y - 20))
        
        for i in range(3):
            deck_rect = pygame.Rect(deck_x + i*2, deck_y + i*2, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, (0, 51, 102), deck_rect, border_radius=CARD_CORNER_RADIUS)
            pygame.draw.rect(self.screen, CARD_WHITE, deck_rect, 2, border_radius=CARD_CORNER_RADIUS)
    
    def draw_board(self):
        if len(self.board.card_space) == 0:
            no_cards_text = FONT_SMALL.render("No cards played yet", True, TEXT_COLOR)
            self.screen.blit(no_cards_text, (WINDOW_WIDTH//2 - 80, 220))
            return
        
        # 3-column grid layout: Sets arranged vertically in 3 columns
        start_x = 60
        start_y = 70
        column_width = 400
        row_height = 125
        max_cards_per_set = 8
        
        for hand_idx, hand in enumerate(self.board.card_space):
            # Calculate position: column 0 has sets 0,1,2; column 1 has sets 3,4,5; etc
            column = hand_idx // 3
            row = hand_idx % 3
            
            set_x = start_x + (column * column_width)
            set_y = start_y + (row * row_height)
            
            # Draw set label
            hand_label = FONT_SMALL.render(f"Set {hand_idx + 1}:", True, TEXT_COLOR)
            self.screen.blit(hand_label, (set_x, set_y))
            
            # Draw cards in this set
            card_start_x = set_x + 60
            for card_idx, card in enumerate(hand.hand[:max_cards_per_set]):
                card_x = card_start_x + (card_idx * 38)
                card_y = set_y
                CardVisual(card, card_x, card_y).draw(self.screen)
    
    def draw_player_hand(self):
        current_player = self.players[self.current_player_idx]
        hand = current_player.hand.hand
        
        hand_label = FONT_MEDIUM.render("YOUR HAND", True, TEXT_COLOR)
        self.screen.blit(hand_label, (20, 560))
        
        if len(hand) == 0:
            return
        
        total_width = len(hand) * (CARD_WIDTH + CARD_SPACING)
        start_x = (WINDOW_WIDTH - total_width) // 2
        start_y = 620
        
        for idx, card in enumerate(hand):
            x = start_x + idx * (CARD_WIDTH + CARD_SPACING)
            y = start_y - 20 if idx in self.selected_cards else start_y
            is_selected = idx in self.selected_cards
            CardVisual(card, x, y, is_selected).draw(self.screen)
    
    def show_message(self, message, duration=120):
        self.message = message
        self.message_timer = duration
    
    def next_turn(self):
        self.current_player_idx = 1 - self.current_player_idx
        self.selected_cards = []
        self.show_message(f"Player {self.current_player_idx + 1}'s turn")
    
    def handle_card_click(self, pos):
        current_player = self.players[self.current_player_idx]
        hand = current_player.hand.hand
        total_width = len(hand) * (CARD_WIDTH + CARD_SPACING)
        start_x = (WINDOW_WIDTH - total_width) // 2
        start_y = 620
        
        for idx in range(len(hand)):
            x = start_x + idx * (CARD_WIDTH + CARD_SPACING)
            y = start_y - 20 if idx in self.selected_cards else start_y
            card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            if card_rect.collidepoint(pos):
                if idx in self.selected_cards:
                    self.selected_cards.remove(idx)
                else:
                    self.selected_cards.append(idx)
                break
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for button in [self.draw_button, self.play_button, self.sort_button, self.done_button]:
            button.is_hovered = button.rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if self.game_over:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.running = False
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_player = self.players[self.current_player_idx]
                
                if self.draw_button.is_clicked(event.pos):
                    card = self.deck.draw_card()
                    if card:
                        current_player.add_to_hand(card)
                        self.show_message("Drew a card")
                        self.next_turn()
                    else:
                        self.show_message("Deck is empty!")
                
                elif self.sort_button.is_clicked(event.pos):
                    current_player.hand.sort_hand()
                    self.selected_cards = []
                    self.show_message("Hand sorted")
                
                elif self.play_button.is_clicked(event.pos):
                    if len(self.selected_cards) == 0:
                        self.show_message("Select cards first!")
                    else:
                        new_hand = Hand()
                        for idx in sorted(self.selected_cards, reverse=True):
                            card = current_player.remove_from_hand(idx)
                            new_hand.add_card(card)
                        self.board.add_new_hand(new_hand)
                        self.selected_cards = []
                        self.show_message("Cards played!")
                
                elif self.done_button.is_clicked(event.pos):
                    if len(current_player.hand.hand) == 0:
                        self.show_message(f"Player {self.current_player_idx + 1} wins!")
                        self.game_over = True
                    else:
                        self.next_turn()
                
                else:
                    self.handle_card_click(event.pos)
    
    def draw(self):
        self.draw_game()
        
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = FONT_LARGE.render("GAME OVER!", True, TEXT_COLOR)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            winner_text = FONT_MEDIUM.render(f"Player {self.current_player_idx + 1} wins!", True, TEXT_COLOR)
            winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
            self.screen.blit(winner_text, winner_rect)
            
            continue_text = FONT_SMALL.render("Press any key to exit", True, TEXT_COLOR)
            continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 70))
            self.screen.blit(continue_text, continue_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


def main():
    game = RummyGameVisual()
    game.run()


if __name__ == "__main__":
    main()

