
from pygame import Surface
import pygame
from pygame.mixer import Channel
from action import Action, Actor
from sounds import AudioBag


class Explosion(Actor):

    facets: list[Surface] = []
    channel: Channel
    z: int = 12

    @classmethod
    def load_assets(cls) -> None:
        cls.facets = [
            pygame.image.load(f'assets/explosion/flash{i:02d}.png').convert_alpha()
            for i in range(9)
        ]
        cls.channel = Channel(2)

    @property
    def pos(self) -> tuple[int, int]:
        return self.__pos

    def __init__(self, *, pos: tuple[int, int], size: int) -> None:
        if not self.facets:
            self.load_assets()

        self.facets = [
            pygame.transform.scale(facet, (size, size))
            for facet in self.facets
        ]

        self.__pos = pos
        self.frame: float = 0
        self.channel.play(AudioBag.explosions[1])

    async def update(self, delta: float) -> Action | None:
        self.frame += delta * 40
        if self.frame >= 9:
            return Action.remove(self)

    async def draw(self, surface: Surface) -> None:
        frame = min(8, int(self.frame))
        self.blit(dest=surface, src=self.facets[frame])
