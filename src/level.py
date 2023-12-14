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

        self.player_group = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.final_boss_group = pygame.sprite.Group()

        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.player_projectiles = pygame.sprite.Group()

        self.entities = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        
        self.all_sprites = pygame.sprite.Group()

        tileset_level_img = pygame.image.load(tileset_data["path_img"])
        tileset_level = Tileset(tileset_level_img, tileset_data["tile_width"], tileset_data["tile_height"])
        
        self.background_layers = []
        for background_path in tileset_data["background_layers"]:
            background_layer = pygame.image.load(background_path)
            background_layer = pygame.transform.scale(background_layer, (SCREEN_WIDTH, SCREEN_HEIGHT))
            background_layer = background_layer.convert_alpha()
            self.background_layers.append(background_layer)

        tiles_map = read_tile_map(map_data["path_map"])
        self.surfaces_list = tileset_level.get_map(tiles_map)


        for item in self.surfaces_list:
            Platform(item[0], item[1], (self.all_sprites, self.platforms))

        # Instanciar jugador
        player_img = pygame.image.load(self.spritesheets_data["player"]["path"]).convert_alpha()
        player_spritesheet = SpriteSheet(player_img, *list(self.spritesheets_data["player"].values())[1:])
        self.player = Player((self.all_sprites, self.entities, self.player_group), player_spritesheet, map_data["player_position"], *self.entities_data["player"].values())

        # Instanciar enemigos
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------
        for enemies, positions in self.map_data["enemies_positions"].items():
            enemy_img = pygame.image.load(self.spritesheets_data[enemies]["path"]).convert_alpha()
            enemy_spritesheet = SpriteSheet(enemy_img, *list(self.spritesheets_data[enemies].values())[1:])
            if enemies == "nightborne":
                for position in positions:
                    NightBorne((self.all_sprites, self.entities, self.enemies), enemy_spritesheet, position, *self.entities_data["nightborne"].values())
            if enemies == "evil_wizard":
                for position in positions:
                    EvilWizard((self.all_sprites, self.entities, self.enemies), enemy_spritesheet, position, *self.entities_data["evil_wizard"].values())
            if enemies == "shuriken_dude":
                for position in positions:
                    ShurikenDude((self.all_sprites, self.entities, self.enemies), enemy_spritesheet, position, *self.entities_data["shuriken_dude"].values())
            if enemies == "bringer_of_death":
                self.final_boss = BringerOfDeath(self.final_boss_group, enemy_spritesheet, positions, *self.entities_data["bringer_of_death"].values())
                self.final_boss_flag = True
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------

        self.flag = True
    
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
                    if event.key == K_t:
                        running = False
                if event.type == KEYUP:
                    if event.key in self.keydown_keys:
                        self.keydown_keys.remove(event.key)

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
        
        # for entity in self.entities:
        #     entity.draw_rect(self.screen, (88, 182, 192))
        for enemy in self.enemies:
            if isinstance(enemy, NightBorne):
                pygame.draw.rect(self.screen, (43, 176, 199), enemy.attack_hitbox, 2)

        # pygame.draw.rect(self.screen, [240, 120, 23], self.player.attack_hitbox, 1)
        pygame.draw.rect(self.screen, [0, 120, 230], self.player.block_hitbox, 2)

        # for platform in self.platforms:
            # platform.draw_rect(self.screen, (250,0,0)) 

    def update(self):

        self.player.detect_actions(self.platforms.sprites(), self.keydown_keys)
        print(self.player.health)

        for entity in self.entities:
            entity.time_iframes(pygame.time.get_ticks())
            if entity.rect.top > SCREEN_HEIGHT or entity.rect.bottom < 0 \
            or entity.rect.left > SCREEN_WIDTH or entity.rect.right < 0:
                entity.kill()
                print("mi planeta me necesita")

        for projectile in self.projectiles:
            for platform in self.platforms:
                if projectile.rect.colliderect(platform.rect):
                    projectile.kill()
                    continue

        for projectile in self.enemy_projectiles:
            if self.player.hitbox.colliderect(projectile.rect):
                self.player.hurt(projectile.physical_power)
                projectile.kill()
            if self.player.block_hitbox.colliderect(projectile.rect):
                projectile.facing = "f" if projectile.facing == "b" else "b"
                self.player_projectiles.add(projectile)
                self.enemy_projectiles.remove(projectile)

        for enemy in self.enemies:
            enemy.detect_actions(self.platforms.sprites(), self.player)

            # Daño de los proyectiles del jugador a los enemigos
            for projectile in self.player_projectiles:
                if enemy.hitbox.colliderect(projectile.rect):
                    enemy.hurt(projectile.physical_power)
                    projectile.kill()

            # Daño del ataque del jugador a los enemigos
            if enemy.hitbox.colliderect(self.player.attack_hitbox):
                enemy.hurt(self.player.physical_power)

            # Daño por contacto al jugador
            if enemy.hitbox.colliderect(self.player.hitbox):
                self.player.hurt(enemy.physical_power // 2)

            # Parry a los nightborne
            if isinstance(enemy, NightBorne) and enemy.attack_hitbox.colliderect(self.player.block_hitbox):
                enemy.stun(1000)
                self.player.hurt(0) # Esto es para hacer invulnerable al jugador por un tiempo

            # Ataque del enemigo al jugador
            if not isinstance(enemy, ShurikenDude) \
            and enemy.attack_hitbox.colliderect(self.player.hitbox):
                self.player.hurt(enemy.physical_power)

            # Lanzar shuriken
            if isinstance(enemy, ShurikenDude) and enemy.throw_shuriken:
                self.flag = False
                shuriken_img = pygame.image.load(self.spritesheets_data["shuriken"]["path"]).convert_alpha()
                shuriken_spritesheet = SpriteSheet(shuriken_img, *list(self.spritesheets_data["shuriken"].values())[1:])
                Projectile((self.all_sprites, self.entities, self.projectiles, self.enemy_projectiles), shuriken_spritesheet, enemy.rect.center, enemy.facing, *self.entities_data["shuriken"].values())

            if enemy.health <= 0:
                enemy.kill()

        self.all_sprites.update()

        pygame.display.flip()

    def close(self):
        pygame.quit()
        exit()

