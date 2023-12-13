import pygame
from spritesheet import *
from pygame.locals import *
from config import *
from spritesheet import SpriteSheet
from platforms import Platform
from utils import *

class Entity(pygame.sprite.Sprite):
    def __init__(self,
                 groups,
                 spritesheet: SpriteSheet,
                 position: tuple[int, int],
                 health: int = 1,
                 iframes: int = 500,
                 hitbox_scale: tuple = (1, 1),
                 hitbox_offset: list = [0, 0]) -> None:
        
        super().__init__(groups)
        
        self.spritesheet = spritesheet

        self.hitbox_offset = hitbox_offset

        self.animations_forwards = self.spritesheet.get_animations()
        self.animations_backwards = self.spritesheet.get_animations(flip=True)
        self.animations = {'f': self.animations_forwards, 'b': self.animations_backwards}
        self.image = self.__set_default_sprite()

        self.selected_animation = "idle"
        self.facing = 'f'
        self.rect: pygame.Rect = self.image.get_rect(topleft = position)

        self.hitbox = pygame.Rect(self.rect.x + hitbox_offset[0], self.rect.y + hitbox_offset[1], int(self.rect.width * hitbox_scale[0]), int(self.rect.height * hitbox_scale[1]))
        self.rect_diff_x = abs(self.rect.x - self.hitbox.x)
        self.rect_diff_y = abs(self.rect.bottom - self.hitbox.bottom)
        self.hitbox_offset_x_forwards = hitbox_offset[0]
        self.hitbox_offset_x_backwards = (self.rect.width - self.hitbox.width - hitbox_offset[0])

        self.__health = health

        self.__hurt_moment = 0
        self.__iframes = iframes
        self.__vulnerable = True
        self.__intangible = False

        self.last_update = pygame.time.get_ticks()
        self.current_sprite = 0
        self.frame_span = 100

        self.actions = {'hurt': {'flag': False, 'function': self.hurt_animation}}

    def update(self):
        # Actualizar la posicion de la hitbox
        self.hitbox_offset[0] = self.hitbox_offset_x_forwards if self.facing == "f" else self.hitbox_offset_x_backwards
        self.hitbox.x = self.rect.x + self.hitbox_offset[0]
        self.hitbox.y = self.rect.y + self.hitbox_offset[1]

    def hurt(self, damage:int):
        if self.__vulnerable and not self.__intangible:
            self.__vulnerable = False
            self.__health -= damage
            self.__hurt_moment = pygame.time.get_ticks()
            # debería ser 0, pero si lo pongo así se salta el primer frame, así que va -1
            self.current_sprite = -1
            self.actions['hurt']['flag'] = True

    def hurt_animation(self):
        self.selected_animation = "hurt"
        if self.last_sprite():
            self.actions['hurt']['flag'] = False


    def time_iframes(self, tiempo_actual:int):
        if not self.__vulnerable and tiempo_actual >= self.__hurt_moment + self.__iframes:
            self.__vulnerable = True

    def __set_default_sprite(self):
        if isinstance(self.spritesheet, SpriteSheet):
            keys_animations = list(self.animations['f'].keys())
            # self.groups_animations = list(self.animations.values())
            image = self.animations['f'][keys_animations[0]][0]
            return image
        
    def draw_rect(self, surface: pygame.Surface, color: tuple):
        pygame.draw.rect(surface, color, self.hitbox, 2)
        pygame.draw.rect(surface, color, self.rect, 2)

    def last_sprite(self):
        if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
            return True
        return False

    @property
    def health(self):
        return self.__health
    
    @health.setter
    def health(self, value):
        if isinstance(value, (int, float)):
            self.__health = int(value)
    
    @property
    def intangible(self):
        return self.__intangible
    
    @intangible.setter
    def intangible(self, value):
        if isinstance(value, bool):
            self.__intangible = value

