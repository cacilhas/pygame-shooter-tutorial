import math
from types import ModuleType
from typing import Any, Callable, Iterable, TypeIs
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

    @classmethod
    def isActionSet(cls, actor) -> 'TypeIs[__ActionSet]':
        return isinstance(actor, cls._types.ActionSet)

    @classmethod
    def isAddActor(cls, actor) -> 'TypeIs[__AddActor]':
        return isinstance(actor, cls._types.AddActor)

    @classmethod
    def isIncrScore(cls, actor) -> 'TypeIs[__IncrScore]':
        return isinstance(actor, cls._types.IncrScore)

    @classmethod
    def isRemoveActor(cls, actor) -> 'TypeIs[__RemoveActor]':
        return isinstance(actor, cls._types.RemoveActor)

    def __len__(self) -> int:
        return 1


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

    def blit(self, *, dest: Surface, src: Surface) -> None:
        x, y = self.pos
        width, height = src.get_size()
        dest.blit(src, (x - width/2, y - height/2))

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

    async def on_collision(self, other: 'Collider') -> Action | None:
        ...

    async def _process_collision(self, other: 'Collider') -> Action | None:
        action = await self.on_collision(other)
        if action:
            return action
        return await other.on_collision(self)
