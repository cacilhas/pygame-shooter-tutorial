from typing import NoReturn
import pygame
from pygame import Surface
from pygame.constants import K_ESCAPE
from pygame.time import Clock

from actor import Actor
from consts import BACKGROUND, FPS, RESOLUTION
from player import Player


class App:

    def __init__(self) -> None:
        pygame.init()
        self.screen: Surface = pygame.display.set_mode(
            RESOLUTION,
            pygame.NOFRAME | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption('Shooter Tutorial')
        self.clock = Clock()
        self.actors: list[Actor] = []
        self.populate()

    def populate(self) -> None:
        self.actors.append(Player())

    def update(self) -> None:
        delta: float = self.clock.tick(FPS) / 1000
        for actor in self.actors:
            actor.update(delta)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        for actor in self.actors:
            actor.draw(self.screen)
        pygame.display.flip()

    def events(self) -> None:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                import sys
                pygame.quit()
                sys.exit()
        for actor in self.actors:
            actor.react(events)

    def start(self) -> NoReturn:
        while True:
            self.events()
            self.update()
            self.draw()
