import pygame
from pygame.image import load
from settings import *


class Overlay:
    OVERLAY_PATH = 'graphics/overlay'
    def __init__(self, player) -> None:
        self.display_surface = pygame.display.get_surface()
        self.player = player

        self.tools_surf = {tool: load(f'{self.OVERLAY_PATH}/{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: load(f'{self.OVERLAY_PATH}/{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self):
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)

        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf, seed_rect)
