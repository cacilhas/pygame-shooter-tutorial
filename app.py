import asyncio
from typing import NoReturn
import pygame
from pygame import Surface
from pygame.constants import K_ESCAPE
from pygame.time import Clock

from actor import Actor, AddActor, RemoveActor
from consts import BACKGROUND, FPS, RESOLUTION
from fps import FpsDisplay
from player import Player


class App:

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self.screen: Surface = pygame.display.set_mode(
            RESOLUTION,
            pygame.NOFRAME | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption('Shooter Tutorial')
        self.clock = Clock()
        self.actors: list[Actor] = []
        self.populate()

    def populate(self) -> None:
        self.actors.extend((
            FpsDisplay(),
            Player(),
        ))

    async def update(self) -> None:
        delta: float = self.clock.tick(FPS) / 1000
        actions = await asyncio.gather(*[actor.update(delta) for actor in self.actors])
        for action in actions:
            response = action.perform()
            if isinstance(response, AddActor):
                self.actors.insert(0, response.actor)
            elif isinstance(response, RemoveActor):
                self.actors.remove(response.actor)

    async def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        await asyncio.gather(*[actor.draw(self.screen) for actor in self.actors])
        pygame.display.flip()

    async def events(self) -> None:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                import sys
                pygame.quit()
                sys.exit()
        await asyncio.gather(*[actor.react(events) for actor in self.actors])

    async def start(self) -> NoReturn:
        while True:
            await self.events()
            await self.update()
            await self.draw()
