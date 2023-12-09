import pygame
from spritesheet import *
from pygame.locals import *
from config import *
from spritesheet import SpriteSheet

class Entity(pygame.sprite.Sprite):
    def __init__(self,
                 position: tuple[int, int],
                 groups,
                 spritesheet: SpriteSheet,
                 health: int = 1,
                 iframes: int = 500) -> None:
        
        super().__init__(groups)
        
        self.spritesheet = spritesheet

        self.animations_forwards = self.spritesheet.get_animations()
        self.animations_backwards = self.spritesheet.get_animations(flip=True)
        self.animations = {'f': self.animations_forwards, 'b': self.animations_backwards}
        self.image = self.__set_default_sprite()
        self.rect: pygame.Rect = self.image.get_rect( center = position )
        self.selected_animation = "idle"
        self.facing = 'f'
        self.current_attack = 1

        self.__health = health

        self.__hurt_moment = 0
        self.__iframes = iframes
        self.__vulnerable = True
        self.__intangible = False

        self.last_update = pygame.time.get_ticks()
        self.current_sprite = 0
        self.frame_span = 100

    def hurt(self, damage:int):
        if self.__vulnerable and not self.__intangible:
            self.__vulnerable = False
            self.__health -= damage
            self.__hurt_moment = pygame.time.get_ticks()
            print("herido")


    def time_iframes(self, tiempo_actual:int):
        if not self.__vulnerable and tiempo_actual >= self.__hurt_moment + self.__iframes:
            self.__vulnerable = True

    def __set_default_sprite(self):
        if isinstance(self.spritesheet, SpriteSheet):
            keys_animations = list(self.animations['f'].keys())
            # self.groups_animations = list(self.animations.values())
            image = self.animations['f'][keys_animations[0]][0]
            return image


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
                 iframes: int = 500) -> None:
        super().__init__(position, groups, spritesheet, health, iframes)

        self.speed = speed
        self.speed_v = 0
        self.frame_span = 100


class Player(Entity):
    def __init__(self, 
                 position: tuple[int, int], 
                 groups,
                 spritesheet,
                 health: int = 1000, 
                 speed: int = 5,
                 iframes: int = 800,
                 physical_power: int = 40,
                 magic_power: int = 40,
                 cd_parry: int = 1500) -> None:
        super().__init__(position, groups, spritesheet, health, iframes)

        self.speed = speed
        self.speed_v = 0
        self.speed_roll = 7
        self.frame_span = 100

        self.cd_parry = cd_parry
        self.parry_moment = 0
        self.cd_roll = 1500#cd_roll
        self.roll_moment = 0

        self.selected_attack = 0

        self.gravity = 0.2
        self.jump_power = 8

        self.actions = { 
                         'moving': {'flag': False, 'function': self.move},
                         'rolling': {'flag': False, 'function': self.roll},
                         'jumping': {'flag': False, 'function': self.jump},
                         'falling': {'flag': True, 'function': self.fall},
                         'attacking': {'flag': False, 'function': self.attack},
                         'parry': {'flag': False, 'function': self.block},
                         'wall_sliding': {'flag': False, 'function': self.wall_slide}
                       }

    def update(self, keydown_keys: list):
        
        self.detect_actions(keydown_keys)
        if not self.any_action():
            self.selected_animation = "idle"

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

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

            
    def detect_actions(self, keys: list):
        # Movimiento horizontal
        if not self.any_action() or self.actions['falling']['flag'] \
           or self.actions['jumping']['flag'] or self.actions['moving']['flag']:
            
                
            

            if K_d in keys and self.rect.right <= SCREEN_WIDTH:
                self.facing = "f"
                self.actions['moving']['flag'] = True
            elif K_a in keys and self.rect.left >= 0:
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
            if not self.actions['parry']['flag'] and pygame.time.get_ticks() >= self.parry_moment + self.cd_parry:
                self.parry_moment = pygame.time.get_ticks()
                self.actions['parry']['flag'] = True
                self.current_sprite = 0

        # Caida
        if self.rect.bottom < SCREEN_HEIGHT and not self.actions['wall_sliding']['flag'] and not self.actions['jumping']['flag']:
            self.actions['falling']['flag'] = True
        else:
            self.actions['falling']['flag'] = False

        # Wall slide
        if (self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH):
            if (self.actions['jumping']['flag'] or self.actions['falling']['flag']):
                self.actions['wall_sliding']['flag'] = True
        else:
            self.actions['wall_sliding']['flag'] = False

        # Roll
        if K_LSHIFT in keys:
            if (not self.any_action() or self.actions['moving']['flag'] == True) \
                and pygame.time.get_ticks() >= self.roll_moment + self.cd_roll:
                self.roll_moment = pygame.time.get_ticks()
                self.actions['rolling']['flag'] = True
                self.actions['moving']['flag'] = False
                self.intangible = True
                self.current_sprite = 0
                keys.remove(K_LSHIFT)

        # self.move(move_direction)

        for action in self.actions.values():
            if action['flag']:
                action['function']()

    def move(self, direction: str = ""):
        self.selected_animation = "run"
        # if direction == "right":
        if self.facing == "f":
            self.rect.x += self.speed
            # self.facing = 'f'
        # elif direction == "left":
        if self.facing == "b":
            self.rect.x -= self.speed
            # self.facing = 'b'


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
        self.rect.y -= self.speed_v
        self.speed_v -= self.gravity
        if self.rect.left <= 0:
            self.rect.move_ip(6, 0)
        if self.rect.right >= SCREEN_WIDTH:
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
        if self.rect.left >= 0 and self.rect.right <= SCREEN_WIDTH:
            self.rect.move_ip(self.speed_roll, 0) if self.facing == 'f' else self.rect.move_ip(-self.speed_roll, 0)
        if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
            self.actions['rolling']['flag'] = False
            self.intangible = False

    def any_action(self) -> bool:
        flag = False
        for action in self.actions.values():
            if action['flag']:
                flag = True
                break

        return flag