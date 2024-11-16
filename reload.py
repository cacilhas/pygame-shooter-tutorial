from action import Action, Actor, Collider
from player import Player


class Reload(Actor):

    def __init__(self) -> None:
        self.delay: float = 3.0

    async def update(self, delta: float) -> Action | None:
        self.delay -= delta
        if self.delay <= 0:
            return Action.set(
                Action.remove(self),
                Action.register(Player()),
            )
        return Action.remove_if(lambda actor: isinstance(actor, Collider))
