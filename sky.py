from typing import Any
import pygame
from settings import *
from settings import LAYERS
from support import *
from os.path import join
from sprites import Generic
from random import randint, choice


class Sky:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.full_surface = pygame.Surface(self.display_surface.size)
        self.start_color = [255, 255, 255]
        self.end_color = [38, 101, 189]
        self.speed = -2
    
    def display(self, dt):
        for index, color in enumerate(self.end_color):
            if self.start_color[index] > color:
                self.start_color[index] += self.speed * dt
        
        self.full_surface.fill(self.start_color)
        self.display_surface.blit(self.full_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class RainDrop(Generic):
    def __init__(self, pos, surf, groups, moving, z=...):
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        self.moving = moving
        if moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)
    
    def update(self, dt) -> None:
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = self.pos
        
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.lifetime:
            self.kill()
 

class Rain:
    BASEDIR = 'graphics/rain'
    def __init__(self, all_sprites, floor) -> None:
        self.all_sprites = all_sprites
        self.rain_drops = import_folder(join(self.BASEDIR, 'drops'))[0]
        self.rain_floors = import_folder(join(self.BASEDIR, 'floor'))[0]
        self.floor_w, self.floor_h = floor.image.size
    
    def create_floor(self):
        RainDrop(
            pos=(
                randint(0, self.floor_w),
                randint(0, self.floor_h)
            ),
            surf=choice(self.rain_floors),
            moving=False,
            groups=[self.all_sprites],
            z=LAYERS['rain floor']
        )
    
    def create_drops(self):
        RainDrop(
            pos=(
                randint(0, self.floor_w),
                randint(0, self.floor_h)
            ),
            surf=choice(self.rain_drops),
            moving=True,
            groups=[self.all_sprites],
            z=LAYERS['rain drops']
        )
    
    def update(self):
        self.create_drops()
        self.create_floor()