from random import randint, random
from action import Action, Actor
from consts import RESOLUTION
from foe import Foe


class Spawner(Actor):

    async def update(self, delta: float) -> Action:
        if random() < 2 ** -7:
            y = randint(10, RESOLUTION[1] - 10)
            speed = 200 + random() * 200
            return Action.register(Foe(y, speed))
        return Action.noAction
