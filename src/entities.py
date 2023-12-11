import pygame
from spritesheet import *
from pygame.locals import *
from config import *
from spritesheet import SpriteSheet
from platforms import Platform

class Entity(pygame.sprite.Sprite):
    def __init__(self,
                 position: tuple[int, int],
                 groups,
                 spritesheet: SpriteSheet,
                 health: int = 1,
                 iframes: int = 500,
                 hitbox_scale: tuple = (1, 1)) -> None:
        
        super().__init__(groups)
        
        self.spritesheet = spritesheet

        self.animations_forwards = self.spritesheet.get_animations()
        self.animations_backwards = self.spritesheet.get_animations(flip=True)
        self.animations = {'f': self.animations_forwards, 'b': self.animations_backwards}
        self.image = self.__set_default_sprite()

        self.selected_animation = "idle"
        self.facing = 'f'
        self.rect: pygame.Rect = self.image.get_rect( center = position )

        self.hitbox = pygame.Rect(*self.rect.topleft, self.rect.width * hitbox_scale[0], self.rect.height * hitbox_scale[1])

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
        self.hitbox.midbottom = self.rect.midbottom

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
        if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
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


class Character(Entity):
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
        super().__init__(position, groups, spritesheet, health, iframes, hitbox_scale)

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

        # if self.hitbox.bottom > SCREEN_HEIGHT:
        #     self.rect.bottom = SCREEN_HEIGHT

        if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
            self.speed_v = 0
        
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

    def detect_actions(self, platforms_list):
        # Movimiento horizontal
        if self.hitbox.right >= SCREEN_WIDTH:
            self.facing = "b"
        elif self.hitbox.left <= 0:
            self.facing = "f"
        self.actions['moving']['flag'] = True

        # Caida
        if self.hitbox.bottom < SCREEN_HEIGHT and not self.actions['jumping']['flag']:
            self.actions['falling']['flag'] = True
        else:
            self.actions['falling']['flag'] = False

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


class NightBorne(Character):
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

        self.hitbox = pygame.Rect(*self.rect.topleft, self.rect.width * hitbox_scale[0], self.rect.height * hitbox_scale[1])
        self.fix_coefficient = 0.15

    def update(self):
        self.hitbox.midbottom = (self.rect.midbottom[0], self.rect.height * self.fix_coefficient)
        self.hitbox.midbottom = (self.rect.midbottom[0], self.rect.midbottom[1] - self.rect.height * self.fix_coefficient)
        
        if not self.any_action():
            self.selected_animation = "idle"

        if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
            self.speed_v = 0
        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)

    def fall(self):
        self.selected_animation = 'run'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

class EvilWizard(Character):
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

        self.hitbox = pygame.Rect(*self.rect.topleft, self.rect.width * hitbox_scale[0], self.rect.height * hitbox_scale[1])
        self.fix_coefficient = 0.3

    def update(self):
        self.hitbox.midbottom = (self.rect.midbottom[0], self.rect.midbottom[1] - self.rect.height * self.fix_coefficient)
        
        if not self.any_action():
            self.selected_animation = "idle"

        if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
            self.speed_v = 0
        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)

    def fall(self):
        self.selected_animation = 'run'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity


class BringerOfDeath(Character):
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

        self.hitbox = pygame.Rect(*self.rect.topleft, self.rect.width * hitbox_scale[0], self.rect.height * hitbox_scale[1])
        self.fix_coefficient = 0.225

    def update(self):
        if self.facing == "f":
            self.hitbox.midbottom = (self.rect.midbottom[0] - self.rect.width * self.fix_coefficient, self.rect.midbottom[1])
        else:
            self.hitbox.midbottom = (self.rect.midbottom[0] + self.rect.width * self.fix_coefficient, self.rect.midbottom[1])
        
        if not self.any_action():
            self.selected_animation = "idle"

        if not self.actions['falling']['flag'] and not self.actions['jumping']['flag']:
            self.speed_v = 0
        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)

    def fall(self):
        self.selected_animation = 'run'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

