from typing import Protocol
import pygame
from pygame.surface import Surface
from action import Action, Collider
from sounds import AudioBag


class Foe(Protocol):

    @property
    def xy(self) -> tuple[float, float]:
        ...


class EnemyFire(Collider):

    facet: Surface

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/enemy-bullet.png').convert_alpha(),
            (12, 12),
        )

    def __init__(self, shooter: Foe) -> None:
        if not hasattr(EnemyFire, 'facet'):
            self.load_assets()

        self.x, self.y = shooter.xy
        self.shooter = shooter
        self.speed: float = 1200.0
        self.started: bool = False

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return 6.0

    async def draw(self, surface: Surface) -> None:
        return self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Action | None:
        if not self.started:
            self.started = True
            return Action.play_audio(AudioBag.explosions[0])

        self.x -= self.speed * delta
        if self.x < -self.radius:
            return Action.remove(self)

    async def on_collision(self, other: 'Collider') -> Action | None:
        from foe import Foe
        if isinstance(other, Foe):
            foe: Foe = other
            if foe is self.shooter:
                return

            from explosion import Explosion
            return Action.remove(self)

        from player import Player
        if isinstance(other, Player):
            return Action.remove(self)
