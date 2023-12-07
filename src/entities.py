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
        self.rect = self.image.get_rect( center = position )
        self.selected_animation = "idle"
        self.facing = 'f'
        self.current_attack = 1

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
        self.falling = True

    def update(self, keydown_keys: list):
        
        self.move(keydown_keys)
        self.attack(keydown_keys)
        self.jump(keydown_keys)
        self.fall()
        print(self.falling)
        if keydown_keys == [] and not self.attacking and not self.falling:
            self.selected_animation = "idle"

        
        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.facing][self.selected_animation]) - 1, self.selected_animation)

        

    def update_frame(self, current_time, last_frame, key_animation):
        if current_time - self.last_update >= self.frame_span:
            self.current_sprite += 1
            if self.current_sprite > last_frame:
                self.current_sprite = 0
            self.image = self.animations[self.facing][key_animation][self.current_sprite]
            self.last_update = current_time
            

    def move(self, keys: list):
        if K_a in keys or K_d in keys:
                self.selected_animation = "run"

        if not self.attacking:
            if K_d in keys and self.rect.right <= SCREEN_WIDTH:
                self.rect.x += self.speed
                if self.facing == 'b':
                    self.facing = 'f'

            if K_a in keys and self.rect.left >= 0:
                self.rect.x -= self.speed
                if self.facing == 'f':
                    self.facing = 'b'

            if K_a in keys and K_d in keys:
                keys.remove(K_d) if keys.index(K_d) < keys.index(K_a) else keys.remove(K_a)

            



    def attack(self, keys: list):
        if K_j in keys:
            keys.remove(K_j)
            if self.attacking and self.current_attack < 3:
                self.current_attack += 1 
            else:
                self.current_attack = 1
            self.attacking = True
            self.current_sprite = 0

        if self.attacking:
            self.selected_animation = f"at{self.current_attack}"
            if self.current_sprite >= len(self.animations[self.facing][self.selected_animation]) - 1:
                self.attacking = False
                self.current_attack = 1

    def jump(self, keys: list):

        if K_SPACE in keys and not self.falling:
            self.selected_animation = "jump"

            if not self.attacking:
                self.rect.y -= self.speed
        else:
            self.falling = True

    def fall(self):
        if self.rect.bottom < SCREEN_HEIGHT and self.falling:
            self.rect.y += self.speed
            self.selected_animation = 'fall'
        else:
            self.falling = False