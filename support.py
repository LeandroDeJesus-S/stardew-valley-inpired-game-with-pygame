from os import walk
from os.path import join
from pygame.image import load
from pygame import font, display, image
from os import listdir
from re import sub


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

        
def load_image(path):
    img = image.load(path)
    return img.convert_alpha() if img.get_alpha() else img.convert()


def import_files_dict(dir):
        animations = dict(
            map(
                lambda f: (sub(r'\.\w{3}$', '', f), load_image(join(dir, f))), 
                listdir(dir)
            )
        )
        return animations
