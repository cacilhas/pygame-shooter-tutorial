import asyncio
import sys
from typing import Coroutine, Iterable, NoReturn, TypeIs
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
        pygame.display.set_caption('Simple PyGame Shooter')
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
        """
        Add actors to the world
        """
        self.actors.extend((
            Spawner(),
            FpsDisplay(),
            Score(self),
            Player(),
        ))

    async def check_collisions(self) -> Iterable[Action]:
        """
        Instantiate all collision action objects
        """
        colliders: list[Collider] = [
            actor for actor in self.actors
            if isinstance(actor, Collider)
        ]
        if len(colliders) < 2:
            return []

        async def process_collision(actor1: Collider, actor2: Collider) -> Action | None:
            action = await actor1.on_collision(actor2)
            if action:
                return action
            return await actor2.on_collision(actor1)

        futures: list[Coroutine[None, None, Action | None]] = [
            process_collision(actor1, actor2)
            for i, actor1 in enumerate(colliders[:len(colliders)-1])
            for actor2 in colliders[i+1:]
            if actor1.is_colliding(actor2)
        ]
        return [action for action in await asyncio.gather(*futures) if action]

    async def update(self) -> None:
        """
        Perform update for all actors and collect their actions
        """
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
        """
        Process all collcted actions
        """
        if Action.isActionSet(action):
            async for a in async_gen(action.actions):
                await self.process(a)

        if Action.isAddActor(action):
            for actor in action.actors:
                self.actors.insert(0, actor)
            return

        if Action.isIncrScore(action):
            self.score += action.value

        if Action.isRemoveActor(action):
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
        """
        Process global events and delegate object dedicated events
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                import sys
                pygame.quit()
                sys.exit()
        async for actor in async_gen(self.actors):
            await actor.react(events)

    async def start(self) -> NoReturn:
        while True:
            await self.events()
            await self.update()
            await self.draw()
