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
        ...

    async def update(self, delta: float) -> Action:
        return Action.noAction

    async def draw(self, surface: Surface) -> None:
        ...

    async def react(self, events: list[Event]) -> None:
        ...
