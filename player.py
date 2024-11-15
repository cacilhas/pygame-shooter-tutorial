import math
import pygame
from pygame import Surface
from pygame.event import Event
from action import Action, Collider
from bullet import Bullet
from consts import RESOLUTION
from foe import Foe
from sounds import AudioBag


class Player(Collider):

    def __init__(self) -> None:
        super().__init__()
        self.facet = pygame.transform.scale(
            pygame.image.load('assets/player.png').convert_alpha(),
            (64, 64),
        )
        pygame.display.set_icon(self.facet)
        self.keys: list[bool] = [False] * 5
        self.speed: float = 400.0
        self.no_fire = 0.0
        self.x: float = RESOLUTION[0] / 4
        self.y: float = RESOLUTION[1] / 2
        self.dx: float = 0.0
        self.dy: float = 0.0
        self.dangle: float = 0.0
        self.angle: float = 0.0

    @property
    def radius(self) -> float:
        return 32

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    async def draw(self, surface: Surface) -> None:
        facet = pygame.transform.rotate(
            self.facet,
            -self.angle * 180 / math.pi,
        )
        x = int(self.x - facet.get_width() / 2)
        y = int(self.y - facet.get_height() / 2)
        surface.blit(facet, (x, y))

    async def update(self, delta: float) -> Action:
        self.no_fire = max([0, self.no_fire - delta])
        self.x += self.speed * self.dx * delta
        self.y += self.speed * self.dy * delta
        self.angle += (self.dangle - self.angle) * delta * 4
        self.x = max([0, min([RESOLUTION[0] / 2, self.x])])
        self.y = max([0, min([RESOLUTION[1], self.y])])
        self.angle = max([-math.pi/4, min(math.pi/4, self.angle)])

        if self.keys[4] and self.no_fire == 0:
            self.no_fire = 0.125
            pos = self.x, self.y
            return Action.register(Bullet(pos, self.angle))
        return Action.noAction

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
            if event.key in (pygame.K_SPACE, pygame.K_LCTRL):
                self.keys[4] = False
        for event in (ev for ev in events if ev.type == pygame.KEYDOWN):
            if event.key in (pygame.K_UP, pygame.K_w):
                self.keys[0] = True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.keys[1] = True
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.keys[2] = True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.keys[3] = True
            if event.key in (pygame.K_SPACE, pygame.K_LCTRL):
                self.keys[4] = True

        self.dx = self.dy = self.dangle = 0
        if self.keys[0]:
            self.dy -= 1
            self.dangle -= math.pi / 4
        if self.keys[1]:
            self.dy += 1
            self.dangle += math.pi / 4
        if self.keys[2]:
            self.dx -= 1
        if self.keys[3]:
            self.dx += 1

    async def on_collision(self, other: Collider, *, jump: bool=False) -> Action | None:
        if isinstance(other, Foe):
            AudioBag.explosions[1].play()
            return Action.remove(self, other)
