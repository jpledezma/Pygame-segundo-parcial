import pygame
from pygame.locals import *
from config import *
from entities import *
from platforms import *
import os
from utils import *

# TODO Colisiones con las plataformas

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Juego piola")
        pygame.display.set_icon(ICON_IMG)

        self.all_sprites = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        self.sprites_data_path = os.path.join(os.getcwd(), "data", "sprites.json")
        sprites_data = read_json(self.sprites_data_path)

        self.tile_sets_data_path = os.path.join(os.getcwd(), "data", "tile_sets.json")
        tile_sets_data = read_json(self.tile_sets_data_path)

        oak_woods_tileset_img = pygame.image.load(tile_sets_data["oak_woods"]["path_img"])
        oak_woods_tileset = Tileset(oak_woods_tileset_img, tile_sets_data["oak_woods"]["tile_width"], tile_sets_data["oak_woods"]["tile_height"])

        self.oak_woods_background_layers = []
        for background_path in tile_sets_data["oak_woods"]["background_layers"]:
            background_layer = pygame.image.load(background_path)
            background_layer = pygame.transform.scale(background_layer, (SCREEN_WIDTH, SCREEN_HEIGHT))
            background_layer = background_layer.convert_alpha()
            self.oak_woods_background_layers.append(background_layer)

        oak_woods_tile_map = read_tile_map(tile_sets_data["oak_woods"]["path_map"])
        self.oak_woods_surfaces_list = oak_woods_tileset.get_map(oak_woods_tile_map)

        for item in self.oak_woods_surfaces_list:
            Platform(item[0], item[1], (self.all_sprites, self.platforms))

        player_img = pygame.image.load(sprites_data["player"]["path"]).convert_alpha()
        player_spritesheet = SpriteSheet(player_img, sprites_data["player"]["rows"], sprites_data["player"]["cols"], sprites_data["player"]["width"], sprites_data["player"]["height"], sprites_data["player"]["anim_keys"], sprites_data["player"]["anim_frames"], 1)

        nightborne_img = pygame.image.load(sprites_data["nightborne"]["path"]).convert_alpha()
        nightborne_spritesheet = SpriteSheet(nightborne_img, sprites_data["nightborne"]["rows"], sprites_data["nightborne"]["cols"], sprites_data["nightborne"]["width"], sprites_data["nightborne"]["height"], sprites_data["nightborne"]["anim_keys"], sprites_data["nightborne"]["anim_frames"], 1.2)

        evil_wizard_img = pygame.image.load(sprites_data["evil_wizard"]["path"]).convert_alpha()
        evil_wizard_spritesheet = SpriteSheet(evil_wizard_img, sprites_data["evil_wizard"]["rows"], sprites_data["evil_wizard"]["cols"], sprites_data["evil_wizard"]["width"], sprites_data["evil_wizard"]["height"], sprites_data["evil_wizard"]["anim_keys"], sprites_data["evil_wizard"]["anim_frames"], 1.2)

        bringer_of_death_img = pygame.image.load(sprites_data["bringer_of_death"]["path"]).convert_alpha()
        bringer_of_death_spritesheet = SpriteSheet(bringer_of_death_img, sprites_data["bringer_of_death"]["rows"], sprites_data["bringer_of_death"]["cols"], sprites_data["bringer_of_death"]["width"], sprites_data["bringer_of_death"]["height"], sprites_data["bringer_of_death"]["anim_keys"], sprites_data["bringer_of_death"]["anim_frames"], 2)
        
        shuriken_dude_img = pygame.image.load(sprites_data["shuriken_dude"]["path"]).convert_alpha()
        shuriken_dude_spritesheet = SpriteSheet(shuriken_dude_img, sprites_data["shuriken_dude"]["rows"], sprites_data["shuriken_dude"]["cols"], sprites_data["shuriken_dude"]["width"], sprites_data["shuriken_dude"]["height"], sprites_data["shuriken_dude"]["anim_keys"], sprites_data["shuriken_dude"]["anim_frames"], 0.8)

        self.player = Player((200, 400), (self.all_sprites, self.entities), player_spritesheet, health=1000, speed=3, physical_power=40, magic_power=40, jump_power=6, iframes=1000, speed_roll=3, gravity=0.2, hitbox_scale=(0.3, 0.78))
        # self.nightborne = NightBorne((380, 100), (self.all_sprites, self.enemies, self.entities), nightborne_spritesheet, 1500, 1, hitbox_scale=(0.5, 0.45))
        # self.evil_wizard = EvilWizard((500, 400), (self.all_sprites, self.enemies, self.entities), evil_wizard_spritesheet, 1500, 1, hitbox_scale=(0.3, 0.35), gravity=0.1)
        # self.bringer_of_death = BringerOfDeath((500, 400), (self.all_sprites, self.enemies, self.entities), bringer_of_death_spritesheet, 1500, 1, hitbox_scale=(0.3, 0.6), gravity=0.1)
        # self.shuriken_dude = ShurikenDude((600, 100), (self.all_sprites, self.enemies, self.entities), shuriken_dude_spritesheet, 1500, 1, hitbox_scale=(0.45, 0.85), gravity=0.1)

        self.keydown_keys = []


        
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
        for background in self.oak_woods_background_layers:
            self.screen.blit(background, (0, 0))

        self.all_sprites.draw(self.screen)
        
        for entity in self.entities:
            entity.draw_rect(self.screen, (250,250,250)) 
            entity.time_iframes(pygame.time.get_ticks())

        for platform in self.platforms:
            platform.draw_rect(self.screen, (250,0,0)) 

    def update(self):

        self.player.detect_actions(self.platforms.sprites(), self.keydown_keys)
        for enemy in self.enemies:
            enemy.detect_actions(self.platforms.sprites())
            if enemy.hitbox.colliderect(self.player.hitbox):
                self.player.hurt(enemy.physical_power)
                if self.player.actions['attacking']['flag']:
                    enemy.hurt(500)
            if enemy.health <= 0:
                enemy.kill()

        self.all_sprites.update()

        pygame.display.flip()

    def close(self):
        pygame.quit()

