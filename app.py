from typing import NoReturn
import pygame
from pygame import Surface
from pygame.constants import K_ESCAPE
from pygame.time import Clock

from consts import BACKGROUND, FPS, RESOLUTION


class App:

    def __init__(self) -> None:
        pygame.init()
        self.screen: Surface = pygame.display.set_mode(
            RESOLUTION,
            pygame.NOFRAME | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption('Shooter Tutorial')
        self.clock = Clock()

    def update(self) -> None:
        delta: float = self.clock.tick(FPS) / FPS

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        pygame.display.flip()

    def events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                import sys
                pygame.quit()
                sys.exit()

    def start(self) -> NoReturn:
        while True:
            self.events()
            self.update()
            self.draw()
            pygame.time.delay(10)
