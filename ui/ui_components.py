import pygame

CARD_WIDTH = 70
CARD_HEIGHT = 100
CARD_CORNER_RADIUS = 5

CARD_WHITE = (255, 255, 255)
CARD_BORDER = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 149, 237)
RED_SUIT = (220, 20, 60)
BLACK_SUIT = (0, 0, 0)
SELECTED_COLOR = (255, 215, 0)


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.font = pygame.font.Font(None, 32)
        
    def draw(self, screen):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 2, border_radius=10)
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class CardVisual:
    def __init__(self, card, x, y, selected=False):
        self.card = card
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.is_selected = selected
        self.font_card = pygame.font.Font(None, 20)
        self.font_suit = pygame.font.Font(None, 32)
        
    def draw(self, screen):
        pygame.draw.rect(screen, CARD_WHITE, self.rect, border_radius=CARD_CORNER_RADIUS)
        border_color = SELECTED_COLOR if self.is_selected else CARD_BORDER
        border_width = 4 if self.is_selected else 2
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=CARD_CORNER_RADIUS)
        
        suit_color = RED_SUIT if self.card.suit in ['H', 'D'] else BLACK_SUIT
        suit_symbols = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}
        suit_symbol = suit_symbols.get(self.card.suit, self.card.suit)
        
        rank_text = self.font_card.render(str(self.card.rank), True, suit_color)
        suit_text = self.font_suit.render(suit_symbol, True, suit_color)
        
        screen.blit(rank_text, (self.rect.x + 5, self.rect.y + 5))
        suit_rect = suit_text.get_rect(center=self.rect.center)
        screen.blit(suit_text, suit_rect)
        screen.blit(rank_text, (self.rect.x + CARD_WIDTH - 20, self.rect.y + CARD_HEIGHT - 25))

