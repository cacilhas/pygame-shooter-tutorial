import asyncio
import math
from types import ModuleType
from typing import Any, Callable, Iterable, Type, TypeIs
from pygame import Surface
from pygame.event import Event
from pygame.mixer import Sound


#---------#---------------------------------------------------------------------
# Actions #
#---------#

class Action:

    __ActionSet: 'type[__ActionSet]'
    __AddActor: 'type[__AddActor]'
    __DecreaseLives: 'type[__DecreaseLives]'
    __ForEach: 'type[__ForEach]'
    __IncrScore: 'type[__IncrScore]'
    __PlayAudio: 'type[__PlayAudio]'
    __PlayerHit: 'type[__PlayerHit]'
    __RemoveActor: 'type[__RemoveActor]'
    __RemoveIf: 'type[__RemoveIf]'

    #-----#

    @classmethod
    def decr_lives(cls) -> 'Action':
        return cls.__DecreaseLives()

    @classmethod
    def for_each(cls, cb: Callable[['Actor'], 'Action | None']):
        return cls.__ForEach(cb)

    @classmethod
    def incr_score(cls, value: int) -> 'Action':
        return cls.__IncrScore(value)

    @classmethod
    def play_audio(cls, audio: Sound) -> 'Action':
        return cls.__PlayAudio(audio)

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
    def remove_if(cls, cb: Callable[['Actor'], bool]) -> 'Action':
        return cls.__RemoveIf(cb)

    @classmethod
    def set(cls, *actions: 'Action') -> 'Action':
        return cls.__ActionSet(actions)

    #-----#

    @classmethod
    def isDecreaseLives(cls, action) -> TypeIs['__DecreaseLives']:
        return isinstance(action, cls.__DecreaseLives)

    @classmethod
    def isActionSet(cls, action) -> TypeIs['__ActionSet']:
        return isinstance(action, cls.__ActionSet)

    @classmethod
    def isAddActor(cls, action) -> TypeIs['__AddActor']:
        return isinstance(action, cls.__AddActor)

    @classmethod
    def isForEach(cls, action) -> TypeIs['__ForEach']:
        return isinstance(action, cls.__ForEach)

    @classmethod
    def isIncrScore(cls, action) -> TypeIs['__IncrScore']:
        return isinstance(action, cls.__IncrScore)

    @classmethod
    def isPlayAudio(cls, action) -> TypeIs['__PlayAudio']:
        return isinstance(action, cls.__PlayAudio)

    @classmethod
    def isPlayerHit(cls, action) -> TypeIs['__PlayerHit']:
        return isinstance(action, cls.__PlayerHit)

    @classmethod
    def isRemoveActor(cls, action) -> TypeIs['__RemoveActor']:
        return isinstance(action, cls.__RemoveActor)

    @classmethod
    def isRemoveIf(cls, action) -> TypeIs['__RemoveIf']:
        return isinstance(action, cls.__RemoveIf)

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
class __DecreaseLives(Action):

    ...


@register_subclass
class __ForEach(Action):

    # TODO: make it async
    def __init__(self, cb: Callable[['Actor'], Action | None]) -> None:
        self.cb = cb


@register_subclass
class __IncrScore(Action):

    def __init__(self, value: int) -> None:
        self.value = value


@register_subclass
class __PlayAudio(Action):

    def __init__(self, audio: Sound) -> None:
        self.audio = audio


@register_subclass
class __PlayerHit(Action):

    ...


@register_subclass
class __RemoveActor(Action):

    def __init__(self, actor: 'Actor') -> None:
        self.actor = actor


@register_subclass
class __RemoveIf(Action):
    def __init__(self, cb: Callable[['Actor'], bool]) -> None:
        self.check = cb


ActionPair = tuple[Action | None, Action | None]


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

    async def on_close(self) -> Action | None:
        ...


class Collider(Actor):

    def is_colliding(self, other: 'Collider') -> bool:
        return self.distance(other) <= self.radius + other.radius

    async def on_collision(self, other: 'Collider') -> Action | None:
        ...

    async def _process_collision(self, other: 'Collider') -> ActionPair:
        return await asyncio.gather(
            self.on_collision(other),
            other.on_collision(self),
        )
