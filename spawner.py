from random import randint, random
from action import Action, Actor
from consts import RESOLUTION
from foe import Foe


class Spawner(Actor):

    def __init__(self) -> None:
        self.wait_time: float = 0.0
        self.max_wait_time: float = 5.0

    async def update(self, delta: float) -> Action | None:
        self.wait_time -= delta
        self.wait_time = max(0.0, self.wait_time)
        if self.wait_time == 0:
            if self.max_wait_time > 0:
                self.wait_time = random() * self.max_wait_time
                self.max_wait_time = max(0, self.max_wait_time - 0.06125)
            y = randint(10, RESOLUTION[1] - 10)
            speed = 200 + random() * 200
            return Action.register(Foe(y, speed))
