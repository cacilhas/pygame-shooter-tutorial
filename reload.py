from typing import Optional
from action import Action, Actor
from enemy_fire import EnemyFire
from foe import Foe
from meteor import Meteor
from player import Player


class Reload(Actor):

    def __init__(self) -> None:
        self.delay: float = 3.0

    async def update(self, delta: float) -> Optional[Action]:
        self.delay -= delta
        if self.delay <= 0:
            return Action.set(
                Action.remove(self),
                Action.decr_lives(),
                Action.remove_if(lambda actor: isinstance(actor, (EnemyFire, Foe, Meteor))),
                Action.register(Player()),
            )
