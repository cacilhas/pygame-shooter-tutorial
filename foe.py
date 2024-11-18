import math
from random import randint, random
from typing import Iterable, Optional
from pygame import Surface
import pygame
from pygame.math import clamp
from action import Action, Collider
from consts import FPS, RESOLUTION
from enemy_fire import EnemyFire
from explosion import Explosion
from fire import Fire
from foe_sensor import FoeSensor
from sounds import AudioBag


class Foe(Collider):

    __inited: bool = False

    facet: Surface
    x: float
    y: float
    dy: float
    dx: float
    hp: int

    def __new__(cls, y: float, speed: float) -> 'Foe':
        if not Foe.__inited:
            RocketFoe.load_assets()
            ShooterFoe.load_assets()
            LaserProofFoe.load_assets()
            Foe.__inited = True

        if random() < 0.125:
            return ShooterFoe(y, speed)
        return LaserProofFoe(y, speed) if random() < 0.25 else RocketFoe(y, speed)

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    async def on_collision(self, other: Collider) -> Optional[Action]:
        if isinstance(other, (Fire, EnemyFire)):
            if isinstance(other, Fire) and other.power in [4, 5]:
                self.hp = 0
            else:
                self.hp -= 1

            if self.hp <= 0:
                actions = [
                    Action.register(Explosion(pos=self.pos, size=72)),
                    Action.remove(self),
                ]
                if isinstance(other, Fire):
                    actions.append(Action.incr_score(10))
                return Action.set(*actions)

            else:
                return Action.play_audio(AudioBag.explosions[0])

        if isinstance(other, Foe):
            if self.y < other.y:
                self.dy = -100
                other.dy = 100
            else:
                self.dy = 100
                other.dy = -100


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
        self.x: float = RESOLUTION[0]
        self.y = y
        self.dx = speed
        self.dy: float = 0.0
        self.hp: int = 3
        self.sensor: FoeSensor | None = None

    @property
    def radius(self) -> float:
        return 32

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Optional[Action]:
        if self.sensor is None:
            self.sensor = FoeSensor(self)
            return Action.register(self.sensor)

        self.x -= self.dx * delta
        self.y += clamp(self.dy, -100, 100) * delta
        self.dy -= self.dy * delta
        if self.x + self.facet.get_width() < 0:
            return self.remove_self()

    def remove_self(self) -> Action:
        action = Action.remove(self)
        if self.sensor:
            action = Action.set(action, Action.remove(self.sensor))
        return action

    async def on_collision(self, other: Collider) -> Optional[Action]:
        from meteor import Meteor
        if isinstance(other, Meteor):
            return Action.set(
                self.remove_self(),
                Action.register(Explosion(pos=other.pos, size=72)),
                Action.play_audio(AudioBag.explosions[0]),
            )
        return await super().on_collision(other)


class ShooterFoe(Foe):

    z: int = 10

    def __new__(cls, y: float, speed: float) -> Foe:
        return Collider.__new__(cls)

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/foe-2.png').convert_alpha(),
            (75, 100),
        )

    def __init__(self, y: float, speed: float) -> None:
        self.x: float = RESOLUTION[0]
        self.y = y
        self.max_hp = self.hp = 10 + randint(0, 4)
        self.dx = speed
        self.dy: float = 0.0
        self.osc: float = 0.0
        self.r = 2 - random() * 4

    @property
    def f(self) -> float:
        return 1.0 - self.hp / self.max_hp

    @property
    def xy(self) -> tuple[float, float]:
        return self.x + math.sin(self.osc) * self.f * 48, self.y

    @property
    def radius(self) -> float:
        return 37.5

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Optional[Action]:
        self.x -= self.dx * delta
        self.dx -= self.dx * delta / 2
        self.y += math.sin(self.dy) * self.r
        self.dy += delta
        self.osc += 10 * self.f * delta

        if random() < 0.03125:
            from enemy_fire import EnemyFire
            return Action.register(EnemyFire(self))

    async def on_collision(self, other: Collider) -> Optional[Action]:
        if isinstance(other, EnemyFire) and other.shooter is self:
            return
        from player import Player
        if isinstance(other, Player):
            return Action.remove(self)
        return await super().on_collision(other)


class LaserProofFoe(RocketFoe):

    facets: list[Surface] = []

    @classmethod
    def load_assets(cls) -> None:
        cls.facets = [
            pygame.image.load(f'assets/foe-3/{idx}.png').convert_alpha()
            for idx in range(12)
        ]

    def __init__(self, y: float, speed: float) -> None:
        super().__init__(y, speed)
        self.idx: float = 0.0
        self.facet = self.facets[0]
        self.hp: int = 1

    @property
    def radius(self) -> float:
        return 32

    async def update(self, delta: float) -> Optional[Action]:
        self.idx += delta * 10
        self.facet = self.facets[int(self.idx) % 12]
        actions: list[Action] = []
        action = await super().update(delta)
        if action:
            actions.append(action)

        if random() < 0.03125:
            from enemy_fire import EnemyFire
            actions.append(Action.register(EnemyFire(self)))

        if actions:
            return Action.set(*actions)

    async def on_collision(self, other: Collider) -> Optional[Action]:
        if isinstance(other, Fire) and other.power in [2, 3]:
            from foe_force_field import FoeForceField
            return Action.register(FoeForceField(self.xy, self.dx))
        if isinstance(other, EnemyFire) and other.shooter is self:
            return
        from player import Player
        if isinstance(other, Player):
            return self.remove_self()
        return await super().on_collision(other)
