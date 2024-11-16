from pygame import Surface
import pygame
from pygame.math import clamp
from action import Action, Collider
from consts import FPS, RESOLUTION
from explosion import Explosion
from fire import Fire
from foe_sensor import FoeSensor
from sounds import AudioBag


class Foe(Collider):

    facet: Surface
    x: float
    y: float
    dy: float
    speed: float

    def __new__(cls, y: float, speed: float) -> 'Foe':
        return RocketFoe(y, speed)

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y


class RocketFoe(Foe):

    def __new__(cls, y: float, speed: float) -> 'Foe':
        return Collider.__new__(cls)

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/foe-1.png').convert_alpha(),
            (64, 40),
        )

    def __init__(self, y: float, speed: float) -> None:
        if not hasattr(RocketFoe, 'facet'):
            self.load_assets()

        self.x = RESOLUTION[0] + self.facet.get_width() / 2
        self.y = y
        self.dy: float = 0.0
        self.hp: int = 3
        self.speed = speed
        self.sensor: FoeSensor | None = None

    @property
    def radius(self) -> float:
        return 32

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Action | None:
        if self.sensor is None:
            self.sensor = FoeSensor(self)
            return Action.register(self.sensor)

        self.x -= self.speed * delta
        self.y += clamp(self.dy, -100, 100) * delta
        self.dy -= self.dy * delta
        if self.x + self.facet.get_width() / 2 < 0:
            return Action.remove(self)

    async def on_collision(self, other: Collider) -> Action | None:
        if isinstance(other, Fire):
            self.hp -= 1
            if self.hp <= 0:
                return Action.set(
                    Action.register(Explosion(pos=self.pos, size=72)),
                    Action.remove(self),
                    Action.remove(other),
                    Action.incr_score(10),
                )
            else:
                return Action.set(
                    Action.remove(other),
                    Action.play_audio(AudioBag.explosions[0])
                )

        if isinstance(other, Foe):
            if self.y < other.y:
                self.dy = -100
                other.dy = 100
            else:
                self.dy = 100
                other.dy = -100

    async def on_close(self) -> Action | None:
        if self.sensor:
            return Action.remove(self.sensor)
