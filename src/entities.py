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

        self.animations = self.spritesheet.get_animations()
        self.image = self.__set_default_sprite()
        self.rect = self.image.get_rect( center = position )
        self.selected_animation = "idle"

        self.__health = health

        self.__hurt_time = 0
        self.__iframes = iframes
        self.__vulnerable = True
        self.__intangible = False

        self.last_update = pygame.time.get_ticks()
        self.current_sprite = 0
        self.frame_span = 100

    def herir(self, intensidad:int):
        if self.__vulnerable and not self.__intangible:
            self.__vulnerable = False
            self.__health -= intensidad
            self.__hurt_time = pygame.time.get_ticks()
            print("herido")


    def cronometrar_iframes(self, tiempo_actual:int):
        if not self.__vulnerable and tiempo_actual >= self.__hurt_time + self.__iframes:
            self.__vulnerable = True
        # if not self.__vulnerable:
        #     print(self.__health)

    def __set_default_sprite(self):
        if isinstance(self.spritesheet, SpriteSheet):
            keys_animations = list(self.animations.keys())
            # self.groups_animations = list(self.animations.values())
            image = self.animations[keys_animations[0]][0]
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
                 path_image: str, 
                 position: tuple[int, int], 
                 health: int = 1000, 
                 iframes: int = 800,
                 physical_power: int = 40,
                 magic_power: int = 40,
                 cd_attack: int = 200) -> None:
        super().__init__(path_image, position, health, iframes)

        self.speed = 5
        self.frame_span = 100

        self.selected_attack = 0
        self.attacking = False
        self.moving = False
        self.falling = False

    def update(self, pressed_keys:pygame.key.ScancodeWrapper, keydown_keys: list):
        
        # if not (pressed_keys[K_w] or pressed_keys[K_a] or pressed_keys[K_s] or pressed_keys[K_d] or pressed_keys[K_j] or pressed_keys[K_j]):
        #     self.selected_animation = 'idle'

        self.move(pressed_keys)
        self.attack(keydown_keys)

        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.selected_animation]) - 1, self.selected_animation)

        

    def update_frame(self, current_time, last_frame, key_animation):
        if current_time - self.last_update >= self.frame_span:
            self.current_sprite += 1
            if self.current_sprite > last_frame:
                self.current_sprite = 0
            self.image = self.animations[key_animation][self.current_sprite]
            self.last_update = current_time
            

        print(len(self.animations[self.selected_animation]), self.current_sprite, (self.selected_animation), self.current_sprite >= len(self.animations[self.selected_animation]) - 4)
        # print(self.attacking)



    def move(self, keys: pygame.key.ScancodeWrapper):

        if keys[K_d] and self.rect.right <= SCREEN_WIDTH:
            self.rect.x += self.speed

        if keys[K_a] and self.rect.left >= 0:
            self.rect.x -= self.speed

        if keys[K_w] and self.rect.top >= 0:
            self.rect.y -= self.speed

        if keys[K_s] and self.rect.bottom <= SCREEN_HEIGHT:
            self.rect.y += self.speed

        if keys[K_w] or keys[K_a] or keys[K_s] or keys[K_d]:
            self.selected_animation = "run"



    def attack(self, keys: list):

        animations = ('at1', 'at2', 'at3')

        # if K_j in keys:
        #     if not self.attacking:
        #         self.current_sprite = 0
        #         self.selected_attack = 0
        #         self.attacking = True

        #     if self.current_sprite >= len(self.animations[self.selected_animation]) -1:
        #         self.selected_attack += 1
        #         self.current_sprite = 0

        #     if self.selected_attack > 2:
        #         self.selected_attack = 0

        #     self.selected_animation = animations[self.selected_attack]

        # else:
        #     self.attacking = False

        if K_j in keys:
            keys.remove(K_j)
            self.attacking = True

        self.play_animation(2)

    def play_animation(self, animation):

        if self.attacking:
            self.current_sprite = 0
            self.selected_animation = "at2"
            self.attacking = False

        if self.current_sprite >= len(self.animations[self.selected_animation]) - 1:
            self.current_sprite = 0
            self.selected_animation = 'idle'
            print("aaaaaaaaaa")


