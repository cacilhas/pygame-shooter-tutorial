import math
import pygame
from pygame import Surface
from pygame.event import Event
from action import Action, Collider
from consts import RESOLUTION
from explosion import Explosion
from fire import Fire
from foe import Foe
from meteor import Meteor
from util import async_gen


class Player(Collider):

    facet: Surface

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/player.png').convert_alpha(),
            (64, 64),
        )

    def __init__(self) -> None:
        if not hasattr(Player, 'facet'):
            Player.load_assets()

        pygame.display.set_icon(self.facet)
        self.z = 10
        self.keys: list[bool] = [False] * 5
        self.speed: float = 400.0
        self.no_fire = 0.0
        self.x: float = RESOLUTION[0] / 4
        self.y: float = RESOLUTION[1] / 2
        self.dx: float = 0.0
        self.dy: float = 0.0
        self.dangle: float = 0.0
        self.angle: float = 0.0
        self.power: int = 0

    @property
    def radius(self) -> float:
        return 28

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    async def draw(self, surface: Surface) -> None:
        facet = pygame.transform.rotate(
            self.facet,
            -self.angle * 180 / math.pi,
        )
        self.blit(dest=surface, src=facet)

    async def update(self, delta: float) -> Action | None:
        self.no_fire = max([0, self.no_fire - delta])
        self.x += self.speed * self.dx * delta
        self.y += self.speed * self.dy * delta
        self.angle += (self.dangle - self.angle) * delta * 4
        self.x = max([0, min([RESOLUTION[0] * 2/3, self.x])])
        self.y = max([0, min([RESOLUTION[1], self.y])])
        self.angle = max([-math.pi/4, min(math.pi/4, self.angle)])

        if self.keys[4] and self.no_fire == 0:
            fire = Fire(self.xy, self.angle, power=self.power)
            self.no_fire = fire.delay
            return Action.register(fire)

    async def react(self, events: list[Event]) -> None:
        async for event in async_gen(ev for ev in events if ev.type == pygame.KEYUP):
            match event.key:
                case pygame.K_UP | pygame.K_w:
                    self.keys[0] = False
                case pygame.K_DOWN | pygame.K_s:
                    self.keys[1] = False
                case pygame.K_LEFT | pygame.K_a:
                    self.keys[2] = False
                case pygame.K_RIGHT | pygame.K_d:
                    self.keys[3] = False
                case pygame.K_SPACE | pygame.K_LCTRL:
                    self.keys[4] = False

        async for event in async_gen(ev for ev in events if ev.type == pygame.KEYDOWN):
            match event.key:
                case pygame.K_UP | pygame.K_w:
                    self.keys[0] = True
                case pygame.K_DOWN | pygame.K_s:
                    self.keys[1] = True
                case pygame.K_LEFT | pygame.K_a:
                    self.keys[2] = True
                case pygame.K_RIGHT | pygame.K_d:
                    self.keys[3] = True
                case pygame.K_SPACE | pygame.K_LCTRL:
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

    async def on_collision(self, other: Collider) -> Action | None:
        if isinstance(other, Foe):
            return Action.set(
                Action.remove(self),
                Action.remove(other),
                Action.register(Explosion(pos=self.pos, size=120)),
                Action.player_hit(),
            )
        if isinstance(other, Meteor):
            return Action.set(
                Action.remove(self),
                Action.register(Explosion(pos=self.pos, size=120)),
                Action.player_hit(),
            )
