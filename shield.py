import math
from typing import Optional, Protocol
import pygame
from pygame.surface import Surface
from action import Action, Collider
from consts import FPS
from sounds import AudioBag


class Player(Protocol):

    angle: float

    @property
    def xy(self) -> tuple[float, float]:
        ...


class Shield(Collider):

    facet: Surface

    @classmethod
    def load_assets(cls):
        cls.facet = pygame.image.load('assets/shield.png')

    def __init__(self, player: Player) -> None:
        if not hasattr(Shield, 'facet'):
            self.load_assets()
        self.player = player
        self.x, self.y = player.xy
        self.size: float = 2.0
        self.angle: float = player.angle
        self.hp: int = 10

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return self.size

    async def draw(self, surface: Surface) -> None:
        facet = pygame.transform.scale(self.facet, (self.size, self.size))
        return self.blit(dest=surface, src=facet)

    async def update(self, delta: float) -> Optional[Action]:
        tx, ty = self.player.xy
        tangle = self.player.angle
        tx += math.cos(tangle) * 48
        ty += math.sin(tangle) * 48

        self.angle += (tangle - self.angle) * 10 * delta
        self.x += (tx - self.x) * 10 * delta
        self.y += (ty - self.y) * 10 * delta
        self.size += (128 - self.size) * 5 * delta

    async def on_collision(self, other: Collider) -> Optional[Action]:
        from enemy_fire import EnemyFire
        from explosion import Explosion
        from foe import Foe
        from foe_force_field import FoeForceField
        from meteor import Meteor

        if isinstance(other, Foe):
            return Action.set(
                Action.remove(self),
                Action.play_audio(AudioBag.explosions[1]),
                Action.register(Explosion(pos=self.pos, size=128)),
            )

        if isinstance(other, (EnemyFire, FoeForceField)):
            self.hp -= 1

            if self.hp <= 0:
                return Action.set(
                    Action.remove(self),
                    Action.play_audio(AudioBag.explosions[1]),
                    Action.register(Explosion(pos=self.pos, size=128)),
                )
            else:
                return Action.play_audio(AudioBag.explosions[0])

        if isinstance(other, Meteor):
            self.x -= 10 / FPS
