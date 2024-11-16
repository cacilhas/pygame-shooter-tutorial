from math import isinf
from random import random

from pygame import Surface
import pygame
from pygame.font import Font
from action import Action, Collider
from consts import RESOLUTION
from player import Player
from sounds import AudioBag


class PowerUp(Collider):

    facets: list[Surface] = []

    @classmethod
    def load_assets(cls) -> None:
        font = Font('assets/digital-7.ttf', 48)
        for i in range(3):
            facet = Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(facet, colors[i][0], (24, 24), 24)
            text = font.render(str(i), True, colors[i][1])
            facet.blit(text, (text.get_width()/2, 4))
            cls.facets.append(facet)

    def __init__(self, y: float, speed: float) -> None:
        if not self.facets:
            self.load_assets()

        power = 0
        if random() < 0.25:
            power = 1
            if random() < 0.25:
                power = 2

        self.facet = self.facets[power]
        self.power = power

        self.x = RESOLUTION[0] + self.facet.get_width() / 2
        self.y = y
        self.speed = speed

    @property
    def xy(self) -> tuple[float, float]:
        return (self.x, self.y)

    async def update(self, delta: float) -> Action | None:
        self.x -= self.speed * delta
        if self.x < -self.facet.get_width():
            return Action.remove(self)

    async def draw(self, surface: Surface) -> None:
        return self.blit(dest=surface, src=self.facet)

    async def on_collision(self, other: Collider) -> Action | None:
        if isinstance(other, Player):
            if other.power < self.power:
                AudioBag.power_up.play()
            elif other.power > self.power:
                AudioBag.power_down.play()
            else:
                AudioBag.catch.play()

            other.power = self.power
            return Action.set(
                Action.remove(self),
                Action.incr_score(20 + self.power * 10),
            )


colors = [
    ('black', 'white'),
    ('orange', 'black'),
    ('red', 'black'),
]
