
import math
from pygame import Surface
import pygame
from action import Action, Collider
from consts import RESOLUTION
from sounds import AudioBag


class Bullet(Collider):

    facets: list[Surface] = []

    @classmethod
    def load_assets(cls) -> None:
        bullet = pygame.transform.scale(
            pygame.image.load('assets/bullet.png').convert_alpha(),
            (12, 12),
        )
        laser = Surface((24, 2))
        laser.fill('red')
        cls.facets.extend([bullet, bullet, laser])

    def __init__(self, pos: tuple[float, float], angle: float, *, power: int) -> None:
        self.x, self.y = pos
        self.angle = angle
        self.speed = 1200.0

        if not self.facets:
            self.load_assets()
        self.facet = self.facets[power]
        self.power = power
        AudioBag.bullet.play()

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        match self.power:
            case 2:
                return 20
            case _:
                return 6

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Action | None:
        if self.power == 1:
            # Triple bullet
            self.power = 0
            return Action.set(
                Action.register(Bullet(self.xy, self.angle - math.pi/12, power=0)),
                Action.register(Bullet(self.xy, self.angle + math.pi/12, power=0)),
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
