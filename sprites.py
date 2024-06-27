from random import random, choice, randint
from typing import Any
from timer import Timer
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

class Interaction(Generic):
    def __init__(self, pos, size, groups, name, z=LAYERS['main']):
        surf = Surface(size)
        super().__init__(pos, surf, groups, z)
        self.name = name


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
        

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        self.start_time = time.get_ticks()
        self.duration = duration

        self.mask = mask.from_surface(self.image)
        self.new_surf = self.mask.to_surface()
        self.new_surf.set_colorkey((0,0,0))
        self.image = self.new_surf

    def update(self, dt):
        current_time = time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.kill()


class Tree(Generic):
    def __init__(self, pos, surf, groups, name, add_player_item, z=LAYERS['main']):
        super().__init__(pos, surf, groups, z)
        self.name = name

        self.apple_surf = image.load('graphics/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name]

        self.all_sprites = self.groups()[0]
        self.apple_sprites = sprite.Group()

        self.health = 5
        self._alive = True
        self.stump_surf = image.load(f'graphics/stumps/{name.lower()}.png').convert_alpha()
        self.invul_timer = Timer(200)

        self.add_player_item = add_player_item

        self.create_apple()
    
    def damage(self):
        self.health -= 1
        if len(self.apple_sprites.sprites()):
            random_apple = choice(self.apple_sprites.sprites())
            Particle(random_apple.rect.topleft, random_apple.image, random_apple.groups(), random_apple.z)
            random_apple.kill()
            self.add_player_item('apple')

    def check_death(self):
        if self.health <= 0:
            Particle(self.pos, self.image, self.groups(), self.z)
            self.image = self.stump_surf
            self.rect = self.image.get_frect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, self.rect.height * .6)
            self._alive = False
            qtt = randint(1, 5) if self.name.lower() == 'small' else randint(5, 10)
            self.add_player_item('wood', qtt)

    def create_apple(self):
        for pos in self.apple_pos:
            if random() > .9:
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                Generic(
                    pos=(x, y), 
                    surf=self.apple_surf, 
                    groups=(self.apple_sprites, self.all_sprites), 
                    z=LAYERS['fruit']
                )
    
    def update(self, dt) -> None:
        if self._alive:
            self.check_death()