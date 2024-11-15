from pygame import Surface
import pygame
from action import Action, Collider
from bullet import Bullet
from consts import RESOLUTION
from sounds import AudioBag


class Foe(Collider):

    facet: Surface | None = None

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/foe-1.png').convert_alpha(),
            (64, 40),
        )

    def __init__(self, y: float, speed: float) -> None:
        if Foe.facet is None:
            Foe.load_assets()
        assert Foe.facet

        self.x = RESOLUTION[0] + Foe.facet.get_width() / 2
        self.y = y
        self.hp = 3
        self.speed = speed

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return 20

    async def draw(self, surface: Surface) -> None:
        facet = Foe.facet
        assert facet
        x = int(self.x - facet.get_width() / 2)
        y = int(self.y - facet.get_height() / 2)
        surface.blit(facet, (x, y))

    async def update(self, delta: float) -> Action:
        facet = Foe.facet
        assert facet
        self.x -= self.speed * delta
        if self.x + facet.get_width() / 2 < 0:
            return Action.remove(self)
        return Action.noAction

    async def on_collision(self, other: Collider, *, jump: bool=False) -> Action | None:
        if isinstance(other, Bullet):
            self.hp -= 1
            to_remove: list[Collider] = [other]
            if self.hp <= 0:
                to_remove.append(self)
                AudioBag.explosions[1].play()
            else:
                AudioBag.explosions[0].play()
            return Action.remove(*to_remove)
        if jump:
            return
        return await other.on_collision(self, jump=True)
