import pygame
from pygame.locals import *
from config import *
from entities import *
import json
import os

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Juego piola")
        pygame.display.set_icon(ICON_IMG)

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.sprites_data_path = os.path.join(os.getcwd(), "data", "surfaces.json")

        with open(self.sprites_data_path, "r", encoding="utf-8") as file:
            sprites_data = json.load(file)

        player_img = pygame.image.load(sprites_data["player"]["path"]).convert_alpha()
        player_spritesheet = SpriteSheet(player_img, sprites_data["player"]["rows"], sprites_data["player"]["cols"], sprites_data["player"]["width"], sprites_data["player"]["height"], sprites_data["player"]["anim_keys"], sprites_data["player"]["anim_frames"], 2)

        nightborne_img = pygame.image.load(sprites_data["nightborne"]["path"]).convert_alpha()
        nightborne_spritesheet = SpriteSheet(nightborne_img, sprites_data["nightborne"]["rows"], sprites_data["nightborne"]["cols"], sprites_data["nightborne"]["width"], sprites_data["nightborne"]["height"], sprites_data["nightborne"]["anim_keys"], sprites_data["nightborne"]["anim_frames"], 2.5)

        evil_wizard_img = pygame.image.load(sprites_data["evil_wizard"]["path"]).convert_alpha()
        evil_wizard_spritesheet = SpriteSheet(evil_wizard_img, sprites_data["evil_wizard"]["rows"], sprites_data["evil_wizard"]["cols"], sprites_data["evil_wizard"]["width"], sprites_data["evil_wizard"]["height"], sprites_data["evil_wizard"]["anim_keys"], sprites_data["evil_wizard"]["anim_frames"], 2)

        bringer_of_death_img = pygame.image.load(sprites_data["bringer_of_death"]["path"]).convert_alpha()
        bringer_of_death_spritesheet = SpriteSheet(bringer_of_death_img, sprites_data["bringer_of_death"]["rows"], sprites_data["bringer_of_death"]["cols"], sprites_data["bringer_of_death"]["width"], sprites_data["bringer_of_death"]["height"], sprites_data["bringer_of_death"]["anim_keys"], sprites_data["bringer_of_death"]["anim_frames"], 3)
        
        shuriken_dude_img = pygame.image.load(sprites_data["shuriken_dude"]["path"]).convert_alpha()
        shuriken_dude_spritesheet = SpriteSheet(shuriken_dude_img, sprites_data["shuriken_dude"]["rows"], sprites_data["shuriken_dude"]["cols"], sprites_data["shuriken_dude"]["width"], sprites_data["shuriken_dude"]["height"], sprites_data["shuriken_dude"]["anim_keys"], sprites_data["shuriken_dude"]["anim_frames"], 1.5)

        self.player = Player((250, 250), self.all_sprites, player_spritesheet, 1000, 6, 40, 40, 7, 1000, gravity=0.2, hitbox_scale=(0.3, 0.78))
        self.nightborne = NightBorne((380, 100), (self.all_sprites, self.enemies), nightborne_spritesheet, 1500, 4, hitbox_scale=(0.5, 0.45))
        self.evil_wizard = EvilWizard((500, 400), (self.all_sprites, self.enemies), evil_wizard_spritesheet, 1500, 4, hitbox_scale=(0.3, 0.35), gravity=0.1)
        self.bringer_of_death = BringerOfDeath((500, 400), (self.all_sprites, self.enemies), bringer_of_death_spritesheet, 1500, 4, hitbox_scale=(0.3, 0.6), gravity=0.1)
        self.shuriken_dude = ShurikenDude((600, 100), (self.all_sprites, self.enemies), shuriken_dude_spritesheet, 1500, 4, hitbox_scale=(0.45, 0.85), gravity=0.1)

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
                    enemy.hurt(500)
            if enemy.health <= 0:
                enemy.kill()
        self.all_sprites.update(self.keydown_keys)
        # print(self.player.health, self.nightborne.health, self.evil_wizard.health)

        pygame.display.flip()

    def close(self):
        pygame.quit()

