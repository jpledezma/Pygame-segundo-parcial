import pygame
from os import path, getcwd
from config import *

class HUD():
    def __init__(self) -> None:
        self.max_health = 1000
        self.rect_health = pygame.Rect(50, 660, 200, 15)
        self.rect_health_bg = pygame.Rect(45, 655, 210, 25)

        self.path_bg_img = path.join(getcwd(), "assets", "backgrounds", "hud_background.png")
        self.bg_img = pygame.image.load(self.path_bg_img)

        self.path_font = path.join(getcwd(), "assets", "fonts", "ENDOR___.ttf")
        self.font = pygame.font.Font(self.path_font, 20)

        self.text_hp = self.font.render("Health", True, (248, 237, 24))

        self.max_width = 200

    def draw(self, screen: pygame.Surface, timer: int, enemies: int, key_items: int, player_hp: int, player_max_hp):

        self.max_health = player_max_hp
        self.calculate_hp_rect(player_hp, player_max_hp)

        self.text_timer = self.font.render(f"Time left: {timer}", True, (248, 237, 24))
        self.text_enemies_killed = self.font.render(f"Enemies killed: {enemies}", True, (248, 237, 24))
        self.text_key_items = self.font.render(f"Key items: {key_items}/3", True, (248, 237, 24))

        screen.blit(self.bg_img, (0, SCREEN_HEIGHT - 100))
        screen.blit(self.text_hp, (120, 610))
        screen.blit(self.text_timer, (350, 630))
        screen.blit(self.text_enemies_killed, (550, 630))
        screen.blit(self.text_key_items, (750, 630))
        pygame.draw.rect(screen, (224, 168, 37), self.rect_health_bg, border_radius = 3)
        pygame.draw.rect(screen, (224, 0, 0), self.rect_health, border_radius = 3)

    def calculate_hp_rect(self, hp: int, max_hp: int):
        
        hp_percentage = hp / self.max_health * 100

        width = hp_percentage * self.max_width / 100
        if width >= 0:
            self.rect_health.width = width
        