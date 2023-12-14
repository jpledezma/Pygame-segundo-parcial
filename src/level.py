import pygame
from pygame.locals import *
from config import *
from entities import *
from platforms import *
import os
from utils import *

class Level():
    def __init__(self, screen: pygame.Surface, 
                 spritesheets_data: dict, 
                 tileset_data: dict, 
                 entities_data: dict, 
                 map_data: dict,
                 *aditional_groups: pygame.sprite.Group
                 ) -> None:

        self.clock = pygame.time.Clock()

        self.screen = screen

        self.final_boss_flag = False

        self.spritesheets_data = spritesheets_data
        self.tileset_data = tileset_data
        self.entities_data = entities_data
        self.map_data = map_data

        self.enemies = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        
        self.entities = pygame.sprite.Group()
        self.final_boss_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        tileset_img = pygame.image.load(tileset_data["path_img"])
        
        tileset = Tileset(tileset_img, tileset_data["tile_width"], tileset_data["tile_height"])
        
        self.background_layers = []
        for background_path in tileset_data["background_layers"]:
            background_layer = pygame.image.load(background_path)
            background_layer = pygame.transform.scale(background_layer, (SCREEN_WIDTH, SCREEN_HEIGHT))
            background_layer = background_layer.convert_alpha()
            self.background_layers.append(background_layer)

        tiles_map = read_tile_map(map_data["path_map"])
        self.surfaces_list = tileset.get_map(tiles_map)


        for item in self.surfaces_list:
            Platform(item[0], item[1], (self.all_sprites, self.platforms))



        player_img = pygame.image.load(self.spritesheets_data["player"]["path"]).convert_alpha()
        player_spritesheet = SpriteSheet(player_img, *list(self.spritesheets_data["player"].values())[1:])

        # Jugador
        self.player = Player((self.all_sprites, self.entities), player_spritesheet, map_data["player_position"], *self.entities_data["player"].values())

        # Enemigos
        for enemies, positions in self.map_data["enemies_positions"].items():
            if enemies == "nightbornes":
                nightborne_img = pygame.image.load(self.spritesheets_data["nightborne"]["path"]).convert_alpha()
                nightborne_spritesheet = SpriteSheet(nightborne_img, *list(self.spritesheets_data["nightborne"].values())[1:])
                for position in positions:
                    NightBorne((self.all_sprites, self.entities, self.enemies), nightborne_spritesheet, position, *self.entities_data["nightborne"].values())
           
            if enemies == "evil_wizards":
                evil_wizard_img = pygame.image.load(self.spritesheets_data["evil_wizard"]["path"]).convert_alpha()
                evil_wizard_spritesheet = SpriteSheet(evil_wizard_img, *list(self.spritesheets_data["evil_wizard"].values())[1:])
                for position in positions:
                    EvilWizard((self.all_sprites, self.entities, self.enemies), evil_wizard_spritesheet, position, *self.entities_data["evil_wizard"].values())

            if enemies == "shuriken_dudes":
                shuriken_dude_img = pygame.image.load(self.spritesheets_data["shuriken_dude"]["path"]).convert_alpha()
                shuriken_dude_spritesheet = SpriteSheet(shuriken_dude_img, *list(self.spritesheets_data["shuriken_dude"].values())[1:])
                for position in positions:
                    ShurikenDude((self.all_sprites, self.entities, self.enemies), shuriken_dude_spritesheet, position, *self.entities_data["shuriken_dude"].values())
           
            if enemies == "bringer_of_death":
                bringer_of_death_img = pygame.image.load(self.spritesheets_data["bringer_of_death"]["path"]).convert_alpha()
                bringer_of_death_spritesheet = SpriteSheet(bringer_of_death_img, *list(self.spritesheets_data["bringer_of_death"].values())[1:])
                self.final_boss = BringerOfDeath(self.final_boss_group, bringer_of_death_spritesheet, positions, *self.entities_data["bringer_of_death"].values())
                self.final_boss_flag = True
           
        self.keydown_keys = []
        
    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.close()

                if event.type == KEYDOWN:
                    if not event.key in self.keydown_keys:
                        self.keydown_keys.append(event.key)
                if event.type == KEYUP:
                    if event.key in self.keydown_keys:
                        self.keydown_keys.remove(event.key)

                # if event.type == MOUSEBUTTONDOWN:
                #     if self.player.rect.collidepoint(pygame.mouse.get_pos()):
                #         self.player.hurt(100)

            if self.enemies.sprites() == [] and self.final_boss_flag:
                self.all_sprites.add(self.final_boss)
                self.final_boss_flag = False

            self.draw()
            self.update()
            
            
        return

    def draw(self):
        for background in self.background_layers:
            self.screen.blit(background, (0, 0))

        self.all_sprites.draw(self.screen)

        for entity in self.entities:
            entity.draw_rect(self.screen, (88, 182, 192))

        # for platform in self.platforms:
            # platform.draw_rect(self.screen, (250,0,0)) 

    def update(self):

        for entity in self.entities:
            entity.time_iframes(pygame.time.get_ticks())

        self.player.detect_actions(self.platforms.sprites(), self.keydown_keys)

        for enemy in self.enemies:
            enemy.detect_actions(self.platforms.sprites(), self.player)
            if enemy.hitbox.colliderect(self.player.hitbox):
                self.player.hurt(enemy.physical_power)
                if self.player.actions['attacking']['flag']:
                    enemy.hurt(self.player.physical_power)
            if enemy.health <= 0:
                enemy.kill()

        self.all_sprites.update()

        pygame.display.flip()

    def close(self):
        pygame.quit()
        exit()

