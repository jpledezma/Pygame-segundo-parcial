import pygame
from pygame.locals import *
from config import *
import os
from level import *

class Game():
    def __init__(self) -> None:
        pygame.init()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Juego piola")
        pygame.display.set_icon(ICON_IMG)


        self.sprites_data_path = os.path.join(os.getcwd(), "data", "spritesheets.json")
        sprites_data = read_json(self.sprites_data_path)

        self.entities_data_path = os.path.join(os.getcwd(), "data", "entities_attributes.json")
        entities_data = read_json(self.entities_data_path)

        self.tile_sets_data_path = os.path.join(os.getcwd(), "data", "tile_sets.json")
        tile_sets_data = read_json(self.tile_sets_data_path)

        self.maps_data_path = os.path.join(os.getcwd(), "data", "levels.json")
        self.maps_data = read_json(self.maps_data_path)

        self.level_1_data = (self.screen, sprites_data, tile_sets_data[self.maps_data["level_1"]["tileset"]], entities_data, self.maps_data["level_1"])
        self.level_2_data = (self.screen, sprites_data, tile_sets_data[self.maps_data["level_2"]["tileset"]], entities_data, self.maps_data["level_2"])

        self.level_1 = Level(*self.level_1_data)
        self.level_2 = Level(*self.level_2_data)

        

        
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False       
            self.level_1 = Level(*self.level_1_data)
            self.level_2 = Level(*self.level_2_data)
            self.level_1.run()
            self.level_2.run()     
            
        self.close()
        
    def close(self):
        pygame.quit()

