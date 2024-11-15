from random import randint
from pygame import Surface
import pygame
from action import Action, Actor
from consts import RESOLUTION


class StarsBackground(Actor):

    def __init__(self) -> None:
        facet = self.facet = Surface(RESOLUTION, pygame.SRCALPHA)
        self.speed: float = 40.0
        self.x: float = 0.0
        self.z = -1
        width = self.width = RESOLUTION[0]

        for x in range(width):
            y = randint(0, RESOLUTION[1])
            pygame.draw.circle(
                facet,
                'white',
                (x, y),
                1,
            )

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, 0.0

    async def update(self, delta: float) -> Action | None:
        self.x -= self.speed * delta
        if self.x <= - self.width:
            self.x += self.width

    async def draw(self, surface: Surface) -> None:
        surface.blit(self.facet, self.pos)
        pos = self.pos[0] + self.width, self.pos[1]
        surface.blit(self.facet, pos)
