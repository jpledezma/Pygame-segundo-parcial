import pygame
from pygame.locals import *
from pygame.rect import Rect as Rect
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

class SliderButton(Button):
    def __init__(self, rect: Rect, text: str | None = None) -> None:
        super().__init__(rect, text)
        path_img = path.join(getcwd(), "assets", "gui", "slider_button.png")
        path_img_hover = path.join(getcwd(), "assets", "gui", "slider_button_hover.png")

        self.img = pygame.image.load(path_img)
        self.img_hover = pygame.image.load(path_img_hover)

        self.img = pygame.transform.scale(self.img, (self.rect.width, self.rect.height))
        self.img_hover = pygame.transform.scale(self.img_hover, (self.rect.width, self.rect.height))


class Menu():
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        path_bg_img = path.join(getcwd(), "assets", "gui", "menu_background.jpg")
        self.background_img = pygame.image.load(path_bg_img)
        self.background_img = pygame.transform.scale(self.background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.path_font = path.join(getcwd(), "assets", "fonts", "ENDOR___.ttf")
        self.font = pygame.font.Font(self.path_font, 40)

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
        
        self.text_surface = self.font.render("Ira Tenax", True, (218, 188, 21))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (SCREEN_WIDTH //2, 100)

        self.button_play = Button(pygame.Rect(400, 200, 220, 70), "Play")
        self.button_ranking = Button(pygame.Rect(400, 300, 220, 70), "Ranking")
        self.button_options = Button(pygame.Rect(400, 400, 220, 70), "Options")
        self.button_exit = Button(pygame.Rect(400, 500, 220, 70), "Quit game")

        self.buttons = [self.button_play, self.button_ranking, self.button_options, self.button_exit]

        for button in self.buttons:
            button.rect.centerx = SCREEN_WIDTH // 2
            button.text_rect.centerx = SCREEN_WIDTH // 2

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
                    if self.button_ranking.rect.collidepoint(pygame.mouse.get_pos()):
                        return
                    if self.button_options.rect.collidepoint(pygame.mouse.get_pos()):
                        pass
                    if self.button_play.rect.collidepoint(pygame.mouse.get_pos()):
                        return
            
            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hover = True
                else:
                    button.hover = False
            
            self.draw()

class OptionsMenu(Menu):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        self.secondary_font = pygame.font.Font(self.path_font, 24)

        self.text_surface = self.font.render("Options", True, (218, 188, 21))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (SCREEN_WIDTH // 2 , 100)

        self.text_music_volume_surface = self.secondary_font.render("Music volume", True, (218, 188, 21))
        self.text_music_volume_rect = self.text_music_volume_surface.get_rect()
        self.text_music_volume_rect.center = (SCREEN_WIDTH // 2 , 215)

        self.text_effects_volume_surface = self.secondary_font.render("Effects volume", True, (218, 188, 21))
        self.text_effects_volume_rect = self.text_effects_volume_surface.get_rect()
        self.text_effects_volume_rect.center = (SCREEN_WIDTH // 2 , 315)

        self.button_music = Button(pygame.Rect(400, 400, 220, 70), "Music on/off")
        self.button_exit = Button(pygame.Rect(400, 500, 220, 70), "Main Menu")

        self.slider_music = SliderButton(pygame.Rect(400, 250, 35, 20))
        self.slider_effects = SliderButton(pygame.Rect(400, 350, 35, 20))

        self.range_slider_music = pygame.Rect(0, 0, 300, 10)
        self.range_slider_music.centery = self.slider_music.rect.centery
        self.range_slider_music.centerx = SCREEN_WIDTH // 2
        
        self.range_slider_effects = pygame.Rect(0, 0, 300, 10)
        self.range_slider_effects.centery = self.slider_effects.rect.centery
        self.range_slider_effects.centerx = SCREEN_WIDTH // 2

        self.slider_music_pressed = False
        self.slider_effects_pressed = False

        self.volume_music = 1
        self.volume_effects = 1
        
        self.buttons = [self.button_music, self.button_exit, self.slider_music, self.slider_effects]

        for button in self.buttons:
            if not isinstance(button, SliderButton):
                button.rect.centerx = SCREEN_WIDTH // 2
                button.text_rect.centerx = SCREEN_WIDTH // 2

    def draw(self):
        self.screen.blit(self.background_img, (0, 0))

        pygame.draw.rect(self.screen, (206, 142, 24), self.range_slider_music, border_radius = 5)
        pygame.draw.rect(self.screen, (206, 142, 24), self.range_slider_effects, border_radius = 5)

        self.screen.blit(self.text_surface, self.text_rect)
        self.screen.blit(self.text_music_volume_surface, self.text_music_volume_rect)
        self.screen.blit(self.text_effects_volume_surface, self.text_effects_volume_rect)
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
                        return
                    if self.button_music.rect.collidepoint(pygame.mouse.get_pos()):
                        pass
                    if self.slider_music.rect.collidepoint(pygame.mouse.get_pos()):
                        self.slider_music_pressed = True
                    if self.slider_effects.rect.collidepoint(pygame.mouse.get_pos()):
                        self.slider_effects_pressed = True
                if event.type == MOUSEBUTTONUP:
                    self.slider_music_pressed = False
                    self.slider_effects_pressed = False
            
            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hover = True
                else:
                    button.hover = False

            if self.slider_music_pressed and self.slider_music.rect.collidepoint(pygame.mouse.get_pos()):
                self.slider_music.rect.centerx = pygame.mouse.get_pos()[0]

            if self.slider_effects_pressed and self.slider_effects.rect.collidepoint(pygame.mouse.get_pos()):
                self.slider_effects.rect.centerx = pygame.mouse.get_pos()[0]

            if self.slider_music.rect.centerx <= self.range_slider_music.left:
                self.slider_music.rect.centerx = self.range_slider_music.left
            if self.slider_music.rect.centerx >= self.range_slider_music.right:
                self.slider_music.rect.centerx = self.range_slider_music.right

            if self.slider_effects.rect.centerx <= self.range_slider_effects.left:
                self.slider_effects.rect.centerx = self.range_slider_effects.left
            if self.slider_effects.rect.centerx >= self.range_slider_effects.right:
                self.slider_effects.rect.centerx = self.range_slider_effects.right
            
            self.volume_music = self.get_volume(self.slider_music.rect.centerx)
            self.volume_effects = self.get_volume(self.slider_effects.rect.centerx)

            self.draw()

    def get_volume(self, value: int):
        max_value = self.range_slider_effects.right - self.range_slider_effects.left
        value = value - self.range_slider_effects.left

        volume = value / max_value

        return volume
    
class PauseMenu(Menu):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        
        self.text_surface = self.font.render("Pause", True, (255, 230, 0))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (SCREEN_WIDTH // 2, 200)

        self.button_continue = Button(pygame.Rect(400, 300, 220, 70), "Continue")
        self.button_options = Button(pygame.Rect(400, 400, 220, 70), "Options")
        self.button_exit = Button(pygame.Rect(400, 500, 220, 70), "Main Menu")

        self.buttons = [self.button_continue, self.button_options, self.button_exit]

        for button in self.buttons:
            button.rect.centerx = SCREEN_WIDTH // 2
            button.text_rect.centerx = SCREEN_WIDTH // 2

    def draw(self):
        self.screen.blit(self.filter, (0, 0))
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
                        return
                    if self.button_options.rect.collidepoint(pygame.mouse.get_pos()):
                        pass
                    if self.button_continue.rect.collidepoint(pygame.mouse.get_pos()):
                        return
            
            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hover = True
                else:
                    button.hover = False
            
            self.draw()

class RankingMenu(Menu):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        
        self.text_surface = self.font.render("Ranking", True, (218, 188, 21))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (SCREEN_WIDTH //2, 100)

        self.button_exit = Button(pygame.Rect(400, 500, 220, 70), "Main Menu")

        self.buttons = [self.button_exit]

        for button in self.buttons:
            button.rect.centerx = SCREEN_WIDTH // 2
            button.text_rect.centerx = SCREEN_WIDTH // 2

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
                        return

            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hover = True
                else:
                    button.hover = False
            
            self.draw()

class SelectionMenu(Menu):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        
        self.text_surface = self.font.render("Select Level", True, (218, 188, 21))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (SCREEN_WIDTH //2, 100)

        self.button_lvl_1 = Button(pygame.Rect(400, 180, 220, 70), "Level 1")
        self.button_lvl_2 = Button(pygame.Rect(400, 280, 220, 70), "Level 2")
        self.button_lvl_3 = Button(pygame.Rect(400, 380, 220, 70), "Level 3")
        self.button_exit = Button(pygame.Rect(400, 500, 220, 70), "Main Menu")

        self.buttons = [self.button_exit, self.button_lvl_1, self.button_lvl_2, self.button_lvl_3]

        for button in self.buttons:
            button.rect.centerx = SCREEN_WIDTH // 2
            button.text_rect.centerx = SCREEN_WIDTH // 2

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
                        return
                    if self.button_lvl_1.rect.collidepoint(pygame.mouse.get_pos()):
                        return
                    if self.button_lvl_2.rect.collidepoint(pygame.mouse.get_pos()):
                        return
                    if self.button_lvl_3.rect.collidepoint(pygame.mouse.get_pos()):
                        return

            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    button.hover = True
                else:
                    button.hover = False
            
            self.draw()