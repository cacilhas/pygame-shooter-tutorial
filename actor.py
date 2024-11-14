from typing import Any, Callable
from pygame import Surface
from pygame.event import Event


class RemoveActor:

    def __init__(self, actor: 'Actor') -> None:
        self.actor = actor


class AddActor:

        def __init__(self, actor: 'Actor') -> None:
            self.actor = actor


class Action[T]:

    noAction: 'Action[None]'

    def __init__(self, callback: Callable[..., T]):
        self.callback = callback

    @staticmethod
    def register(actor: 'Actor') -> 'Action[AddActor]':
        return Action(lambda: AddActor(actor))

    @staticmethod
    def remove(actor: 'Actor') -> 'Action[RemoveActor]':
        return Action(lambda: RemoveActor(actor))

    def perform(self) -> T:
        return self.callback()

Action.noAction = Action(lambda: None)


class Actor:

    @property
    def pos(self) -> tuple[int, int]:
        ...

    async def update(self, delta: float) -> 'Action':
        ...

    async def draw(self, surface: Surface) -> None:
        ...

    async def react(self, events: list[Event]) -> None:
        ...
