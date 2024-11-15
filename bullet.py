
import math
from pygame import Surface
import pygame
from action import Action, Collider
from consts import RESOLUTION
from sounds import AudioBag


class Bullet(Collider):

    facet: Surface

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/bullet.png').convert_alpha(),
            (12, 12),
        )

    def __init__(self, pos: tuple[float, float], angle: float) -> None:
        self.x, self.y = pos
        self.angle = angle
        self.speed = 1200.0

        if not hasattr(Bullet, 'facet'):
            Bullet.load_assets()
        AudioBag.bullet.play()

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return 6

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Action | None:
        width, height = self.facet.get_size()
        speed = self.speed * delta
        dx, dy = math.cos(self.angle) * speed, math.sin(self.angle) * speed
        self.x += dx
        self.y += dy

        if not -width / 2 < self.x < RESOLUTION[0] + width / 2:
            return Action.remove(self)
        if not -height / 2 < self.y < RESOLUTION[1] + height / 2:
            return Action.remove(self)
