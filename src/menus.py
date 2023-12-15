import pygame
from pygame.locals import *
from config import *
from os import getcwd, path

class Button():
    def __init__(self, rect: pygame.Rect, text: str | None = None) -> None:

        self.rect = rect
        self.text = text

        path_img = path.join(getcwd(), "assets", "gui", "menu_button.png")
        path_img_hover = path.join(getcwd(), "assets", "gui", "menu_button_hover.png")
        path_font = path.join(getcwd(), "assets", "fonts", "ENDOR___.ttf")

        self.img = pygame.image.load(path_img)
        self.img_hover = pygame.image.load(path_img_hover)

        self.img = pygame.transform.scale(self.img, (self.rect.width, self.rect.height))
        self.img_hover = pygame.transform.scale(self.img_hover, (self.rect.width, self.rect.height))

        self.font = pygame.font.Font(path_font, 24)

        if self.text:
            self.text_surface = self.font.render(text, True, (218, 188, 21))
            self.text_rect = self.text_surface.get_rect()
            self.text_rect.center = self.rect.center

        self.hover = False

    def draw(self, screen: pygame.Surface):
        if self.hover:
            screen.blit(self.img_hover, self.rect)
        else:
            screen.blit(self.img, self.rect)
        if self.text:
            screen.blit(self.text_surface, self.text_rect)


class Menu():
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        path_bg_img = path.join(getcwd(), "assets", "gui", "menu_background.jpg")
        self.background_img = pygame.image.load(path_bg_img)
        self.background_img = pygame.transform.scale(self.background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.filter = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        self.filter.fill((0, 150, 150, 1))

        self.running = True

    def run(self):
        
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.close()

            self.draw()

    def draw(self):
        pygame.display.flip()

    def close(self):
        pygame.quit()
        exit()

class MainMenu(Menu):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        path_font = path.join(getcwd(), "assets", "fonts", "ENDOR___.ttf")
        self.font = pygame.font.Font(path_font, 40)
        self.text_surface = self.font.render("Ira Tenax", True, (218, 188, 21))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (SCREEN_WIDTH //2 - 25, 100)

        self.button_play = Button(pygame.Rect(400, 200, 220, 70), "Play")
        self.button_select_level = Button(pygame.Rect(400, 300, 220, 70), "Select Level")
        self.button_options = Button(pygame.Rect(400, 400, 220, 70), "Options")
        self.button_exit = Button(pygame.Rect(400, 500, 220, 70), "Exit to Desktop")

        self.buttons = [self.button_play, self.button_select_level, self.button_options, self.button_exit]

    def draw(self):
        self.screen.blit(self.background_img, (0, 0))
        self.screen.blit(self.text_surface, self.text_rect)
        for button in self.buttons:
            button.draw(self.screen)
        super().draw()
        
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.close()
                if event.type == MOUSEBUTTONDOWN:
                    if self.button_exit.rect.collidepoint(pygame.mouse.get_pos()):
                        self.close()
                    if self.button_options.rect.collidepoint(pygame.mouse.get_pos()):
                        pass
                    if self.button_select_level.rect.collidepoint(pygame.mouse.get_pos()):
                        pass
                    if self.button_play.rect.collidepoint(pygame.mouse.get_pos()):
                        return
            
            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hover = True
                else:
                    button.hover = False


            
            self.draw()
