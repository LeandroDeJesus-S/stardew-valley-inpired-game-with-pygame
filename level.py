from pygame import *
from player import Player
from support import *
from overlay import Overlay
from sprites import Generic
from settings import *


class Level:
    def __init__(self) -> None:
        self.display_surface = display.get_surface()
        self.all_sprites = CameraGroup(self.display_surface)

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        Generic(
            pos=(0, 0), 
            surf=image.load('graphics/world/ground.png').convert_alpha(), 
            groups=(self.all_sprites,),
            z=LAYERS['ground']
        )
        self.player = Player((300, 300), self.all_sprites)

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(sprite.Group):
    def __init__(self, display_surface):
        super().__init__()
        self.display_surface = display_surface
    
    def custom_draw(self, player):
        offset = Vector2(player.rect.center) - Vector2(SCREEN_WIDTH, SCREEN_HEIGHT) / 2
        for sprite in sorted(self.sprites(), key=lambda s: s.z):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= offset
            self.display_surface.blit(sprite.image, offset_rect)
    