from pygame import *
from settings import *
from level import Level


class Game:
    def __init__(self) -> None:
        init()
        self.display_surface = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        display.set_caption('Stardew Inspired')
        
        self.running = True
        self.clock = time.Clock()

        self.level = Level()
    
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            if event.get(eventtype=QUIT):
                self.running = False
            
            self.level.run(dt)
            display.update()

        quit()


if __name__ == '__main__':
    game = Game()
    game.run()
