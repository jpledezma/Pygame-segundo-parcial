import pygame
from pygame.locals import *
from config import *
import os
from level import *
from menus import *
from platforms import Platform

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

        # Plataforma movil del segundo nivel
        path_platform = path.join(getcwd(), "assets", "tiles", "platform.png")
        rect_platform = pygame.Rect(500, 180, 70, 40)
        img_platform = pygame.image.load(path_platform).convert_alpha()
        img_platform = pygame.transform.scale(img_platform, (rect_platform.width, rect_platform.height))
        g = pygame.sprite.Group()
        mobile_platform = Platform(img_platform, rect_platform, [])
        self.mobile_platform = mobile_platform

        self.level_1_data = (self.screen, sprites_data, tile_sets_data[self.maps_data["level_1"]["tileset"]], entities_data, self.maps_data["level_1"])
        self.level_2_data = (self.screen, sprites_data, tile_sets_data[self.maps_data["level_2"]["tileset"]], entities_data, self.maps_data["level_2"])
        self.level_3_data = (self.screen, sprites_data, tile_sets_data[self.maps_data["level_3"]["tileset"]], entities_data, self.maps_data["level_3"])

        self.level_1 = Level(*self.level_1_data)
        self.level_2 = Level(*self.level_2_data, mobile_platform)
        self.level_3 = Level(*self.level_3_data)

        self.main_menu = MainMenu(self.screen)
        self.options_menu = OptionsMenu(self.screen)
        self.pause_menu = PauseMenu(self.screen)
        self.ranking_menu = RankingMenu(self.screen)
        self.selection_menu = SelectionMenu(self.screen)
        self.final_score_menu = FinalScorenMenu(self.screen)

        self.level_1_passed = False
        self.level_2_passed = False
        self.level_3_passed = False

        self.level_2_unlocked = False
        self.level_3_unlocked = False

        self.seconds_left = 0
        self.total_enemies_killed = 0

        self.score = 0

        self.selection = "main_menu"
        self.previous_selection = "main_menu"

        self.active = {
            "lvl1": False,
            "lvl2": False,
            "lvl3": False,
            "main_menu": False,
            "selection": False,
            "ranking": False,
            "pause": False,
            "options": False,
            "final_score": False
            }
            
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            if self.active["main_menu"]:
                # Reiniciar niveles
                self.level_1 = Level(*self.level_1_data)
                self.level_2 = Level(*self.level_2_data, self.mobile_platform)
                self.level_3 = Level(*self.level_3_data)
                self.previous_selection = "main_menu"
                self.selection = self.main_menu.run()

                self.level_1_passed = False
                self.level_2_passed = False
                self.level_3_passed = False
                self.seconds_left = 0
                self.total_enemies_killed = 0
                
            if self.active["selection"]:
                self.selection = self.selection_menu.run()

            if self.active["final_score"]:
                self.selection = self.final_score_menu.run(self.score)

            if self.active["lvl1"]:
                self.previous_selection = "lvl1"
                self.selection = self.level_1.run()
                if not isinstance(self.selection, str):
                    self.level_1 = Level(*self.level_1_data)
                    self.level_1_passed = self.selection[0]
                    self.total_enemies_killed += self.selection[1]
                    self.seconds_left += self.selection[2]

                    self.selection = "selection"

            if self.active["lvl2"]:
                if self.level_2_unlocked:
                    self.previous_selection = "lvl2"
                    self.selection = self.level_2.run()
                    if not isinstance(self.selection, str):
                        self.level_2 = Level(*self.level_2_data, self.mobile_platform)
                        self.level_2_passed = self.selection[0]
                        self.total_enemies_killed += self.selection[1]
                        self.seconds_left += self.selection[2]

                self.selection = "selection"

            if self.active["lvl3"]:
                if self.level_3_unlocked:
                    self.previous_selection = "lvl3"
                    self.selection = self.level_3.run()
                    if not isinstance(self.selection, str):
                        self.level_3 = Level(*self.level_3_data)
                        self.level_3_passed = self.selection[0]
                        self.total_enemies_killed += self.selection[1]
                        self.seconds_left += self.selection[2]
                    
                self.selection = "selection"

                if self.level_2_unlocked and self.level_3_unlocked \
                and self.level_1_passed and self.level_2_passed and self.level_3_passed:
                    self.score = self.total_enemies_killed * 100 + self.seconds_left * 10
                    self.selection = "final_score"
                    print("final score")

            if self.active["pause"]:
                self.selection = self.pause_menu.run(self.previous_selection)

            if self.active["ranking"]:
                self.selection = self.ranking_menu.run()

            if self.active["options"]:
                self.selection  = self.options_menu.run(self.previous_selection)

            for key in self.active:
                self.active[key] = False

            if self.active != None:
                self.active[self.selection] = True

            if self.level_1_passed:
                self.level_2_unlocked = True
            if self.level_2_passed:
                self.level_3_unlocked = True            

            pygame.display.flip()
        
        self.close()
        
    def close(self):
        pygame.quit()

# añadir flags para desbloquear niveles 
# añadir sonidos
# añadir database