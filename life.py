from typing import Protocol
import pygame
from pygame.surface import Surface
from action import Actor
from consts import RESOLUTION


class App(Protocol):

    lives: int


class Lives(Actor):

    facet: Surface
    z: int = 20

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/player.png').convert_alpha(),
            (32, 32),
        )

    def __init__(self, app: App) -> None:
        if not hasattr(Lives, 'facet'):
            self.load_assets()
        self.app = app
        self.max: int = self.app.lives - 1
        self.width, self.height = self.facet.get_size()

    @property
    def xy(self) -> tuple[float, float]:
        return RESOLUTION[0] / 2.0, self.height / 2.0

    async def draw(self, surface: Surface) -> None:
        extra_lifes = self.app.lives - 1
        if extra_lifes > 0:
            facet = Surface((self.width * self.max, self.height), pygame.SRCALPHA)
            for i in range(extra_lifes):
                facet.blit(self.facet, (i *self.width, 0))
            self.blit(dest=surface, src=facet)
