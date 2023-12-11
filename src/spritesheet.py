# from config import *
import pygame
from utils import *

class SpriteSheet():
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



    def get_animations(self, flip: bool = False) -> dict:

        animations = {}
        frames_group = []

        selected_animation = 0
        
        

        for row in range(self.rows):
            col = 0
            while col < self.cols:
                sprite = self.sheet.subsurface((col * self.sprite_width, row * self.sprite_height, self.sprite_width, self.sprite_height))
                sprite = pygame.transform.scale(sprite, (self.sprite_width * self.scale, self.sprite_height * self.scale))
                sprite = sprite.convert_alpha()
                if flip:
                    sprite = pygame.transform.flip(sprite, True, False)
                if len(frames_group) < self.animations_frames_number[selected_animation]:
                    frames_group.append(sprite)
                    col += 1
                else:
                    animations[self.animations_keys[selected_animation]] = frames_group
                    selected_animation += 1
                    frames_group = []

        # hay que poner esto para que agregue el ultimo grupo de frames,
        # ya que no va a volver a entrar al else, porque se sale del bucle
        # y frames_group queda en el aire
        animations[self.animations_keys[selected_animation]] = frames_group

        return animations
    

class Tileset():
    def __init__(self,
                 tileset: pygame.Surface,
                 tile_width: int,
                 tile_height: int,
                 scale: float = 1) -> None:
        
        self.tileset = tileset#.convert_alpha()
        self.tile_width = tile_width
        self.tile_height = tile_height

        self.scale = scale

        self.tileset_width = tileset.get_width()
        self.tileset_height = tileset.get_height()

        self.cols = self.tileset_width // self.tile_width
        self.rows = self.tileset_height // self.tile_height

        self.tiles_list = []

    def slice_tileset(self):
        i = 0
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tileset.subsurface((col * self.tile_width, row * self.tile_height, self.tile_width, self.tile_height))
                tile = pygame.transform.scale(tile, (self.tile_width * self.scale, self.tile_height * self.scale))
                tile = tile.convert_alpha()
                self.tiles_list.append(tile)
                i += 1

        return self.tiles_list
    
    def get_map(self, tile_map: list) -> list:
        self.slice_tileset()
        surfaces_list = []
        rows = len(tile_map)
        cols = len(tile_map[0])

        for row in range(rows):
            for col in range(cols):
                tile = int(tile_map[row][col])
                if tile != -1:
                    surface = self.tiles_list[tile]
                    rect = (col * self.tile_width, row * self.tile_height, self.tile_width, self.tile_height)
                    surfaces_list.append((surface, rect))


        return surfaces_list