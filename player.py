from pygame import *
from pygame.math import Vector2
from settings import *
import os
from os.path import join
from support import *
from timer import Timer
from re import sub


class Player(sprite.Sprite):
    def __init__(self, pos, groups, ground, collision_sprites, tree_sprites, interaction_sprites, soil_layer, toggle_shop) -> None:
        super().__init__(*groups)
        self.ground = ground

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
        self.speed = 200
        self.last_position = None

        
        # collision
        self.hitbox = self.rect.inflate(-120, -70)
        self.collision_sprites = collision_sprites

        # tools
        self.tools = ['hoe', 'water', 'axe']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # interactions
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.soil_layer = soil_layer
        self.sleeping = False

        # inventory
        self.inventory = {
            'wood': 10,
            'apple': 10,
            'corn': 10,
            'tomato': 10,
        }
        self.seed_inventory = {
            'corn': 5,
            'tomato': 5
        }
        self.money = 200

        # trading
        self.toggle_shop = toggle_shop

        # timer
        self.timers = {
            'tool_use': Timer(600, self.use_tool),
            'tool_change': Timer(600),
            'seed_use': Timer(600, self.use_seed),
            'seed_change': Timer(600),
        }

        self.watering_sound = mixer.Sound('audio/water.mp3')
    
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
        if self.timers['tool_use'].active or self.sleeping:
            return
        
        keys = key.get_pressed()
        # directions
        x = int(keys[K_d]) - int(keys[K_a])
        y = int(keys[K_s]) - int(keys[K_w])
        if x != 0 or y != 0:
            self.last_position = self.pos.copy()

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
        
        # restarting day
        if keys[K_RETURN]:
            interactions = sprite.spritecollide(self, self.interaction_sprites, False)
            for interaction in interactions:
                if interaction.name == 'Trader':
                    self.toggle_shop()

                if interaction.name == 'Bed':
                    self.sleeping = True

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
        self.pos.x =  max(0, min(self.pos.x, self.ground.image.width))
        self.hitbox.centerx = self.pos.x
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.pos.y = max(0, min(self.pos.y, self.ground.image.height))
        self.hitbox.centery = self.pos.y
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

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

    def get_target_pos(self):
        primary_status = sub(r'_\w+$', '', self.status)
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[primary_status]

    def use_tool(self):
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        
        if self.selected_tool == 'water':
            self.watering_sound.play()
            self.soil_layer.water(self.target_pos)
    
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1
    
    def update_timers(self):
        list(map(lambda t: t.update(), self.timers.values()))

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(self.hitbox):
                is_idle = self.status.endswith('_idle')
                if direction == 'horizontal' and self.direction.x > 0 and not is_idle:
                    self.hitbox.right = sprite.hitbox.left
                
                elif direction == 'horizontal' and self.direction.x < 0 and not is_idle:
                    self.hitbox.left = sprite.hitbox.right
                
                if direction == 'vertical' and self.direction.y > 0 and not is_idle:
                    self.hitbox.bottom = sprite.hitbox.top
                
                elif direction == 'vertical' and self.direction.y < 0 and not is_idle:
                    self.hitbox.top = sprite.hitbox.bottom

                self.rect.center = self.hitbox.center
                self.pos = Vector2(self.hitbox.center)

    def update(self, dt):
        self.inputs()
        # debug(f'direction: {self.direction}', (20, 20))
        # debug(f'tool_use: {self.timers["tool_use"].active}', (20, 40))

        self.get_status()
        # debug(f'status: {self.status}', (20, 60))
        
        self.update_timers()
        self.get_target_pos()
        
        self.move(dt)
        self.animate(dt)
        # debug(f'{self}')
