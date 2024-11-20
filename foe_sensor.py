from typing import Protocol
from action import Collider


class Foe(Protocol):
    x: float
    y: float
    dy: float


class FoeSensor(Collider):
    def __init__(self, foe: Foe) -> None:
        self.foe = foe

    @property
    def xy(self) -> tuple[float, float]:
        return self.foe.x - 100, self.foe.y

    @property
    def radius(self) -> float:
        return 100

    async def on_collision(self, other: Collider) -> None:
        if other is self.foe:
            return

        from player import Player
        from foe import Foe
        from meteor import Meteor

        if isinstance(other, (Foe, Meteor, Player)):
            dy = 80 if isinstance(other, Player) else -80
            _, y = other.xy
            if y < self.foe.y:
                self.foe.dy -= dy
            else:
                self.foe.dy += dy
