import math
from typing import Any, Callable, Iterable
from pygame import Surface
from pygame.event import Event


class Action:

    noAction: 'Action'

    @staticmethod
    def register(*actors: 'Actor') -> 'Action':
        return AddActor(actors)

    @staticmethod
    def remove(*actors: 'Actor') -> 'Action':
        return RemoveActor(actors)

Action.noAction = Action()


class RemoveActor(Action):

    def __init__(self, actors: Iterable['Actor']) -> None:
        self.actors = actors


class AddActor(Action):

        def __init__(self, actors: Iterable['Actor']) -> None:
            self.actors = actors


class Actor:

    @property
    def pos(self) -> tuple[int, int]:
        x, y = self.xy
        return int(x), int(y)

    @property
    def radius(self) -> float:
        ...

    @property
    def xy(self) -> tuple[float, float]:
        ...

    async def update(self, delta: float) -> Action:
        return Action.noAction

    async def draw(self, surface: Surface) -> None:
        ...

    async def react(self, events: list[Event]) -> None:
        ...

    def squared_distance(self, other: 'Actor') -> float:
        x0, y0 = self.xy
        x1, y1 = other.xy
        dx, dy = x0 - x1, y0 - y1
        return dx*dx + dy*dy

    def distance(self, other: 'Actor') -> float:
        return math.sqrt(self.squared_distance(other))


class Collider(Actor):

    def is_colliding(self, other: 'Collider') -> bool:
        return self.distance(other) <= self.radius + other.radius

    async def on_collision(self, other: 'Collider', *, jump: bool=False) -> Action | None:
        if jump:
            return
        return await other.on_collision(self, jump=True)


class DarkMatter(Actor):

    @property
    def radius(self) -> float:
        return 0

    @property
    def xy(self) -> tuple[float, float]:
        return 1 << 32, 1 << 32
