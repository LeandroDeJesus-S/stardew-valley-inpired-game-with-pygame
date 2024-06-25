from pygame import *
from settings import *


class Generic(sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(*groups)
        self.pos = pos
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z