from pygame import *
from player import Player
from support import *
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from settings import *
from camera import CameraGroup
from transition import Transition
from pytmx.util_pygame import load_pygame
from soil import SoilLayer
from sky import Rain, Sky
from menu import Menu
from random import uniform


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

        self.rain = Rain(self.all_sprites, self.ground)
        self.raining = False
        self.sky = Sky()
        self.soil_layer = SoilLayer(self.all_sprites, self.ground, self.raining, self.collision_sprites)

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset_day, self.player)

        self.success_sound = mixer.Sound('audio/success.wav')

        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)

        self.bg_music = mixer.Sound('audio/music.mp3')
        self.bg_music.play(-1)

    def player_add_item(self, item, quantity=1):
        self.player.inventory[item] += quantity
        self.success_sound.play()

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def plant_collision(self):
        """colher"""
        if not self.soil_layer.plant_sprites: return

        for plant in self.soil_layer.plant_sprites.sprites():
            if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                self.player_add_item(plant.plant_type)
                Particle(plant.rect.topleft, plant.image, [self.all_sprites], plant.z)

                x = int(plant.rect.centerx / TILE_SIZE)
                y = int(plant.rect.centery / TILE_SIZE)
                if 'p' in self.soil_layer.grid[y][x]:
                    self.soil_layer.grid[y][x].remove('p')

                plant.kill()

    def reset_day(self):
        # plants
        self.soil_layer.update_plants()

        # watered soil
        self.soil_layer.remove_water()

        self.raining = uniform(0, 1) < 0.1
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # apple on trees
        for tree in self.tree_sprites.sprites():
            tree: Tree
            if not tree._alive:
                tree.reset_tree()

            elif not tree.apple_sprites.sprites():
                tree.create_apple()
        
        # restart daytime
        self.sky.start_color = [255, 255, 255]
        
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
                    soil_layer = self.soil_layer,
                    toggle_shop=self.toggle_shop
                )
            
            if obj.name == 'Bed':
                Interaction(
                    pos=(obj.x, obj.y), 
                    size=(obj.width, obj.height), 
                    groups=(self.interaction_sprites,),
                    name=obj.name,
                )
            
            if obj.name == 'Trader':
                Interaction(
                    pos=(obj.x, obj.y), 
                    size=(obj.width, obj.height), 
                    groups=(self.interaction_sprites,),
                    name=obj.name,
                )

    def run(self, dt):
        # draws
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        # updates
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

        # weather
        self.overlay.display()

        if self.raining and not self.shop_active:
            self.rain.update()
        
        self.sky.display(dt)

        if self.player.sleeping:
            self.transition.play(dt)
