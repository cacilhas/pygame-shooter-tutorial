import math
from types import ModuleType
from typing import Any, Callable, Iterable, Type, TypeIs
from pygame import Surface
from pygame.event import Event


#---------#---------------------------------------------------------------------
# Actions #
#---------#

class Action:

    __ActionSet: 'type[__ActionSet]'
    __AddActor: 'type[__AddActor]'
    __IncrScore: 'type[__IncrScore]'
    __PlayerHit: 'type[__PlayerHit]'
    __RemoveActor: 'type[__RemoveActor]'

    #-----#

    @classmethod
    def incr_score(cls, value: int) -> 'Action':
        return cls.__IncrScore(value)

    @classmethod
    def player_hit(cls) -> 'Action':
        return cls.__PlayerHit()

    @classmethod
    def register(cls, actor: 'Actor') -> 'Action':
        return cls.__AddActor(actor)

    @classmethod
    def remove(cls, actor: 'Actor') -> 'Action':
        return cls.__RemoveActor(actor)

    @classmethod
    def set(cls, *actions: 'Action') -> 'Action':
        return cls.__ActionSet(actions)

    #-----#

    @classmethod
    def isActionSet(cls, actor) -> 'TypeIs[__ActionSet]':
        return isinstance(actor, cls.__ActionSet)

    @classmethod
    def isAddActor(cls, actor) -> 'TypeIs[__AddActor]':
        return isinstance(actor, cls.__AddActor)

    @classmethod
    def isIncrScore(cls, actor) -> 'TypeIs[__IncrScore]':
        return isinstance(actor, cls.__IncrScore)

    @classmethod
    def isPlayerHit(cls, actor) -> 'TypeIs[__PlayerHit]':
        return isinstance(actor, cls.__PlayerHit)

    @classmethod
    def isRemoveActor(cls, actor) -> 'TypeIs[__RemoveActor]':
        return isinstance(actor, cls.__RemoveActor)

    def __len__(self) -> int:
        return 1


def register_subclass[T](cls: type[T]) -> type[T]:
    setattr(Action, f'_{Action.__name__}{cls.__name__}', cls)
    return cls


@register_subclass
class __ActionSet(Action):

    def __init__(self, actions: Iterable[Action]) -> None:
        self.actions = actions


@register_subclass
class __AddActor(Action):

    def __init__(self, actor: 'Actor') -> None:
        self.actor = actor


@register_subclass
class __IncrScore(Action):

    def __init__(self, value: int) -> None:
        self.value = value


@register_subclass
class __PlayerHit(Action):

    ...

@register_subclass
class __RemoveActor(Action):

    def __init__(self, actor: 'Actor') -> None:
        self.actor = actor


#--------#----------------------------------------------------------------------
# Actors #
#--------#

class Actor:

    z: int = 0

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
