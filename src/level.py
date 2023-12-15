import pygame
import os
from pygame.locals import *
from config import *
from entities import *
from platforms import *
from utils import *
from hud import *

class Level():
    def __init__(self, screen: pygame.Surface, 
                 spritesheets_data: dict, 
                 tileset_data: dict, 
                 entities_data: dict, 
                 map_data: dict,
                 mobile_platform: Platform = None
                 ) -> None:

        self.clock = pygame.time.Clock()

        self.screen = screen
        self.hud = HUD()

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
        if mobile_platform:
            self.platforms.add(mobile_platform)
            self.all_sprites.add(mobile_platform)
            self.mobile_platform_facing = "f"
        self.mobile_platform = mobile_platform

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

        self.enemies_killed = 0
        self.keys_collected = 0
        self.timer = 60

        self.player_max_hp = self.player.health

        self.timer_count = FPS

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
                    if event.key == K_p or event.key == K_ESCAPE:
                        return "pause"
                if event.type == KEYUP:
                    if event.key in self.keydown_keys:
                        self.keydown_keys.remove(event.key)

            # Añadir al jefe final
            if self.enemies.sprites() == [] and self.final_boss_flag:
                self.all_sprites.add(self.final_boss)
                self.enemies.add(self.final_boss)
                self.entities.add(self.final_boss)
                self.final_boss_flag = False

            if not self.enemies and not self.final_boss_group:
                return (0, 0)
            
            # Perder si se muere el player
            if not self.player_group:
                return (0, 0)

            self.update()
            self.draw()


    def draw(self):
        for background in self.background_layers:
            self.screen.blit(background, (0, 0))

        self.all_sprites.draw(self.screen)
        self.hud.draw(self.screen, self.timer, self.enemies_killed, 17, self.player.health, self.player_max_hp)

        pygame.display.flip()

    def update(self):

        # Acciones del jugador
        self.player.detect_actions(self.platforms.sprites(), self.keydown_keys)
        if self.player.health <= 0:
            self.player.kill()

        # Plataformas moviles
        if self.mobile_platform:
            if self.mobile_platform.rect.left < 300:
                self.mobile_platform_facing = "f"
            if self.mobile_platform.rect.right > 800:
                self.mobile_platform_facing = "b"
            
            if self.mobile_platform_facing == "f":
                self.mobile_platform.rect.centerx += 1
            else:
                self.mobile_platform.rect.centerx -= 1
        

        # Medir los iframes de las entidades y eliminarlas si se salen de la pantalla
        for entity in self.entities:
            entity.time_iframes(pygame.time.get_ticks())
            if entity.rect.top > SCREEN_HEIGHT or entity.rect.bottom < 0 \
            or entity.rect.left > SCREEN_WIDTH or entity.rect.right < 0:
                entity.kill()
                print("mi planeta me necesita")

        # Eliminar los proyectiles que colisionen con plataformas
        for projectile in self.projectiles:
            for platform in self.platforms:
                if projectile.rect.colliderect(platform.rect):
                    projectile.kill()
                    continue

        # Proyectiles de los enemigos
        for projectile in self.enemy_projectiles:
            if self.player.hitbox.colliderect(projectile.rect):
                self.player.hurt(projectile.physical_power)
                if not self.player.intangible:
                    projectile.kill()
            if self.player.block_hitbox.colliderect(projectile.rect):
                projectile.facing = "f" if projectile.facing == "b" else "b"
                self.player_projectiles.add(projectile)
                self.enemy_projectiles.remove(projectile)

        # Acciones de los enemigos
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
                shuriken_img = pygame.image.load(self.spritesheets_data["shuriken"]["path"]).convert_alpha()
                shuriken_spritesheet = SpriteSheet(shuriken_img, *list(self.spritesheets_data["shuriken"].values())[1:])
                Projectile((self.all_sprites, self.entities, self.projectiles, self.enemy_projectiles), shuriken_spritesheet, enemy.rect.center, enemy.facing, *self.entities_data["shuriken"].values())

            # Eliminar al enemigo
            if enemy.health <= 0:
                enemy.kill()
                self.enemies_killed += 1

            self.timer_count -= 1
            if self.timer_count <= 0:
                self.timer_count = FPS * 8
                self.timer -= 1

            if self.timer <= 0:
                self.player.kill()

        self.all_sprites.update()

    def close(self):
        pygame.quit()
        exit()

