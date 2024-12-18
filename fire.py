import math
from random import random
from typing import Optional
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
            pygame.image.load("assets/bullet.png").convert_alpha(),
            (12, 12),
        )
        laser = Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.line(laser, "red", (0, 12), (24, 12), 2)
        fake_nuke = Surface((1, 1), pygame.SRCALPHA)
        cls.facets.extend(
            [
                bullet,
                bullet,
                laser,
                laser,
                fake_nuke,
                fake_nuke,
            ]
        )

    def __init__(
        self, pos: tuple[float, float], angle: float, *, power: int, quiet: bool = False
    ) -> None:
        if not self.facets:
            self.load_assets()

        self.x, self.y = pos
        self.angle = angle
        self.speed: float = 1200.0
        self.started: bool = quiet

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
        else:
            facet = self.facet
        self.blit(dest=surface, src=facet)

    async def update(self, delta: float) -> Optional[Action]:
        if self.power in [1, 3]:
            # Triple shoot
            self.power -= 1
            return Action.set(
                Action.register(
                    Fire(
                        self.xy, self.angle - math.pi / 12, power=self.power, quiet=True
                    )
                ),
                Action.register(
                    Fire(
                        self.xy, self.angle + math.pi / 12, power=self.power, quiet=True
                    )
                ),
            )

        if not self.started:
            self.started = True
            match self.power:
                case 2 | 3:
                    return Action.play_audio(AudioBag.laser) if random() < 0.5 else None

                case 4 | 5:
                    return Action.play_audio(AudioBag.explosions[1])

                case _:
                    return Action.play_audio(AudioBag.bullet)

        if self.power in [4, 5]:
            self._radius += math.sqrt(self.speed * self._radius) * 5 * delta
            if self.radius > 1280:
                return Action.remove(self)
            facet = Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            color = (
                0x00,
                0xFF,
                0xBB,
                max(
                    0x00,
                    min(
                        0xFF,
                        int(256 - (256.0 * self.radius / 1280.0)),
                    ),
                ),
            )
            pygame.draw.circle(facet, color, (self.radius, self.radius), self.radius)
            self.facet = facet
            return

        width, height = self.facet.get_size()
        speed = self.speed * delta
        dx, dy = math.cos(self.angle) * speed, math.sin(self.angle) * speed
        self.x += dx
        self.y += dy

        if self.x > RESOLUTION[0]:
            return Action.remove(self)

    async def on_collision(self, other: "Collider") -> Optional[Action]:
        if self.power not in [4, 5]:
            from foe import Foe
            from foe_force_field import FoeForceField
            from meteor import Meteor

            if isinstance(other, (Foe, FoeForceField, Meteor)):
                return Action.remove(self)
