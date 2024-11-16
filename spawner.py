from random import randint, random
from action import Action, Actor
from consts import RESOLUTION
from foe import Foe
from powerup import PowerUp


class FoeSpawner(Actor):

    def __init__(self) -> None:
        self.wait_time: float = 0.0
        self.max_wait_time: float = 5.0
        self.reset: float | None = None

    async def update(self, delta: float) -> Action | None:
        self.wait_time -= delta
        self.wait_time = max(0.0, self.wait_time)

        if self.wait_time == 0:
            self.wait_time = random() * self.max_wait_time
            self.max_wait_time = max(0.25, self.max_wait_time - 0.06125)
            if self.reset is None and self.max_wait_time == 0.25:
                self.reset = 20.0
            y = randint(10, RESOLUTION[1] - 10)
            speed = 200 + random() * 200
            return Action.register(Foe(y, speed))

        if self.reset:
            self.reset -= delta
            if self.reset <= 0:
                self.reset = None
                self.max_wait_time = 5.0
                self.wait_time = 5.0
                return Action.incr_score(100)


class PowerUpSpawner(Actor):

    def __init__(self) -> None:
        self.min_wait_time: float = 10.0
        self.max_wait_time: float = 20.0
        self.wait_time: float = self.min_wait_time

    async def update(self, delta: float) -> Action | None:
        self.wait_time -= delta
        self.wait_time = max(0.0, self.wait_time)
        if self.wait_time == 0:
            self.wait_time = self.min_wait_time + random() * (self.max_wait_time - self.max_wait_time)
            y = randint(24, RESOLUTION[1] - 24)
            speed = 50 + random() * 50
            return Action.register(PowerUp(y, speed))
