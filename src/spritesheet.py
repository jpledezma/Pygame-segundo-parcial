# from config import *
import pygame

class SpriteSheet:
    def __init__(self,
                 sheet: pygame.Surface,
                 rows: int,
                 cols: int,
                 sprite_width: int,
                 sprite_height: int,
                 animations_keys: list,
                 animations_frames_number: list,
                 scale: int = 1) -> None:
        
        self.sheet = sheet

        self.rows = rows
        self.cols = cols

        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

        self.animations_keys = animations_keys
        self.animations_frames_number = animations_frames_number
        
        self.scale = scale



    def get_animations(self) -> dict:

        animations = {}
        frames_group = []

        selected_animation = 0
        

        for row in range(self.rows):
            columna = 0
            while columna < self.cols:
                sprite = self.sheet.subsurface((columna * self.sprite_width, row * self.sprite_height, self.sprite_width, self.sprite_height))
                sprite = pygame.transform.scale(sprite, (self.sprite_width * self.scale, self.sprite_height * self.scale))
                if len(frames_group) < self.animations_frames_number[selected_animation]:
                    frames_group.append(sprite)
                    columna += 1
                else:
                    animations[self.animations_keys[selected_animation]] = frames_group
                    selected_animation += 1
                    frames_group = []

        # hay que poner esto para que agregue el ultimo grupo de frames,
        # ya que no va a volver a entrar al else, porque se sale del bucle
        # y frames_group queda en el aire
        animations[self.animations_keys[selected_animation]] = frames_group

        return animations