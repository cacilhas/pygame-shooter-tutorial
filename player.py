import math
from typing import Optional
import pygame
from pygame import Surface
from pygame.event import Event
from action import Action, Collider
from consts import RESOLUTION
from enemy_fire import EnemyFire
from explosion import Explosion
from fire import Fire
from foe import Foe
from foe_force_field import FoeForceField
from meteor import Meteor
from shield import Shield
from sounds import AudioBag
from util import async_gen


class Player(Collider):
    facet: Surface

    @classmethod
    def load_assets(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load("assets/player.png").convert_alpha(),
            (64, 64),
        )

    def __init__(self) -> None:
        if not hasattr(Player, "facet"):
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
        self._power: int = 0
        self.previous_power: int = 0
        self.shots: int = 0
        self.shield: Optional[Shield] = None
        self.may_spawn_shield: float = 0.0

    @property
    def radius(self) -> float:
        return 28

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def power(self) -> int:
        return self._power

    @power.setter
    def power(self, value: int) -> None:
        if self._power not in [value, 4]:
            self.previous_power = self._power
        if value == 4:
            self.shots = 5
        self.no_fire = 0.0
        self._power = value

    async def draw(self, surface: Surface) -> None:
        facet = pygame.transform.rotate(
            self.facet,
            -self.angle * 180 / math.pi,
        )
        self.blit(dest=surface, src=facet)

    async def update(self, delta: float) -> Optional[Action]:
        self.no_fire = max([0, self.no_fire - delta])
        self.x += self.speed * self.dx * delta
        self.y += self.speed * self.dy * delta
        self.angle += (self.dangle - self.angle) * delta * 4
        self.x = max([0, min([RESOLUTION[0] * 2 / 3, self.x])])
        self.y = max([0, min([RESOLUTION[1], self.y])])
        self.angle = max([-math.pi / 4, min(math.pi / 4, self.angle)])

        actions: list[Action] = []
        if self.shield is None:
            actions.append(Action.spawn_shield())

        if self.keys[4] and self.no_fire == 0:
            fire = Fire(self.xy, self.angle, power=self.power)
            self.no_fire = fire.delay
            actions.append(Action.register(fire))
            if self.power == 4:
                self.shots -= 1
                if self.shots <= 0:
                    actions.append(Action.play_audio(AudioBag.power_down))
                    self._power = self.previous_power
                    self.no_fire = 0.5

        if len(actions) == 1:
            return actions[0]
        elif actions:
            return Action.set(*actions)

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

    async def on_collision(self, other: Collider) -> Optional[Action]:
        if isinstance(other, (EnemyFire, Foe, FoeForceField, Meteor)):
            actions = [
                Action.remove(self),
                Action.register(Explosion(pos=self.pos, size=120)),
                Action.player_hit(),
            ]
            if self.shield:
                actions.append(Action.remove(self.shield))
            return Action.set(*actions)

        from powerup import PowerUp

        if isinstance(other, PowerUp):
            if other.power < 4:
                self.power = other.power

            elif other.power == 4:
                self.previous_power = self.power
                self.power = 4

            elif other.power == 5:
                return Action.register(Fire(self.pos, 0, power=5))

            elif other.power == PowerUp.shield:
                old = self.shield
                shield = Shield(self)
                if old:
                    return Action.set(
                        Action.remove(old),
                        Action.register(shield),
                    )
                else:
                    return Action.register(shield)
