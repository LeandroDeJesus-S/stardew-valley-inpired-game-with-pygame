import pygame


class Timer:
    def __init__(self, duration, callback=None, *cbargs, **cbkwargs) -> None:
        self.duration = duration
        self.func = callback
        self.start_time = 0
        self.active = False

        self.cbargs = cbargs
        self.cbkwargs = cbkwargs

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()
    
    def deactivate(self):
        self.active = False
        self.start_time = 0
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration and self.active:
            self.deactivate()
            if self.func:
                self.func(*self.cbargs, **self.cbkwargs)
        