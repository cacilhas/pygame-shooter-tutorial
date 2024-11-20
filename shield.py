import math
from typing import Optional, Protocol
import pygame
from pygame.surface import Surface
from action import Action, Collider
from consts import FPS
from sounds import AudioBag


class Player(Protocol):
    angle: float
    shield: Optional["Shield"]

    @property
    def xy(self) -> tuple[float, float]: ...


class Shield(Collider):
    facet: Surface

    @classmethod
    def load_assets(cls):
        cls.facet = pygame.image.load("assets/shield.png")

    def __init__(self, player: Player) -> None:
        if not hasattr(Shield, "facet"):
            self.load_assets()
        self.player = player
        player.shield = self
        self.x, self.y = player.xy
        self.size: float = 2.0
        self.desired_size: float = 64.0
        self.angle: float = player.angle
        self.hp: int = 10

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return self.size

    async def draw(self, surface: Surface) -> None:
        facet = pygame.transform.rotate(
            pygame.transform.scale(self.facet, (self.size * 2, self.size * 2)),
            -self.angle * 180 / math.pi,
        )
        return self.blit(dest=surface, src=facet)

    async def update(self, delta: float) -> Optional[Action]:
        tx, ty = self.player.xy
        tangle = self.player.angle
        tx += math.cos(tangle) * self.desired_size
        ty += math.sin(tangle) * self.desired_size

        self.angle = tangle
        self.x = tx
        self.y = ty
        self.size += (self.desired_size - self.size) * 4 * delta

    async def on_collision(self, other: Collider) -> Optional[Action]:
        from enemy_fire import EnemyFire
        from explosion import Explosion
        from foe import Foe
        from foe_force_field import FoeForceField
        from meteor import Meteor

        if isinstance(other, (EnemyFire, Foe, FoeForceField)):
            self.hp -= 4 if isinstance(other, Foe) else 1

            if self.hp <= 0:
                self.player.shield = None
                return Action.set(
                    Action.remove(self),
                    Action.play_audio(AudioBag.explosions[1]),
                    Action.register(Explosion(pos=self.pos, size=int(self.size))),
                )
            else:
                return Action.set(
                    Action.play_audio(AudioBag.explosions[0]),
                    Action.register(Explosion(pos=self.pos, size=12)),
                )

        if isinstance(other, Meteor):
            self.x -= 10 / FPS
