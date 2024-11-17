
import pygame
from pygame.font import Font
from pygame.surface import Surface
from action import Actor
from consts import RESOLUTION


class GameOver(Actor):

    z: int = 20

    def __init__(self) -> None:
        self.font = Font('assets/game-over.ttf', 120)
        self.aux_font = Font('assets/digital-7.ttf', 24)
        self.populate()

    def populate(self) -> None:
        shadow: Surface =  self.font.render('Game Over', True, '#220000')
        shadow_size: tuple[int, int] = shadow.get_size()

        text: Surface = self.aux_font.render('Press Enter to restart', True, 'white')
        text_size = text.get_size()

        size = shadow_size[0] + 4, shadow_size[1] + text_size[1] + 36
        facet = self.facet = Surface(size, pygame.SRCALPHA)
        facet.blit(shadow, (4, 4))
        facet.blit(text, ((size[0] - text_size[0]) / 2, shadow_size[1] + 32))

        text = self.font.render('Game Over', True, '#aa0000')
        facet.blit(text, (0, 0))


    @property
    def xy(self) -> tuple[float, float]:
        return RESOLUTION[0] / 2, RESOLUTION[1] / 2

    async def draw(self, surface: Surface) -> None:
        self.blit(dest=surface, src=self.facet)
