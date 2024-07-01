import pygame
from settings import *
from settings import LAYERS
from support import *
from os.path import join
from pprint import pp
from pytmx.util_pygame import load_pygame
from sprites import Generic
from random import choice


class SoilTile(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, LAYERS['soil'])


class GetSoil:
    def __init__(self, ri, ci, soil_grid) -> None:
        self.soil_grid = soil_grid
        self.t = 'x' in soil_grid[ri - 1][ci]
        self.b = 'x' in soil_grid[ri + 1][ci]
        self.l = 'x' in soil_grid[ri][ci - 1]
        self.r = 'x' in soil_grid[ri][ci + 1]

        self._soil_type = 'o'
        self.set_soil()

    def set_soil(self):
        self.full_centered()
        self.single_horizontal()
        self.single_vertical()
        self.centered_horizontal()
        self.centered_vertical()
        self.on_corner()
        self.t_format()

    def full_centered(self):
        if all((self.t, self.b, self.l, self.r)): self._soil_type = 'x'
    
    def single_horizontal(self):
        if self.l and not any((self.r, self.t, self.b)): self._soil_type = 'r'
        elif self.r and not any((self.l, self.t, self.b)): self._soil_type = 'l'

    def single_vertical(self): 
        if self.t and not any((self.b, self.l, self.r)): self._soil_type = 'b'
        elif self.b and not any((self.t, self.l, self.r)): self._soil_type = 't'

    def centered_horizontal(self):
        if all((self.l, self.r)) and not any((self.t, self.b)): self._soil_type = 'lr'
    
    def centered_vertical(self):
        if all((self.t, self.b)) and not any((self.r, self.l)): self._soil_type = 'tb'

    def on_corner(self):
        if all((self.t, self.l)) and not any((self.b, self.r)): self._soil_type = 'br'
        elif all((self.b, self.l)) and not any((self.t, self.r)): self._soil_type = 'tr'
        elif all((self.t, self.r)) and not any((self.b, self.l)): self._soil_type = 'bl'
        elif all((self.b, self.r)) and not any((self.t, self.l)): self._soil_type = 'tl'

    def t_format(self):
        if all((self.t, self.l, self.r)) and not self.b: self._soil_type = 'lrb'
        elif all((self.b, self.l, self.r)) and not self.t: self._soil_type = 'lrt'
        elif all((self.t, self.b, self.r)) and not self.l: self._soil_type = 'tbr'
        elif all((self.b, self.t, self.l)) and not self.r: self._soil_type = 'tbl'

    @property
    def soil(self):
        return self._soil_type


class WaterLayer(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, LAYERS['soil water'])


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, soil, groups, check_watered):
        super().__init__(*groups)
        self.plant_type = plant_type
        self.soil = soil
        self.frames = import_folder(f'graphics/fruit/{plant_type}')[0]
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]

        self.image = self.frames[self.age]
        self.y_offset = pygame.math.Vector2(0, -16 if plant_type == 'corn' else -8)
        self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + self.y_offset)
        self.z = LAYERS['ground plant']

        self.check_watered = check_watered
        self.harvestable = False
    
    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * .4)

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + self.y_offset)


class SoilLayer:
    SOIL_DIR = 'graphics/soil'
    def __init__(self, all_sprites, ground, raining, collision_sprites) -> None:
        self.ground = ground
        self.farmable_tiles = load_pygame('data/map.tmx').get_layer_by_name('Farmable').tiles()
        # groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        self.collision_sprites = collision_sprites

        # graphics
        self.soil_surfs = import_files_dict(self.SOIL_DIR)
        self.water_surfs = import_folder('graphics/soil_water')[0]

        # sound
        self.hoe_sound = pygame.mixer.Sound('audio/hoe.wav')
        self.hoe_sound.set_volume(.1)

        self.plant_sound = pygame.mixer.Sound('audio/plant.wav')

        self.raining = raining
        
        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        h_tiles = self.ground.image.width // TILE_SIZE
        v_tiles = self.ground.image.height // TILE_SIZE

        self.grid = [[[] for _ in range(h_tiles)] for _ in range(v_tiles)]
        list(map(lambda t: self.grid[t[1]][t[0]].append('F'), self.farmable_tiles))

    def create_hit_rects(self):
        self.hit_rects = []
        for row_idx, row in enumerate(self.grid):
            for col_idx, col in enumerate(row):
                if 'F' not in col: continue

                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                self.hit_rects.append(rect)
    
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for row_idx, row in enumerate(self.grid):
            for col_idx, col in enumerate(row):
                if 'x' in col:                    
                    soil_type = GetSoil(row_idx, col_idx, self.grid).soil

                    x = col_idx * TILE_SIZE
                    y = row_idx * TILE_SIZE
                    SoilTile((x, y), self.soil_surfs[soil_type], [self.all_sprites, self.soil_sprites,])

    def get_hit(self, point):
        for rect in self.hit_rects:
            x = rect.x // TILE_SIZE
            y = rect.y // TILE_SIZE
            if 'F' in self.grid[y][x] and rect.collidepoint(point):
                self.hoe_sound.play()
                self.grid[y][x].append('x')
                self.create_soil_tiles()
                if self.raining:
                    self.water_all()

    def water(self, point):
        for sprite in self.soil_sprites.sprites():
            x = int(sprite.rect.x / TILE_SIZE)
            y = int(sprite.rect.y / TILE_SIZE)
            if 'w' not in self.grid[y][x] and sprite.rect.collidepoint(point):
                self.grid[y][x].append('w')

                water_surf = choice(self.water_surfs)
                WaterLayer(sprite.rect.topleft, water_surf, [self.all_sprites, self.water_sprites])
    
    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'w' in cell:
                    cell.remove('w')

    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        return 'w' in cell

    def plant_seed(self, target_pos, selected_seed):
        for sprite in self.soil_sprites.sprites():
            if sprite.rect.collidepoint(target_pos):
                x = int(sprite.rect.x / TILE_SIZE)
                y = int(sprite.rect.y / TILE_SIZE)
                if 'p' not in self.grid[y][x]:
                    self.plant_sound.play()
                    self.grid[y][x].append('p')
                    Plant(selected_seed, sprite, [self.all_sprites, self.plant_sprites, self.collision_sprites], self.check_watered)

    def water_all(self):
        for ri, row in enumerate(self.grid):
            for ci, cell in enumerate(row):
                if 'x' in cell and 'w' not in cell:
                    cell.append('w')

                    x, y = ci * TILE_SIZE, ri * TILE_SIZE
                    water_surf = choice(self.water_surfs)
                    WaterLayer((x,y), water_surf, [self.all_sprites, self.water_sprites])

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()





