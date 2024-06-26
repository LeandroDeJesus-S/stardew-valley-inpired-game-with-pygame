from pygame import *
from settings import *
from support import *

class CameraGroup(sprite.Group):
    def __init__(self, display_surface: Surface, ground: sprite.Sprite):
        super().__init__()
        self.display_surface = display_surface
        self.ground = ground
    
    def custom_draw(self, player):
        player_pos = Vector2(player.rect.center)
        camera_dis = Vector2(SCREEN_WIDTH, SCREEN_HEIGHT) / 2

        offset = player_pos - camera_dis
        max_offset = Vector2(self.ground.image.size) - Vector2(self.display_surface.size)
        offset.x = max(0, min(offset.x, max_offset.x))
        offset.y = max(0, min(offset.y, max_offset.y))

        ground_pos = self.ground.rect.topleft - offset
        self.display_surface.blit(self.ground.image, ground_pos)

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
                if sprite.z != layer:
                    continue

                offset_rect: Rect = sprite.rect.copy()
                offset_rect.center -= offset
                self.display_surface.blit(sprite.image, offset_rect)
        
        debug(f'player_pos: {player_pos} | {player.pos}\noffset_cam: {offset}', (20, 100))
