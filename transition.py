from pygame import * 
from settings import *


class Transition:
    def __init__(self, reset, player) -> None:
        self.display_surface = display.get_surface()
        self.reset = reset
        self.player = player

        self.image = Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self, dt):    
        self.color += self.speed
        if self.color <= 0:
            self.speed = 2
            self.color = 0

            self.reset()
            self.player.status = 'right_idle'

        if self.color > 255:
            self.color = 255
            self.speed = -2

            self.player.sleeping = False

        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0,0), special_flags=BLEND_RGBA_MULT)