class Projectile(Entity):
    def __init__(self, 
                 groups, 
                 spritesheet: SpriteSheet, 
                 position: tuple[int, int], 
                 health: int = 1,
                 speed: int = 1,
                 physical_power: int = 40,
                 iframes: int = 500, 
                 hitbox_scale: tuple = (1, 1), 
                 hitbox_offset: list = [0, 0]) -> None:
        super().__init__(groups, spritesheet, position, health, iframes, hitbox_scale, hitbox_offset)

class Character(Entity):
    def __init__(self, 
                 groups, 
                 spritesheet: SpriteSheet, 
                 position: tuple[int, int], 
                 health: int = 200, 
                 speed: int = 5,
                 physical_power: int = 40,
                 jump_power: int = 5,
                 iframes: int = 500,
                 gravity: float = 0.2,
                 hitbox_scale: tuple = (1, 1),
                 hitbox_offset: tuple = (0, 0)) -> None:
        super().__init__(groups, spritesheet, position, health, iframes, hitbox_scale, hitbox_offset)

        self.speed = speed
        self.speed_v = 0
        self.terminal_velocity = 8
        self.frame_span = 100
        self.physical_power = physical_power
        self.gravity = gravity
        self.jump_power = jump_power

        self.actions = { 
                         'moving': {'flag': False, 'function': self.move},
                         'jumping': {'flag': False, 'function': self.jump},
                         'falling': {'flag': True, 'function': self.fall},
                         'hurt': {'flag': False, 'function': self.hurt_animation}
                       }
        
    def update(self):
        super().update()
        
        if not self.any_action():
            self.selected_animation = "idle"

        if self.speed_v >= self.terminal_velocity:
            self.speed_v = self.terminal_velocity

        # if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
        #     self.speed_v = 0

        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)


    def update_frame(self, current_time, last_frame, key_animation):
        if current_time - self.last_update >= self.frame_span:
            self.current_sprite += 1
            if self.current_sprite > last_frame:
                self.current_sprite = 0
            self.image = self.animations[self.facing][key_animation][self.current_sprite]
            self.last_update = current_time

    def any_action(self, exclude: str = "") -> bool:
        flag = False
        for key, value in self.actions.items():
            if value['flag'] and key != exclude:
                flag = True
                break
        return flag

    def detect_actions(self, platforms_list: list):

        # Colisiones con las plataformas
        for platform in platforms_list:
            if self.detect_horizontal_collision(platform.rect, 5):
                self.actions['moving']['flag'] = False
            if self.detect_top_platform_collision(platform.rect):
                self.rect.bottom = platform.rect.top + self.rect_diff_y - 0
                self.actions['falling']['flag'] = False
                self.speed_v = 0
            elif self.detect_bottom_platform_collision(platform.rect):
                self.speed_v = 0
                self.actions['jumping']['flag'] = False
                self.actions['falling']['flag'] = True

        for platform in platforms_list:
            if not self.actions['jumping']['flag']:
                self.actions['falling']['flag'] = True
            # Si no hay nada abajo del pj, se cae
            if platform.rect.colliderect((self.hitbox.x , self.hitbox.y + 1, self.hitbox.width, self.hitbox.height)):
                self.actions['falling']['flag'] = False
                break

        for action in self.actions.values():
            if action['flag']:
                action['function']()

    def move(self):
        self.selected_animation = "run"
        if self.facing == "f":
            self.rect.x += self.speed
        if self.facing == "b":
            self.rect.x -= self.speed

    def jump(self):
        self.selected_animation = "jump"
        self.rect.y -= self.speed_v
        self.speed_v -= self.gravity
        if self.speed_v <= 0:
            self.actions['falling']['flag'] = True
            self.actions['jumping']['flag'] = False

    def fall(self):
        self.selected_animation = 'fall'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

    def detect_horizontal_collision(self, platform: pygame.Rect, offset: int = 0):
        # Se debería tomar self.speed o self.speed_roll dependiendo de cual sea el más alto
        if platform.colliderect((self.hitbox.x + self.speed + offset, self.hitbox.y, self.hitbox.width, self.hitbox.height)) and\
         self.facing == 'f' and not platform.colliderect(self.hitbox) or \
        platform.colliderect((self.hitbox.x - self.speed - offset, self.hitbox.y, self.hitbox.width, self.hitbox.height)) and\
         self.facing == 'b' and not platform.colliderect(self.hitbox):
            return True
        else:
            return False
        
    def detect_top_platform_collision(self, platform: pygame.Rect, offset: int = 0):
        if platform.colliderect((self.hitbox.x, self.hitbox.y + self.speed_v + offset, self.hitbox.width, self.hitbox.height)) and \
        not self.actions['jumping']['flag']:
            return True
        else:
            return False
        
    def detect_bottom_platform_collision(self, platform: pygame.Rect, offset: int = 0):
        if platform.colliderect((self.hitbox.x, self.hitbox.y - self.speed_v - offset, self.hitbox.width, self.hitbox.height)) and \
        self.actions['jumping']['flag']:
            return True
        else:
            return False

