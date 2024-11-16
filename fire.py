
import math
from random import random
from re import L
from pygame import Surface
import pygame
from action import Action, Collider
from consts import RESOLUTION
from sounds import AudioBag


class Fire(Collider):

    facets: list[Surface] = []

    @classmethod
    def load_assets(cls) -> None:
        bullet = pygame.transform.scale(
            pygame.image.load('assets/bullet.png').convert_alpha(),
            (12, 12),
        )
        laser = Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.line(laser, 'red', (0,12), (24,12), 2)
        cls.facets.extend([
            bullet,
            bullet,
            laser,
            laser,
        ])

    def __init__(self, pos: tuple[float, float], angle: float, *, power: int, sound: bool=True) -> None:
        self.x, self.y = pos
        self.angle = angle
        self.speed = 1200.0

        if not self.facets:
            self.load_assets()
        self.facet = self.facets[power]
        self.power = power

        match power:
            case 1:
                if sound:
                    AudioBag.bullet.play()
                self.delay = 0.1875

            case 2 | 3:
                if sound and random() < 0.25:
                    AudioBag.laser.play()
                self.delay = 0.0

            case _:
                if sound:
                    AudioBag.bullet.play()
                self.delay = 0.125

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        match self.power:
            case 2 | 3:
                return 12
            case _:
                return 6

    async def draw(self, surface: Surface) -> None:
        if self.power in [2, 3]:
            facet = pygame.transform.rotate(self.facet, -self.angle * 180 / math.pi)
        else:
            facet = self.facet
        self.blit(dest=surface, src=facet)

    async def update(self, delta: float) -> Action | None:
        if self.power in [1, 3]:
            # Triple shoot
            self.power -= 1
            return Action.set(
                Action.register(Fire(self.xy, self.angle - math.pi/12, power=self.power, sound=False)),
                Action.register(Fire(self.xy, self.angle + math.pi/12, power=self.power, sound=False)),
            )

        width, height = self.facet.get_size()
        speed = self.speed * delta
        dx, dy = math.cos(self.angle) * speed, math.sin(self.angle) * speed
        self.x += dx
        self.y += dy

        if not -width / 2 < self.x < RESOLUTION[0] + width / 2:
            return Action.remove(self)
        if not -height / 2 < self.y < RESOLUTION[1] + height / 2:
            return Action.remove(self)
