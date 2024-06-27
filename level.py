from pygame import *
from player import Player
from support import *
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from settings import *
from camera import CameraGroup
from transition import Transition
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
        self.tree_sprites = sprite.Group()
        self.interaction_sprites = sprite.Group()

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset_day, self.player)

    def player_add_item(self, item, quantity=1):
        self.player.inventory[item] += quantity

    def reset_day(self):
        # apple on trees
        for tree in self.tree_sprites.sprites():
            tree: Tree
            if not tree._alive:
                ...

            if not tree.apple_sprites.sprites():
                tree.create_apple()
            

    def setup(self):
        tmx_data = load_pygame('data/map.tmx')

        def create_layer(layers, groups, z=LAYERS['main']):
            def render(layer, groups, z):
                f = lambda t: Generic((t[0]*TILE_SIZE, t[1]*TILE_SIZE), t[2], groups, z)
                tiles = tmx_data.get_layer_by_name(layer).tiles()
                list(map(f, tiles))

            list(map(lambda layer: render(layer, groups, z), layers))
        
        def create_obj(layers, groups, z=LAYERS['main'], obj=Generic):
            def render(layer, groups, z):
                f = lambda o: obj((o.x, o.y), o.image, groups, z)
                tiles = tmx_data.get_layer_by_name(layer)
                list(map(f, tiles))

            list(map(lambda layer: render(layer, groups, z), layers))

        # house
        create_layer(['HouseFloor', 'HouseFurnitureBottom'], (self.all_sprites,), LAYERS['house bottom'])
        create_layer(['HouseWalls', 'HouseFurnitureTop'], (self.all_sprites,), LAYERS['main'])
        # fence
        create_layer(['Fence'], (self.all_sprites, self.collision_sprites))

        # water
        water_frames = import_folder('graphics/water')[0]
        for x, y, _ in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, (self.all_sprites,))
        
        # Flowers
        create_obj(['Decoration'], (self.all_sprites, self.collision_sprites), obj=WildFlower)
        
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos=(obj.x, obj.y), 
                surf=obj.image, 
                groups=(self.all_sprites, self.collision_sprites, self.tree_sprites), 
                name=obj.name,
                add_player_item=self.player_add_item)
        
        # collision tiles
        create_layer(['Collision'], (self.collision_sprites,))

        # Player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x, obj.y), 
                    groups=(self.all_sprites,), 
                    ground=self.ground, 
                    collision_sprites=self.collision_sprites, 
                    tree_sprites=self.tree_sprites,
                    interaction_sprites=self.interaction_sprites,
                )
            
            if obj.name == 'Bed':
                Interaction(
                    pos=(obj.x, obj.y), 
                    size=(obj.width, obj.height), 
                    groups=(self.interaction_sprites,),
                    name=obj.name,
                )

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        self.all_sprites.update(dt)

        self.overlay.display()

        if self.player.sleeping:
            self.transition.play(dt)
