from os import walk
from os.path import join
from pygame.image import load
from itertools import combinations
from pygame import font, display


def debug(info, pos, color='white', fsize=30):
    surf = display.get_surface()
    fnt = font.Font(size=fsize)
    fnt_surf = fnt.render(info, False, color)
    surf.blit(fnt_surf, pos)


def import_folder(path, convert='convert_alpha'):
    imgs = []
    for root, _, files in walk(path):
        img = map(lambda f: getattr(load(join(root, f)), convert)(), files)
        imgs.append(list(img))
    
    return imgs

        
