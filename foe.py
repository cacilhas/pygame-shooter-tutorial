from pygame import Surface
import pygame
from action import Action, Collider
from consts import FPS, RESOLUTION
from explosion import Explosion
from fire import Fire
from sounds import AudioBag


class Foe(Collider):

    facet: Surface

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/foe-1.png').convert_alpha(),
            (64, 40),
        )

    def __init__(self, y: float, speed: float) -> None:
        if not hasattr(Foe, 'facet'):
            Foe.load_assets()

        self.x = RESOLUTION[0] + self.facet.get_width() / 2
        self.y = y
        self.hp = 3
        self.speed = speed

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return 32

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Action | None:
        self.x -= self.speed * delta
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
                AudioBag.explosions[0].play()
                return Action.remove(other)

        if isinstance(other, Foe):
            self.y -= self.speed / FPS
            other.y += other.speed / FPS
