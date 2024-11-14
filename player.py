import math
import pygame
from pygame import Surface
from pygame.event import Event
from actor import Actor
from consts import RESOLUTION


class Player(Actor):

    def __init__(self) -> None:
        super().__init__()
        self.facet = pygame.transform.scale(
            pygame.image.load('assets/player.png').convert_alpha(),
            (64, 64),
        )
        self.keys: list[bool] = [False, False, False, False]
        self.speed: float = 400.0
        self.x: float = RESOLUTION[0] / 4
        self.y: float = RESOLUTION[1] / 2
        self.dx: float = 0.0
        self.dy: float = 0.0
        self.dangle: float = 0.0
        self.angle: float = 0.0

    @property
    def pos(self) -> tuple[int, int]:
        return (
            int(self.x - self.facet.get_width() / 2),
            int(self.y - self.facet.get_height() / 2),
        )

    async def draw(self, surface: Surface) -> None:
        facet = pygame.transform.rotate(
            self.facet,
            self.angle * 180 / math.pi,
        )
        x = int(self.x - facet.get_width() / 2)
        y = int(self.y - facet.get_height() / 2)
        surface.blit(facet, (x, y))

    async def update(self, delta: float) -> None:
        self.x += self.speed * self.dx * delta
        self.y += self.speed * self.dy * delta
        self.angle += (self.dangle - self.angle) * delta * 4
        self.x = max([0, min([RESOLUTION[0] / 2, self.x])])
        self.y = max([0, min([RESOLUTION[1], self.y])])
        self.angle = max([-math.pi/4, min(math.pi/4, self.angle)])

    async def react(self, events: list[Event]) -> None:
        for event in (ev for ev in events if ev.type == pygame.KEYUP):
            if event.key in (pygame.K_UP, pygame.K_w):
                self.keys[0] = False
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.keys[1] = False
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.keys[2] = False
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.keys[3] = False
        for event in (ev for ev in events if ev.type == pygame.KEYDOWN):
            if event.key in (pygame.K_UP, pygame.K_w):
                self.keys[0] = True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.keys[1] = True
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.keys[2] = True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.keys[3] = True

        self.dx = self.dy = self.dangle = 0
        if self.keys[0]:
            self.dy -= 1
            self.dangle += math.pi / 4
        if self.keys[1]:
            self.dy += 1
            self.dangle -= math.pi / 4
        if self.keys[2]:
            self.dx -= 1
        if self.keys[3]:
            self.dx += 1
