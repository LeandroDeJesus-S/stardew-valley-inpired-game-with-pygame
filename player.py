from pygame import *
from pygame.math import Vector2
from settings import *
import os
from os.path import join
from support import *
from timer import Timer
from re import sub


class Player(sprite.Sprite):
    def __init__(self, pos, *groups) -> None:
        super().__init__(*groups)
        # animations
        self.animations_dir = 'graphics/character'
        self.animations = self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        self.animation_speed = 4

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.z = LAYERS['main']
        
        # movement 
        self._direction = Vector2()
        self.pos = Vector2(self.rect.center)
        self.speed = 100

        # tools
        self.tools = ['hoe', 'water', 'axe']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # timer
        self.timers = {
            'tool_use': Timer(600, self.use_tool),
            'tool_change': Timer(600),
            'seed_use': Timer(600, self.use_seed),
            'seed_change': Timer(600),
        }
    
    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, value):
        self._direction = value
        if not isinstance(self._direction, Vector2):
            return
        
        if self._direction.magnitude() != 0:
            self._direction = self._direction.normalize()

    def inputs(self):
        if self.timers['tool_use'].active:
            return
        
        keys = key.get_pressed()
        # directions
        x = int(keys[K_d]) - int(keys[K_a])
        y = int(keys[K_s]) - int(keys[K_w])

        self.direction = Vector2(x, y)

        # tool use
        if keys[K_SPACE]:
            self.timers['tool_use'].activate()
            self.direction = Vector2()
            self.frame_index = 0
        
        # tool changing
        if keys[K_e] and not self.timers['tool_change'].active:
            self.timers['tool_change'].activate()
            self.tool_index += 1
            if self.tool_index >= len(self.tools):
                self.tool_index = 0
                
            self.selected_tool = self.tools[self.tool_index]
        
        # seed use
        if keys[K_LCTRL]:
            self.timers['seed_use'].activate()
            self.direction = Vector2()
            self.frame_index = 0
        
        # seed changing
        if keys[K_q] and not self.timers['seed_change'].active:
            self.timers['seed_change'].activate()
            self.seed_index += 1
            if self.seed_index >= len(self.seeds):
                self.seed_index = 0

            self.selected_seed = self.seeds[self.seed_index]

    def get_status(self):
        if self.timers['tool_use'].active:
            self.status = sub(r'_\w+$', '', self.status) + f'_{self.selected_tool}'
            return

        if self.direction.x > 0: self.status = 'right'
        elif self.direction.x < 0: self.status = 'left'
        elif self.direction.y > 0: self.status = 'down'
        elif self.direction.y < 0: self.status = 'up'
        elif self.direction.magnitude() == 0:
            self.status = sub(r'_\w+$', '', self.status) + '_idle'
    
    def move(self, dt):
        self.pos.x += self.direction.x * self.speed * dt
        self.pos.y += self.direction.y * self.speed * dt

        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y
    
    def import_assets(self):
        animations = dict(map(lambda ad: (ad, []), os.listdir(self.animations_dir)))
        
        f = lambda k: animations[k].extend(import_folder(join(self.animations_dir, k))[0])
        list(map(f, animations.keys()))

        return animations

    def animate(self, dt):
        frames = self.animations[self.status]
        nframe = len(frames)
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= nframe:
            self.frame_index = 0
        
        self.image = frames[int(self.frame_index)]

    def use_tool(self):
        print('use_tool')
    
    def use_seed(self):
        print('use_seed')
    
    def update_timers(self):
        list(map(lambda t: t.update(), self.timers.values()))

    def update(self, dt):
        self.inputs()
        debug(f'direction: {self.direction}', (20, 20))
        debug(f'tool_use: {self.timers["tool_use"].active}', (20, 40))

        self.get_status()
        debug(f'status: {self.status}', (20, 60))
        
        self.update_timers()
        
        self.move(dt)
        self.animate(dt)
        
