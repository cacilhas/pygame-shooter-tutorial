import math
from types import ModuleType
from typing import Any, Callable, Iterable
from pygame import Surface
from pygame.event import Event


class Action:

    class _types(ModuleType):
        ActionSet: 'type[__ActionSet]'
        AddActor: 'type[__AddActor]'
        IncrScore: 'type[__IncrScore]'
        RemoveActor: 'type[__RemoveActor]'

    @classmethod
    def register(cls, *actors: 'Actor') -> 'Action':
        return cls._types.AddActor(actors)

    @classmethod
    def remove(cls, *actors: 'Actor') -> 'Action':
        return cls._types.RemoveActor(actors)

    @classmethod
    def set(cls, *actions: 'Action') -> 'Action':
        return cls._types.ActionSet(actions)

    @classmethod
    def incr_score(cls, value: int) -> 'Action':
        return cls._types.IncrScore(value)


class __RemoveActor(Action):

    def __init__(self, actors: Iterable['Actor']) -> None:
        self.actors = actors

Action._types.RemoveActor = __RemoveActor


class __AddActor(Action):

    def __init__(self, actors: Iterable['Actor']) -> None:
        self.actors = actors

Action._types.AddActor = __AddActor


class __IncrScore(Action):

    def __init__(self, value: int) -> None:
        self.value = value

Action._types.IncrScore = __IncrScore


class __ActionSet(Action):

    def __init__(self, actions: Iterable[Action]) -> None:
        self.actions = actions

Action._types.ActionSet = __ActionSet


class Actor:

    @property
    def pos(self) -> tuple[int, int]:
        x, y = self.xy
        return int(x), int(y)

    @property
    def radius(self) -> float:
        return 0

    @property
    def xy(self) -> tuple[float, float]:
        return 1 << 32, 1 << 32

    async def update(self, delta: float) -> Action | None:
        ...

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
