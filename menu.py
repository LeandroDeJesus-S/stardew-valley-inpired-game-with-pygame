import pygame
from settings import *
from support import *


class Menu:
    def __init__(self, player, toggle_shop) -> None:
        self.player = player
        self.toggle_shop = toggle_shop

        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)

        # options
        self.width = 400
        self.space = 10
        self.padding = 8

        # entries
        self.options = list(self.player.inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.inventory.keys())-1
        self.setup()

        # selection
        self.index = 0

        self.buy_surf = self.font.render('buy', False, 'black')
        self.sell_surf = self.font.render('sell', False, 'black')

    def setup(self):
        self.txt_surfs = []
        self.total_height = 0
        for item in self.options:
            txt_surf = self.font.render(item, False, 'black')
            self.txt_surfs.append(txt_surf)

            self.total_height += txt_surf.height + (self.padding * 2)
        
        self.total_height += (len(self.txt_surfs) - 1) * self.space
        self.menu_top = (SCREEN_HEIGHT / 2) - (self.total_height / 2)

        x = SCREEN_WIDTH / 2 - self.width / 2
        self.main_rect = pygame.Rect(x, self.menu_top, self.width, self.total_height)

    def display_money(self):
        money_surf = self.font.render(f'{self.player.money}', False, 'yellow')
        money_rect = money_surf.get_rect(midbottom=(SCREEN_WIDTH/2, self.main_rect.bottom * 1.10))

        pygame.draw.rect(self.display_surface, 'grey', money_rect.inflate(10,10), 0, 5)
        self.display_surface.blit(money_surf, money_rect)

    def inputs(self):
        event = pygame.event.get(pygame.KEYDOWN)
        if not event: return
        
        event = event[0]

        # closing menu
        if event.key == pygame.K_ESCAPE:
            self.toggle_shop()
            self.index = 0
        
        # navigating for options
        if event.key == pygame.K_UP:
            self.index -= 1
        elif event.key == pygame.K_DOWN:
            self.index += 1
        
        self.index = max(0, min(self.index, len(self.options)-1))

        # selecting option
        if event.key == pygame.K_SPACE:
            current_item = self.options[self.index]
            if self.index <= self.sell_border:  # selling
                if self.player.inventory[current_item] > 0:
                    self.player.inventory[current_item] -= 1
                    self.player.money += SALE_PRICES[current_item]

            else:  # buying
               item_price = PURCHASE_PRICES[current_item]
               if self.player.money >= item_price:
                   self.player.seed_inventory[current_item] += 1
                   self.player.money -= item_price
    
    def display_entries(self, txt_surf, amount, top, selected):
        # background
        height = txt_surf.height + self.padding * 2
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, height)
        pygame.draw.rect(self.display_surface, 'white', bg_rect, 0, 5)

        # text
        txt_rect = txt_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(txt_surf, txt_rect)

        # amount
        amount_surf = self.font.render(f'${amount}', False, 'black')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 5)
            if self.index <= self.sell_border:  # selling
                pos = self.sell_surf.get_rect(midleft=(self.main_rect.left + self.width//2, bg_rect.centery))
                self.display_surface.blit(self.sell_surf, pos)
                
            else:  # buying
                pos = self.buy_surf.get_rect(midleft=(self.main_rect.left + self.width//2, bg_rect.centery))
                self.display_surface.blit(self.buy_surf, pos)
        
    def update(self):
        self.inputs()
        self.display_money()

        for txt_idx, txt_surf in enumerate(self.txt_surfs):
            top = self.main_rect.top + txt_idx * (txt_surf.height + self.padding * 2 + self.space)
            amount = list(self.player.inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount[txt_idx]
            self.display_entries(txt_surf, amount, top, self.index == txt_idx)



