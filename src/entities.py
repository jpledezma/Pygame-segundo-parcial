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
        self.image = self.__select_sprite()
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

    def __select_sprite(self):
        if isinstance(self.spritesheet, SpriteSheet):
            keys_animations = list(self.animations.keys())
            # self.groups_animations = list(self.animations.values())
            image = self.animations[keys_animations[3]][4]
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

        self.speed = 1

    def update(self):
        keys = pygame.key.get_pressed() # esto devuelve una lista de 256 True o False, dependiendo de las teclas que se presionen

        for key in keys:
            if key:
                break
            self.selected_animation = 'idle'

        if keys[K_d] and self.rect.right <= SCREEN_WIDTH:
            self.rect.x += self.speed
            self.selected_animation = 'run'

        if keys[K_a] and self.rect.left >= 0:
            self.rect.x -= self.speed
            self.selected_animation = 'run'

        if keys[K_w] and self.rect.top >= 0:
            self.rect.y -= self.speed
            self.selected_animation = 'run'

        if keys[K_s] and self.rect.bottom <= SCREEN_HEIGHT:
            self.rect.y += self.speed
            self.selected_animation = 'death'

        if keys[K_j] and self.rect.top >= 0:
            self.selected_animation = 'at1'
        if keys[K_k] and self.rect.top >= 0:
            self.selected_animation = 'block_idle'


        self.update_frame(pygame.time.get_ticks(), len(self.animations[self.selected_animation]) - 1, self.selected_animation)

    def update_frame(self, current_time, last_frame, key_animation):
        if current_time - self.last_update >= self.frame_span:
            self.current_sprite += 1
            if self.current_sprite > last_frame:
                self.current_sprite = 0
            self.image = self.animations[key_animation][self.current_sprite]
            self.last_update = current_time