import pygame
from pygame.locals import *
from config import *
from entities import *
import platform

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Juego piola")
        pygame.display.set_icon(ICON_IMG)

        self.all_sprites = pygame.sprite.Group()

        self.path_player = "assets/sprites/jugador/HeroKnight.png"

        self.all_sprites = pygame.sprite.Group()

        lista_keys = ['idle', 'run', 'at1', 'at2', 'at3', 'jump', 'fall', 'hurt', 'death', 'block_idle', 'block', 'roll', 'ledge_grab', 'wall_slide']
        lista_frames = [8, 10, 6, 6, 8, 3, 4, 3, 10, 8, 5, 9, 5, 5]

        player_img = pygame.image.load(self.path_player).convert_alpha()
        hoja_sprites = SpriteSheet(player_img, 9, 10, 100, 55, lista_keys, lista_frames, 2)

        self.player = Player((250, 250), self.all_sprites, hoja_sprites, 500, 500)

        # self.platforms = pygame.sprite.Group()
        
    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False


            self.draw()
            self.update()
            
            
        self.close()

    def draw(self):
        self.screen.fill(LIGHT_BLUE)
        self.all_sprites.draw(self.screen)

    def update(self):
        self.all_sprites.update()

        pygame.display.flip()

    def close(self):
        pygame.quit()