class NightBorne(Character):
    def __init__(self, 
                 groups, 
                 spritesheet: SpriteSheet, 
                 position: tuple[int, int], 
                 health: int = 200, 
                 speed: int = 5, 
                 physical_power: int = 40, 
                 jump_power: int = 5, 
                 iframes: int = 500, 
                 gravity: float = 0.2, 
                 hitbox_scale: tuple = (1, 1),
                 hitbox_offset: tuple = (0, 0)) -> None:
        super().__init__(groups, spritesheet, position, health, speed, physical_power, jump_power, iframes, gravity, hitbox_scale, hitbox_offset)

        self.aggro_distance = 300
        self.frame_span = 70
        self.attack_range_x = self.hitbox.width
        self.attack_range_y = self.hitbox.height + 20
        self.attack_hitbox = pygame.Rect(0, 0, self.attack_range_x, self.attack_range_y)
        self.actions = { 
                         'moving': {'flag': False, 'function': self.move},
                         'jumping': {'flag': False, 'function': self.jump},
                         'falling': {'flag': True, 'function': self.fall},
                         'attacking': {'flag': False, 'function': self.attack},
                         'hurt': {'flag': False, 'function': self.hurt_animation}
                       }


    def update(self):
        super().update()
        if not self.any_action():
            self.selected_animation = "idle"

        if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
            self.speed_v = 0
        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)

    def detect_actions(self, platforms_list, player: Character):
        # Moverse hacia el jugador
        distance_x = get_distance(self.hitbox.centerx, player.hitbox.centerx)
        distance_y = get_distance(self.hitbox.centery, player.hitbox.centery)

        if abs(distance_x) <= self.aggro_distance and abs(distance_y) <= 95:
            self.actions['moving']['flag'] = True
            self.facing = "f" if distance_x <= 0 else "b"
        else:
            self.actions['moving']['flag'] = False

        # Atacar
        if abs(distance_x) <= self.attack_range_x + self.hitbox.width //2 - player.hitbox.width //2 \
        and abs(distance_y) <= 50:
            self.actions['moving']['flag'] = False
            self.actions['attacking']['flag'] = True
            if self.current_sprite >= 8: # Este es el frame en el que baja la espada y ataca
                self.attack_hitbox.width = self.attack_range_x
                self.attack_hitbox.height = self.attack_range_y
                self.attack_hitbox.midbottom = self.hitbox.midbottom
                if self.facing == "f":
                    self.attack_hitbox.left = self.hitbox.centerx
                else:
                    self.attack_hitbox.right = self.hitbox.centerx
            else:
                self.attack_hitbox.width = 0
                self.attack_hitbox.height = 0
        else:
            self.actions['attacking']['flag'] = False
            self.attack_hitbox.width = 0
            self.attack_hitbox.height = 0

        super().detect_actions(platforms_list)

    def fall(self):
        self.selected_animation = 'run'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity
    
    def attack(self):
        self.selected_animation = "attack"
        
