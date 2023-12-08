import pygame
from spritesheet import *
from pygame.locals import *
from config import *

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


class Player(Entity):
    def __init__(self, 
                 position: tuple[int, int], 
                 groups,
                 spritesheet,
                 health: int = 1000, 
                 iframes: int = 800,
                 physical_power: int = 40,
                 magic_power: int = 40,
                 cd_parry: int = 1500) -> None:
        super().__init__(position, groups, spritesheet, health, iframes)

        self.speed = 5
        self.speed_v = 5
        self.frame_span = 100

        self.attacking = False
        self.moving = False
        self.falling = False
        self.jumping = False
        self.parry = False
        self.wall_sliding = False
        self.action_list = (self.attacking, self.falling, self.jumping, self.parry, self.wall_sliding)

        self.cd_parry = cd_parry
        self.parry_moment = 0
        self.selected_attack = 0

        self.gravity = 0.2
        self.jump_power = 8

    def update(self, keydown_keys: list):

        self.action_list = (self.attacking, self.falling, self.jumping, self.parry, self.wall_sliding)
        
        self.detect_actions(keydown_keys)
        if keydown_keys == [] and not any(self.action_list):
            self.selected_animation = "idle"

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        if not self.falling and not self.jumping:
            self.speed_v = 0

        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)
        # print(self.jumping, self.falling, self.wall_sliding)
        # print(self.rect.bottom < SCREEN_HEIGHT )
        print(self.health)

    def update_frame(self, current_time, last_frame, key_animation):
        if current_time - self.last_update >= self.frame_span:
            self.current_sprite += 1
            if self.current_sprite > last_frame:
                self.current_sprite = 0
            self.image = self.animations[self.facing][key_animation][self.current_sprite]
            self.last_update = current_time

            
    def detect_actions(self, keys: list):
        # Movimiento horizontal
        move_direction = "None"
        if not self.attacking and not self.parry or self.falling or self.jumping:
            if K_d in keys and self.rect.right <= SCREEN_WIDTH:
                move_direction = "right"
                self.selected_animation = "run"
            if K_a in keys and self.rect.left >= 0:
                move_direction = "left"
                self.selected_animation = "run"
        if K_a in keys and K_d in keys:
            keys.remove(K_d) if keys.index(K_d) < keys.index(K_a) else keys.remove(K_a)

        # Salto
        if K_SPACE in keys and not self.falling:
            keys.remove(K_SPACE)
            if not self.jumping:
                self.jumping = True
                self.speed_v = self.jump_power

        # Ataque
        if K_j in keys:
            keys.remove(K_j)
            self.parry = False
            if self.attacking and self.current_attack < 3:
                self.current_attack += 1 
            else:
                self.current_attack = 1
            self.attacking = True
            self.current_sprite = 0

        # Bloqueo / parry
        if K_k in keys:
            keys.remove(K_k)
            if not self.parry and pygame.time.get_ticks() >= self.parry_moment + self.cd_parry:
                self.parry_moment = pygame.time.get_ticks()
                self.parry = True
                self.current_sprite = 0

        # Caida
        if self.rect.bottom < SCREEN_HEIGHT and not self.wall_sliding and not self.jumping:
            self.falling = True
        else:
            self.falling = False

        # Wall slide
        if (self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH):
            if (self.jumping or self.falling):
                self.wall_sliding = True
        else:
            self.wall_sliding = False

        self.move(move_direction)
        self.jump()
        self.fall()
        self.attack()
        self.block()
        self.wall_slide()

    def move(self, direction: str):
            if direction == "right":
                self.rect.x += self.speed
                self.facing = 'f'
            elif direction == "left":
                self.rect.x -= self.speed
                self.facing = 'b'


    def attack(self):
        if self.attacking:
            self.selected_animation = f"at{self.current_attack}"
            if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
                self.attacking = False
                self.current_attack = 1

    def block(self):
        if self.parry:
            self.selected_animation = "block_idle"
            if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
                self.parry = False

    def jump(self):
        if self.jumping:
            self.wall_sliding = False
            self.selected_animation = "jump"
            self.rect.y -= self.speed_v
            self.speed_v -= self.gravity
            if self.rect.left <= 0:
                self.rect.move_ip(6, 0)
            if self.rect.right >= SCREEN_WIDTH:
                self.rect.move_ip(-6, 0)
            if self.speed_v <= 0:
                self.falling = True
                self.jumping = False

    def fall(self):
        if self.falling:
            self.rect.y += self.speed_v
            self.speed_v += self.gravity
            self.selected_animation = 'fall'
        else:
            self.falling = False

    def wall_slide(self):
        if self.wall_sliding:
            self.selected_animation = "wall_slide"
            self.speed_v = 1
            self.falling = False
            self.jumping = False
            self.rect.y += self.speed_v
