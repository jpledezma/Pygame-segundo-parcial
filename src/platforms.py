import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self,
                 image: pygame.Surface,
                 rect: tuple,
                 groups,
                 hitbox_scale: tuple = (1, 1)) -> None:
        
        super().__init__(groups)
        
        self.image = image
        self.rect = pygame.Rect(*rect)
        
    def draw_rect(self, surface: pygame.Surface, color: tuple):
        pygame.draw.rect(surface, color, self.rect, 1)