class EvilWizard(Character):
    def __init__(self, 
                 groups, 
                 spritesheet: SpriteSheet, 
                 position: tuple[int, int], 
                 health: int = 200, 
                 speed: int = 5, 
                 physical_power: int = 40, 
                 jump_power: int = 5, 
                 iframes: int = 500, 
                 gravity: float = 0.2, 
                 hitbox_scale: tuple = (1, 1),
                 hitbox_offset: tuple = (0, 0)) -> None:
        super().__init__(groups, spritesheet, position, health, speed, physical_power, jump_power, iframes, gravity, hitbox_scale, hitbox_offset)

        self.aggro_distance = 300
        # self.frame_span = 70
        self.attack_range_x = self.hitbox.width + 30
        self.attack_range_y = self.hitbox.height - 10
        self.attack_hitbox = pygame.Rect(0, 0, self.attack_range_x, self.attack_range_y)
        self.actions = { 
                         'moving': {'flag': False, 'function': self.move},
                         'jumping': {'flag': False, 'function': self.jump},
                         'falling': {'flag': True, 'function': self.fall},
                         'attacking': {'flag': False, 'function': self.attack},
                         'hurt': {'flag': False, 'function': self.hurt_animation}
                       }


    def update(self):
        super().update()

        if not self.any_action():
            self.selected_animation = "idle"

        if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
            self.speed_v = 0
        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)

    def detect_actions(self, platforms_list, player: Character):
        # Moverse hacia el jugador
        distance_x = get_distance(self.hitbox.centerx, player.hitbox.centerx)
        distance_y = get_distance(self.hitbox.centery, player.hitbox.centery)

        if abs(distance_x) <= self.aggro_distance and abs(distance_y)<= 95:
            self.actions['moving']['flag'] = True
            self.facing = "f" if distance_x <= 0 else "b"
        else:
            self.actions['moving']['flag'] = False

        # Atacar
        if abs(distance_x) <= self.attack_range_x + self.hitbox.width //2 - player.hitbox.width //2 \
        and abs(distance_y) <= 50:
            self.actions['attacking']['flag'] = True
            self.actions['moving']['flag'] = False
        else:
            self.actions['attacking']['flag'] = False
            self.attack_hitbox.width = 0
            self.attack_hitbox.height = 0

        super().detect_actions(platforms_list)

    def attack(self):
        self.selected_animation = "attack"
        
        self.attack_hitbox.width = self.attack_range_x
        self.attack_hitbox.height = self.attack_range_y
        self.attack_hitbox.midbottom = self.hitbox.midbottom
        if self.facing == "f":
            self.attack_hitbox.left = self.hitbox.centerx
        else:
            self.attack_hitbox.right = self.hitbox.centerx

    def fall(self):
        self.selected_animation = 'run'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

