import asyncio
import sys
from typing import Coroutine, NoReturn
import pygame
from pygame import Surface
from pygame.constants import K_ESCAPE
from pygame.time import Clock

from action import Action, Actor, Collider
from consts import BACKGROUND, FPS, RESOLUTION
from fps import FpsDisplay
from player import Player
from score import Score
from sounds import AudioBag
from spawner import Spawner
from util import async_gen


class App:

    def __init__(self) -> None:
        pygame.init()
        AudioBag.init()
        pygame.display.set_caption('Shooter Tutorial')
        self.screen: Surface = pygame.display.set_mode(
            RESOLUTION,
            pygame.DOUBLEBUF
            | pygame.FULLSCREEN
            | pygame.SCALED,
            vsync=1,
        )
        self.clock = Clock()
        self.score: int = 0
        self.actors: list[Actor] = []
        self.populate()

    def populate(self) -> None:
        self.actors.extend((
            Spawner(),
            FpsDisplay(),
            Score(self),
            Player(),
        ))

    async def check_collisions(self) -> list[Action]:
        colliders: list[Collider] = [
            actor for actor in self.actors
            if isinstance(actor, Collider)
        ]
        futures: list[Coroutine] = [
            actor1.on_collision(actor2)
            for i, actor1 in enumerate(colliders[:len(colliders)-2])
            for actor2 in colliders[i+1:]
            if actor1.is_colliding(actor2)
        ]
        return [
            action
            for action in await asyncio.gather(*futures)
            if action
        ]

    async def update(self) -> None:
        delta: float = self.clock.tick(FPS) / 1000
        actions: list[Action | None] = await asyncio.gather(*(
            actor.update(delta)
            for actor in self.actors
        ))
        actions.extend(await self.check_collisions())
        async for action in async_gen(actions):
            if action:
                await self.process(action)

    async def process(self, action: Action) -> None:
        if isinstance(action, Action._types.ActionSet):
            async for a in async_gen(action.actions):
                await self.process(a)

        if isinstance(action, Action._types.AddActor):
            for actor in action.actors:
                self.actors.insert(0, actor)
            return

        if isinstance(action, Action._types.IncrScore):
            self.score += action.value

        if isinstance(action, Action._types.RemoveActor):
            for actor in action.actors:
                try:
                    self.actors.remove(actor)
                except ValueError:
                    print(sys.stderr, f'{actor} was supposed to be in the actors list')
            return

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
