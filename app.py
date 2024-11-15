import asyncio
from typing import Coroutine, NoReturn
import pygame
from pygame import Surface
from pygame.constants import K_ESCAPE
from pygame.time import Clock

from action import Action, Actor, AddActor, Collider, RemoveActor
from consts import BACKGROUND, FPS, RESOLUTION
from fps import FpsDisplay
from player import Player
from spawner import Spawner


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
            Spawner(),
            FpsDisplay(),
            Player(),
        ))

    async def check_collisions(self) -> list[Action]:
        colliders: list[Collider] = [
            actor for actor in self.actors
            if isinstance(actor, Collider)
        ]
        futures: list[Coroutine] = [
            actor1.collide(actor2)
            for i, actor1 in enumerate(colliders[:len(colliders)-2])
            for actor2 in colliders[i+1:]
            if actor1.is_colliding(actor2)
        ]
        actions: list[Action] = await asyncio.gather(*futures)
        return [
            action for action in actions
            if action is not Action.noAction
        ]

    async def update(self) -> None:
        delta: float = self.clock.tick(FPS) / 1000
        actions = await asyncio.gather(*[actor.update(delta) for actor in self.actors])
        actions.extend(await self.check_collisions())
        for action in actions:
            if isinstance(action, AddActor):
                for actor in action.actors:
                    self.actors.insert(0, actor)
            elif isinstance(action, RemoveActor):
                for actor in action.actors:
                    self.actors.remove(actor)

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
