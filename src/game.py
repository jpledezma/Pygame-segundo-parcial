import pygame
from pygame.locals import *
from config import *
from entities import *

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Juego piola")
        pygame.display.set_icon(ICON_IMG)

        self.all_sprites = pygame.sprite.Group()

        self.path_player = "assets/sprites/jugador/HeroKnight.png"
        self.path_nightborne = "assets/sprites/enemigos/NightBorne.png"

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        anim_keys_player = ['idle', 'run', 'at1', 'at2', 'at3', 'jump', 'fall', 'hurt', 'death', 'block_idle', 'block', 'roll', 'ledge_grab', 'wall_slide']
        anim_frames_player = [8, 10, 6, 6, 8, 3, 4, 3, 10, 8, 5, 9, 5, 5]

        anim_keys_nightborne = ['idle', 'run', 'jump', 'attack', 'hurt', 'death']
        anim_frames_nightborne = [9, 6, 5, 12, 5, 23]

        nightborne_img = pygame.image.load(self.path_nightborne).convert_alpha()
        enemy_spritesheet = SpriteSheet(nightborne_img, 6, 10, 80, 80, anim_keys_nightborne, anim_frames_nightborne, 2.5)

        player_img = pygame.image.load(self.path_player).convert_alpha()
        player_spritesheet = SpriteSheet(player_img, 9, 10, 100, 55, anim_keys_player, anim_frames_player, 2)

        self.player = Player((250, 250), self.all_sprites, player_spritesheet, 1000, 6, 40, 40, 7, 1000, gravity=0.2, hitbox_scale=(0.3, 0.78))
        self.enemy = NightBorne((380, 100), (self.all_sprites, self.enemies), enemy_spritesheet, 1500, 4, hitbox_scale=(0.5, 0.5))

        self.keydown_keys = []

        # self.platforms = pygame.sprite.Group()
        
    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == KEYDOWN:
                    if not event.key in self.keydown_keys:
                        self.keydown_keys.append(event.key)
                if event.type == KEYUP:
                    if event.key in self.keydown_keys:
                        self.keydown_keys.remove(event.key)

                if event.type == MOUSEBUTTONDOWN:
                    if self.player.rect.collidepoint(pygame.mouse.get_pos()):
                        self.player.hurt(100)

            # print(self.keydown_keys)
            self.draw()
            self.update()
            
            
        self.close()

    def draw(self):
        self.screen.fill(LIGHT_BLUE)
        self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites:
            sprite.draw_rect(self.screen, (0,0,0)) 

        for entity in self.all_sprites:
            entity.time_iframes(pygame.time.get_ticks())

    def update(self):
        # if self.enemy.rect.colliderect(self.player.rect):
        #     self.player.hurt(self.enemy.physical_power)
        for enemy in self.enemies:
            if enemy.hitbox.colliderect(self.player.hitbox):
                self.player.hurt(enemy.physical_power)
                if self.player.actions['attacking']['flag']:
                    self.enemy.hurt(500)
            if enemy.health <= 0:
                enemy.kill()
        self.all_sprites.update(self.keydown_keys)
        print(self.player.health, self.enemy.health)

        pygame.display.flip()

    def close(self):
        pygame.quit()

