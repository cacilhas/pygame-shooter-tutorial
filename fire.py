
import math
from random import random
from pygame import Surface
import pygame
from action import Action, Actor, Collider
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
        nuke = Surface((1280, 1280), pygame.SRCALPHA)
        pygame.draw.circle(nuke, '#00bbff88', (640, 640), 640)
        cls.facets.extend([
            bullet,
            bullet,
            laser,
            laser,
            nuke,
            nuke,
        ])

    def __init__(self, pos: tuple[float, float], angle: float, *, power: int, quiet: bool=False) -> None:
        self.x, self.y = pos
        self.angle = angle
        self.speed: float = 1200.0
        self.started: bool = quiet

        if not self.facets:
            self.load_assets()
        self.facet = self.facets[power]
        self.power = power
        self._radius: float = 6.0

        match power:
            case 1:
                self.delay = 0.1875

            case 2 | 3:
                self.delay = 0.0
                self._radius = 12.0

            case 4:
                self.delay = 3.0

            case _:
                self.delay = 0.125

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return self._radius

    async def draw(self, surface: Surface) -> None:
        if self.power in [2, 3]:
            facet = pygame.transform.rotate(self.facet, -self.angle * 180 / math.pi)
        elif self.power in [4, 5]:
            facet = pygame.transform.scale(self.facet, (self.radius, self.radius))
        else:
            facet = self.facet
        self.blit(dest=surface, src=facet)

    async def update(self, delta: float) -> Action | None:
        if self.power in [1, 3]:
            # Triple shoot
            self.power -= 1
            return Action.set(
                Action.register(Fire(self.xy, self.angle - math.pi/12, power=self.power, quiet=True)),
                Action.register(Fire(self.xy, self.angle + math.pi/12, power=self.power, quiet=True)),
            )

        if not self.started:
            self.started = True
            match self.power:
                case 2 | 3:
                    return Action.play_audio(AudioBag.laser) if random() < 0.5 else None

                case 4:
                    return Action.play_audio(AudioBag.explosions[1])

                case _:
                    return Action.play_audio(AudioBag.bullet)

        if self.power in [4, 5]:
            self._radius += self.speed * delta

            if self.radius > 1280:
                return Action.remove(self)

            else:
                from foe import Foe
                def scoreit(actor: Actor) -> Action | None:
                    if isinstance(actor, Foe):
                        return Action.set(
                            Action.incr_score(10),
                            Action.remove(actor),
                        )

                return Action.for_each(scoreit)

        width, height = self.facet.get_size()
        speed = self.speed * delta
        if self.power not in [4, 5]:
            dx, dy = math.cos(self.angle) * speed, math.sin(self.angle) * speed
            self.x += dx
            self.y += dy

        if self.x > RESOLUTION[0] + width / 2:
            return Action.remove(self)
