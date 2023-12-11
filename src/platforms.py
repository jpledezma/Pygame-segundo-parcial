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

        self.hitbox = pygame.Rect(*self.rect.topleft, self.rect.width * hitbox_scale[0], self.rect.height * hitbox_scale[1])

    def update(self, _):
        self.hitbox.midbottom = self.rect.midbottom
        
    def draw_rect(self, surface: pygame.Surface, color: tuple):
        pygame.draw.rect(surface, color, self.hitbox, 2)
        pygame.draw.rect(surface, color, self.rect, 2)
