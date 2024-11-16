import math
from random import choice
from pygame import Surface
import pygame
from pygame.mixer import Channel
from action import Action, Collider
from consts import RESOLUTION
from explosion import Explosion
from fire import Fire
from foe import Foe
from sounds import AudioBag


class Meteor(Collider):

    facets: list[Surface] = []
    channel: Channel

    @classmethod
    def load_assets(cls) -> None:
        cls.facets = [
            pygame.image.load(f'assets/meteors/meteor{i}.png').convert_alpha()
            for i in range(1, 5)
        ]
        cls.channel = Channel(2)

    def __init__(self, y: float, speed: float, size: int, rotation: float) -> None:
        if not self.facets:
            self.load_assets()
        self.facet: Surface = pygame.transform.scale(choice(self.facets), (size, size))

        self.x: float = RESOLUTION[0] + self.facet.get_width()
        self.y: float = y
        self.size = size
        self.speed: float = speed
        self.angle: float = 0.0
        self.rotation = rotation

    @property
    def radius(self) -> float:
        return self.size / 2.0

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    async def update(self, delta: float) -> Action | None:
        self.x -= self.speed * delta
        if self.x < -self.facet.get_width():
            return Action.remove(self)
        self.angle += self.rotation * delta

    async def draw(self, surface: Surface) -> None:
        facet = pygame.transform.rotate(self.facet, self.angle * 180 / math.pi)
        self.blit(dest=surface, src=facet)

    async def on_collision(self, other: Collider) -> Action | None:
        if isinstance(other, (Foe, Fire)):
            actions: list[Action] = []

            if not (isinstance(other, Fire) and other.power == 4):
                actions.append(Action.remove(other))

            if isinstance(other, Fire) and other.power in [0, 1] or isinstance(other, Foe):
                self.channel.play(AudioBag.explosions[0])
                actions.append(Action.register(Explosion(pos=other.pos, size=72)))

            return Action.set(*actions)