class BringerOfDeath(Character):
    def __init__(self, 
                 groups, 
                 spritesheet: SpriteSheet, 
                 position: tuple[int, int], 
                 health: int = 200, 
                 speed: int = 5, 
                 physical_power: int = 40, 
                 jump_power: int = 5, 
                 iframes: int = 500, 
                 gravity: float = 0.2, 
                 hitbox_scale: tuple = (1, 1),
                 hitbox_offset: tuple = (0, 0)) -> None:
        super().__init__(groups, spritesheet, position, health, speed, physical_power, jump_power, iframes, gravity, hitbox_scale, hitbox_offset)

        self.aggro_distance = 500
        self.attack_range_x = self.hitbox.width + 130
        self.attack_range_y = self.hitbox.height + 30
        self.attack_hitbox = pygame.Rect(0, 0, self.attack_range_x, self.attack_range_y)
        self.sp_attack_hitbox = pygame.Rect(0, 0, 0, 0)
        self.sp_attack_aoe = (40, 70)

        self.flag_begin_attack = True
        self.flag_fix_hitbox = True
        self.previous_facing = self.facing

        self.cd_sp_attack = 3000
        self.sp_attack_moment = 0

        self.actions = { 
                         'moving': {'flag': False, 'function': self.move},
                         'jumping': {'flag': False, 'function': self.jump},
                         'falling': {'flag': True, 'function': self.fall},
                         'attacking': {'flag': False, 'function': self.attack},
                         'sp_attacking': {'flag': False, 'function': self.special_attack},
                         'hurt': {'flag': False, 'function': self.hurt_animation}
                       }


    def update(self):
        super().update()
        if not self.any_action():
            self.selected_animation = "idle"

        if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
            self.speed_v = 0
        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)

    def detect_actions(self, platforms_list, player: Character):
        # Moverse hacia el jugador
        distance_x = get_distance(self.hitbox.centerx, player.hitbox.centerx)
        distance_y = get_distance(self.hitbox.centery, player.hitbox.centery)

        # Mover el sprite en caso de que cambie de direccion
        if self.previous_facing != self.facing:
            self.flag_fix_hitbox = True
            self.previous_facing = self.facing

        if abs(distance_x) <= self.aggro_distance and abs(distance_y) <= 95:
            self.actions['moving']['flag'] = True
            if distance_x <= 0:
                self.facing = "f"
                if self.flag_fix_hitbox:
                    self.rect.centerx += 140
                    self.flag_fix_hitbox = False
            else:
                self.facing = "b"
                if self.flag_fix_hitbox:
                    self.rect.centerx -= 140
                    self.flag_fix_hitbox = False
        else:
            self.actions['moving']['flag'] = False
        
        # Atacar
        if abs(distance_x) <= self.attack_range_x + self.hitbox.width // 2 - player.hitbox.width * 2 \
        and abs(distance_y) <= 50:
            self.actions['moving']['flag'] = False
            self.actions['attacking']['flag'] = True
        else:
            self.actions['attacking']['flag'] = False
            self.attack_hitbox.width = 0
            self.attack_hitbox.height = 0

        # Ataque especial
        if not self.any_action() \
        and pygame.time.get_ticks() >= self.sp_attack_moment + self.cd_sp_attack:
            self.sp_attack_moment = pygame.time.get_ticks()
            self.actions['sp_attacking']['flag'] = True
            self.current_sprite = 0
            self.sp_attack_hitbox.centerx = player.hitbox.centerx - self.sp_attack_aoe[0] //2
            self.sp_attack_hitbox.centery = player.hitbox.centery - self.sp_attack_aoe[1] //2

        if self.actions['sp_attacking']['flag'] and self.current_sprite >= 5:
            self.sp_attack_hitbox.width = self.sp_attack_aoe[0]
            self.sp_attack_hitbox.height = self.sp_attack_aoe[1]
        else:
            self.sp_attack_hitbox.width = 0
            self.sp_attack_hitbox.height = 0


        super().detect_actions(platforms_list)

    def attack(self):
        self.selected_animation = "attack"
        if self.actions['attacking']['flag']:
            if self.current_sprite >= 4 and self.current_sprite <= 7: # Estos son los frames en el que baja la espada y ataca
                self.attack_hitbox.width = self.attack_range_x
                self.attack_hitbox.height = self.attack_range_y
                self.attack_hitbox.midbottom = self.hitbox.midbottom
                if self.facing == "f":
                    self.attack_hitbox.left = self.hitbox.centerx
                else:
                    self.attack_hitbox.right = self.hitbox.centerx
            else:
                self.attack_hitbox.width = 0
                self.attack_hitbox.height = 0
    
    def special_attack(self):
        self.selected_animation = "cast"
        if self.last_sprite():
            self.actions['sp_attacking']['flag'] = False

    def fall(self):
        self.selected_animation = 'run'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

