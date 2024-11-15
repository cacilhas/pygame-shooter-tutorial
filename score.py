from asyncio.protocols import Protocol

from pygame.font import Font
from action import Action, Actor


class App(Protocol):

    score: int


class Score(Actor):

    def __init__(self, app: App) -> None:
        self.app = app
        self.font = Font('assets/digital-7.ttf', 24)
        self.text = 'FPS: 0.0'

    async def update(self, delta: float) -> Action | None:
        ...
