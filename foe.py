from pygame import Surface
import pygame
from action import Action, Actor
from consts import RESOLUTION


class Foe(Actor):

    facet: Surface|None = None

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
        self.speed = speed

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
