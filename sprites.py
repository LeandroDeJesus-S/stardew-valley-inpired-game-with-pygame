from typing import Any
from pygame import *
from settings import *
from settings import LAYERS


class Generic(sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(*groups)
        self.pos = pos
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * .2, -self.rect.height * .75)
        self.z = z


class Water(Generic):
    def __init__(self, pos, frames, groups, z=LAYERS['water']):
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 7.5
        super().__init__(pos, self.frames[self.frame_index], groups, z)
    
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]
    
    def update(self, dt) -> None:
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(pos, surf, groups, z)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height*.9)
        

class Tree(Generic):
    def __init__(self, pos, surf, groups, name, z=LAYERS['main']):
        super().__init__(pos, surf, groups, z)
        self.name = name
