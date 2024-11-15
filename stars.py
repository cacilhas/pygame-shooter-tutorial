from random import choice, randint
from pygame import Surface
import pygame
from action import Action, Actor
from consts import RESOLUTION


class StarsBackground(Actor):

    colors = [
        (0xff, 0xff, 0xff),
        (0xff, 0xd0, 0xd0),
        (0xff, 0xff, 0xd0),
        (0xd0, 0xd0, 0xff),
    ]

    def __init__(self) -> None:
        self.z = -1
        width = self.width = RESOLUTION[0]

        facets = self.facets = [
            Surface(RESOLUTION, pygame.SRCALPHA),
            Surface(RESOLUTION, pygame.SRCALPHA),
            Surface(RESOLUTION, pygame.SRCALPHA),
        ]
        self.speeds: list[float] = [10.0, 20.0, 40.0]
        self.xs: list[float] = [10.0, 0.0, 0.0]

        for i, facet in enumerate(facets):
            for x in range(0, width, 1 << i):
                y = randint(0, RESOLUTION[1])
                color = choice(self.colors)
                pygame.draw.circle(
                    facet,
                    color,
                    (x, y),
                    i + 1,
                )

    async def update(self, delta: float) -> Action | None:
        for i, speed in enumerate(self.speeds):
            self.xs[i] -= speed * delta
            if self.xs[i] < 0:
                self.xs[i] += self.width

    async def draw(self, surface: Surface) -> None:
        for i, facet in enumerate(self.facets):
            surface.blit(facet, (self.xs[i] - self.width, 0))
            surface.blit(facet, (self.xs[i], 0))
