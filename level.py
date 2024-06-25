from pygame import *
from player import Player
from support import *

class Level:
    def __init__(self) -> None:
        self.display_surface = display.get_surface()
        self.all_sprites = sprite.Group()

        self.setup()

    def setup(self):
        self.player = Player((300, 300), self.all_sprites)

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.draw(self.display_surface)

        self.all_sprites.update(dt)