class ShurikenDude(Character):
    def __init__(self, 
                 position: tuple[int, int], 
                 groups, 
                 spritesheet: SpriteSheet, 
                 health: int = 200, 
                 speed: int = 5, 
                 physical_power: int = 40, 
                 jump_power: int = 5, 
                 iframes: int = 500, 
                 gravity: float = 0.2, 
                 hitbox_scale: tuple = (1, 1)) -> None:
        super().__init__(position, groups, spritesheet, health, speed, physical_power, jump_power, iframes, gravity, hitbox_scale)
        
        self.fix_coefficient = 0.225

    def fall(self):
        self.selected_animation = 'idle'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

    def move(self):
        self.selected_animation = 'idle'

class Player(Character):
    def __init__(self,
                 groups,
                 spritesheet: SpriteSheet,
                 position: tuple[int, int],
                 health: int = 200, 
                 speed: int = 5, 
                 physical_power: int = 40,
                 magic_power: int = 40,
                 jump_power: int = 5, 
                 iframes: int = 500, 
                 cd_parry: int = 1500,
                 cd_roll: int = 1500,
                 speed_roll: int = 7,
                 gravity: float = 0.2,
                 hitbox_scale: tuple = (1, 1),
                 hitbox_offset: tuple = (0, 0)
                ) -> None:
        super().__init__(groups, spritesheet, position, health, speed, physical_power, jump_power, iframes, gravity, hitbox_scale, hitbox_offset)

        self.speed_roll = speed_roll
        self.cd_roll = cd_roll
        self.roll_moment = 0

        self.cd_parry = cd_parry
        self.parry_moment = 0

        self.actions = { 
                         'moving': {'flag': False, 'function': self.move},
                         'rolling': {'flag': False, 'function': self.roll},
                         'jumping': {'flag': False, 'function': self.jump},
                         'falling': {'flag': True, 'function': self.fall},
                         'attacking': {'flag': False, 'function': self.attack},
                         'parry': {'flag': False, 'function': self.block},
                         'wall_sliding': {'flag': False, 'function': self.wall_slide},
                         'hurt': {'flag': False, 'function': self.hurt_animation}
                       }
        
    def detect_actions(self, platforms_list, keys: list):
        # Movimiento horizontal
        if not self.any_action() or self.actions['falling']['flag'] \
           or self.actions['jumping']['flag'] or self.actions['moving']['flag']:
            if K_d in keys and self.hitbox.right <= SCREEN_WIDTH:
                self.facing = "f"
                self.actions['moving']['flag'] = True
            elif K_a in keys and self.hitbox.left >= 0:
                self.facing = "b"
                self.actions['moving']['flag'] = True
            else:
                self.actions['moving']['flag'] = False

        if K_a in keys and K_d in keys:
            keys.remove(K_d) if keys.index(K_d) < keys.index(K_a) else keys.remove(K_a)

        # Salto
        if K_SPACE in keys and not self.actions['falling']['flag']:
            keys.remove(K_SPACE)
            if not self.actions['jumping']['flag']:
                self.actions['jumping']['flag'] = True
                self.speed_v = self.jump_power

        # Ataque
        if K_j in keys:
            keys.remove(K_j)
            self.actions['parry']['flag'] = False
            self.actions['moving']['flag'] = False
            self.actions['rolling']['flag'] = False
            if self.actions['attacking']['flag'] and self.current_attack < 3:
                self.current_attack += 1 
            else:
                self.current_attack = 1
            self.actions['attacking']['flag'] = True
            self.current_sprite = 0

        # Bloqueo / parry
        if K_k in keys:
            keys.remove(K_k)
            self.actions['moving']['flag'] = False
            self.actions['rolling']['flag'] = False
            self.actions['attacking']['flag'] = False
            if not self.actions['parry']['flag'] and pygame.time.get_ticks() >= self.parry_moment + self.cd_parry:
                self.parry_moment = pygame.time.get_ticks()
                self.actions['parry']['flag'] = True
                self.current_sprite = 0

        # Roll
        if K_LSHIFT in keys:
            if not self.any_action("moving")  \
                and pygame.time.get_ticks() >= self.roll_moment + self.cd_roll:
                self.roll_moment = pygame.time.get_ticks()
                self.actions['rolling']['flag'] = True
                self.actions['moving']['flag'] = False
                self.intangible = True
                self.current_sprite = 0
                keys.remove(K_LSHIFT)
            if self.actions['wall_sliding']['flag']:
                self.actions['wall_sliding']['flag'] = False
                self.rect.x += 1 if self.facing == "b" else -1
        
        # Detectar colisiones con las plataformas
        for platform in platforms_list:
            if self.detect_horizontal_collision(platform.rect):
                self.actions['moving']['flag'] = False
                self.actions['rolling']['flag'] = False
                # Wall slide
                if self.actions['jumping']['flag'] or self.actions['falling']['flag']:
                    self.actions['wall_sliding']['flag'] = True
            if self.detect_top_platform_collision(platform.rect):
                self.actions['falling']['flag'] = False
                self.speed_v = 0
                self.rect.bottom = platform.rect.top
            elif self.detect_bottom_platform_collision(platform.rect):
                self.speed_v = 0
                self.actions['jumping']['flag'] = False
                self.actions['falling']['flag'] = True

        # Detener el wall slide si no hay ninguna plataforma adyacente al jugador
        if self.actions['wall_sliding']['flag']:
            self.actions['wall_sliding']['flag'] = False
            self.actions['falling']['flag'] = True
            for platform in platforms_list:
                if self.detect_horizontal_collision(platform.rect, 2):
                    self.actions['wall_sliding']['flag'] = True
                    self.actions['falling']['flag'] = False
                    break

        # Detectar colisiones con las plataformas * 2
        for platform in platforms_list:
            if not self.actions['jumping']['flag']:
                self.actions['falling']['flag'] = True
            # Si no hay nada abajo del pj, se cae
            if platform.rect.colliderect((self.hitbox.x , self.hitbox.y + 1, self.hitbox.width, self.hitbox.height)):
                self.actions['falling']['flag'] = False
                break

        # Ejecutar acciones
        for action in self.actions.values():
            if action['flag']:
                action['function']()

    def move(self):
        if self.actions['moving']['flag']:
            self.selected_animation = "run"
            if self.facing == "f":
                self.rect.x += self.speed
            if self.facing == "b":
                self.rect.x -= self.speed

    def attack(self):
        self.selected_animation = f"at{self.current_attack}"
        if self.last_sprite():
            self.actions['attacking']['flag'] = False
            self.current_attack = 1

    def block(self):
        self.selected_animation = "block_idle"
        if self.last_sprite():
            self.actions['parry']['flag'] = False

    def jump(self):
        self.selected_animation = "jump"
        self.actions['rolling']['flag'] = False
        self.rect.y -= self.speed_v
        self.speed_v -= self.gravity
        if self.actions['wall_sliding']['flag']:
            self.actions['wall_sliding']['flag'] = False
            if self.facing == "b":
                self.rect.move_ip(1, 0)
            elif self.facing == "f":
                self.rect.move_ip(-1, 0)
        if self.speed_v <= 0:
            self.actions['falling']['flag'] = True
            self.actions['jumping']['flag'] = False

    def fall(self):
        self.selected_animation = 'fall'
        self.actions['rolling']['flag'] = False
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

    def wall_slide(self):
        self.selected_animation = "wall_slide"
        self.speed_v = 1
        self.actions['falling']['flag'] = False
        self.actions['jumping']['flag'] = False
        self.rect.y += self.speed_v

    def roll(self):
        self.selected_animation = "roll"
        if self.actions['rolling']['flag']:
            self.rect.move_ip(self.speed_roll, 0) if self.facing == 'f' else self.rect.move_ip(-self.speed_roll, 0)
        if self.last_sprite():
            self.actions['rolling']['flag'] = False
            self.intangible = False
