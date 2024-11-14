from pygame import Surface
from pygame.event import Event


class Actor:

    def update(self, delta: float) -> None:
        ...

    def draw(self, surface: Surface) -> None:
        ...

    def react(self, events: list[Event]) -> None:
        ...
