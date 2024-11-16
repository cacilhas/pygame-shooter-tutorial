
import pygame
from pygame.font import Font
from pygame.surface import Surface
from action import Actor
from consts import RESOLUTION


class Paused(Actor):

    def __init__(self) -> None:
        self.font = Font('assets/game-over.ttf', 120)
        self.populate()

    def populate(self) -> None:
        text: Surface =  self.font.render('Paused', True, '#001122')
        size: tuple[int, int] = text.get_size()
        size = size[0] + 4, size[1] + 3
        facet = self.facet = Surface(size, pygame.SRCALPHA)
        facet.blit(text, (4, 4))
        text: Surface =  self.font.render('Paused', True, '#00aaff')
        facet.blit(text, (0, 0))


    @property
    def xy(self) -> tuple[float, float]:
        return RESOLUTION[0] / 2, RESOLUTION[1] / 2

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)
