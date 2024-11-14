import pygame
from pygame.event import Event
from pygame.font import Font
from pygame.surface import Surface
from actor import Action, Actor


class FpsDisplay(Actor):

    def __init__(self) -> None:
        self.font = Font('assets/digital-7.ttf', 24)
        self.text = 'FPS: 0.0'
        self.present = False

    async def update(self, delta: float) -> Action:
        fps = 1 / delta
        self.text = f'FPS: {fps:.1f}'
        return Action.noAction

    async def react(self, events: list[Event]) -> None:
        for event in events:
            if event.type == pygame.KEYUP and event.key == pygame.K_F2:
                self.present = not self.present
                return

    async def draw(self, surface: Surface) -> None:
        if self.present:
            text = self.font.render(self.text, True, 'black')
            x = surface.get_width() - text.get_width() - 5
            surface.blit(text, (x, 5))
