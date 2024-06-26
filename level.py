from pygame import *
from player import Player
from support import *
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from settings import *
from camera import CameraGroup
from pytmx.util_pygame import load_pygame

class Level:
    def __init__(self) -> None:
        self.display_surface = display.get_surface()

        self.ground = Generic(
            pos=(0, 0), 
            surf=image.load('graphics/world/ground.png').convert_alpha(), 
            groups=(),
            z=LAYERS['ground']
        )

        # groups
        self.all_sprites = CameraGroup(self.display_surface, self.ground)
        self.collision_sprites = sprite.Group()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame('data/map.tmx')

        def create(layers, groups, z=LAYERS['main']):
            def render(layer, groups, z):
                f = lambda t: Generic((t[0]*TILE_SIZE, t[1]*TILE_SIZE), t[2], groups, z)
                tiles = tmx_data.get_layer_by_name(layer).tiles()
                list(map(f, tiles))

            list(map(lambda layer: render(layer, groups, z), layers))

        # house
        create(['HouseFloor', 'HouseFurnitureBottom'], (self.all_sprites,), LAYERS['house bottom'])
        create(['HouseWalls', 'HouseFurnitureTop'], (self.all_sprites,), LAYERS['main'])
        # fence
        create(['Fence'], (self.all_sprites, self.collision_sprites))

        # water
        water_frames = import_folder('graphics/water')[0]
        for x, y, _ in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, (self.all_sprites,))
        
        # Flowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites), obj.name)
        
        self.player = Player((2000, 2000), (self.all_sprites,), self.ground, self.collision_sprites)

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        self.all_sprites.update(dt)

        self.overlay.display()