class ShurikenDude(Character):
    def __init__(self, position: tuple[int, int], groups, spritesheet: SpriteSheet, health: int = 200, speed: int = 5, physical_power: int = 40, jump_power: int = 5, iframes: int = 500, gravity: float = 0.2, hitbox_scale: tuple = (1, 1)) -> None:
        super().__init__(position, groups, spritesheet, health, speed, physical_power, jump_power, iframes, gravity, hitbox_scale)
        
        self.hitbox = pygame.Rect(*self.rect.topleft, self.rect.width * hitbox_scale[0], self.rect.height * hitbox_scale[1])
        self.fix_coefficient = 0.225

    def fall(self):
        self.selected_animation = 'idle'
        self.rect.y += self.speed_v
        self.speed_v += self.gravity

    def move(self):
        self.selected_animation = 'idle'


class Player(Character):
    def __init__(self,
                 position: tuple[int, int],
                 groups,
                 spritesheet: SpriteSheet,
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
                 hitbox_scale: tuple = (1, 1)
                ) -> None:
        super().__init__(position, groups, spritesheet, health, speed, physical_power, jump_power, iframes, gravity, hitbox_scale)

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

        # Wall slide
        if (self.hitbox.left <= 0 or self.hitbox.right >= SCREEN_WIDTH):
            if (self.actions['jumping']['flag'] or self.actions['falling']['flag']):
                self.actions['wall_sliding']['flag'] = True
        else:
            self.actions['wall_sliding']['flag'] = False

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
        
        for platform in platforms_list:
            if self.detect_horizontal_collision(platform):
                self.actions['moving']['flag'] = False
                self.actions['rolling']['flag'] = False
            if self.detect_top_platform_collision(platform):
                self.actions['falling']['flag'] = False
                self.speed_v = 0
                self.rect.bottom = platform.rect.top
            elif self.detect_bottom_platform_collision(platform):
                self.speed_v = 0
                self.actions['jumping']['flag'] = False
                self.actions['falling']['flag'] = True

        print(self.speed_v)

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
        if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
            self.actions['attacking']['flag'] = False
            self.current_attack = 1

    def block(self):
        self.selected_animation = "block_idle"
        if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
            self.actions['parry']['flag'] = False

    def jump(self):
        self.selected_animation = "jump"
        self.actions['wall_sliding']['flag'] = False
        self.actions['rolling']['flag'] = False
        self.rect.y -= self.speed_v
        self.speed_v -= self.gravity
        if self.hitbox.left <= 0:
            self.rect.move_ip(6, 0)
        if self.hitbox.right >= SCREEN_WIDTH:
            self.rect.move_ip(-6, 0)
        if self.speed_v <= 0:
            self.actions['falling']['flag'] = True
            self.actions['jumping']['flag'] = False

    def fall(self):
        self.selected_animation = 'fall'
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
        if self.hitbox.left >= 0 and self.hitbox.right <= SCREEN_WIDTH: # Solucionar esto
            self.rect.move_ip(self.speed_roll, 0) if self.facing == 'f' else self.rect.move_ip(-self.speed_roll, 0)
        if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
            self.actions['rolling']['flag'] = False
            self.intangible = False

    def detect_horizontal_collision(self, platform: Platform):
        if platform.rect.colliderect((self.hitbox.x + self.speed, self.hitbox.y, self.hitbox.width, self.hitbox.height)) and\
        self.actions['moving']['flag'] and self.facing == 'f' and not platform.rect.colliderect(self.hitbox) or \
        platform.rect.colliderect((self.hitbox.x - self.speed, self.hitbox.y, self.hitbox.width, self.hitbox.height)) and\
        self.actions['moving']['flag'] and self.facing == 'b' and not platform.rect.colliderect(self.hitbox):
            return True
        else:
            return False
        
    def detect_top_platform_collision(self, platform: Platform):
        if platform.rect.colliderect((self.hitbox.x, self.hitbox.y + self.speed_v, self.hitbox.width, self.hitbox.height)) and \
        not self.actions['jumping']['flag']:
            return True
        else:
            return False
        
    def detect_bottom_platform_collision(self, platform: Platform):
        if platform.rect.colliderect((self.hitbox.x, self.hitbox.y - self.speed_v, self.hitbox.width, self.hitbox.height)) and \
        self.actions['jumping']['flag']:
            return True
        else:
            return False