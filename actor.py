from pygame import Surface
from pygame.event import Event


class Actor:

    async def update(self, delta: float) -> None:
        ...

    async def draw(self, surface: Surface) -> None:
        ...

    async def react(self, events: list[Event]) -> None:
        ...
