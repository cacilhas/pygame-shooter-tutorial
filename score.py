from typing import Protocol
from pygame.font import Font
from pygame.surface import Surface
from action import Action, Actor


class App(Protocol):

    score: int


class Score(Actor):

    def __init__(self, app: App) -> None:
        self.app = app
        self.font = Font('assets/digital-7.ttf', 24)
        self.text = 'Score: 0'

    async def update(self, delta: float) -> Action | None:
        self.text = f'Score: {self.app.score:4d}'

    async def draw(self, surface: Surface) -> None:
        text = self.font.render(self.text, True, 'white')
        surface.blit(text, (5, 5))
