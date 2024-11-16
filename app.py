import asyncio
import random
import sys
from typing import Coroutine, DefaultDict, Iterable, NoReturn, TypeIs
import pygame
from pygame import Surface
from pygame.constants import K_ESCAPE, K_PAUSE, KEYUP
from pygame.time import Clock

from action import Action, Actor, Collider
from consts import BACKGROUND, FPS, RESOLUTION
from fps import FpsDisplay
from gameover import GameOver
from life import Lives
from paused import Paused
from player import Player
from reload import Reload
from score import Score
from sounds import AudioBag
from spawner import FoeSpawner, MeteorSpawner, PowerUpSpawner
from stars import StarsBackground


class App:

    def __init__(self) -> None:
        random.seed()
        pygame.init()
        AudioBag.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption('Simple PyGame Shooter')
        self.screen: Surface = pygame.display.set_mode(
            RESOLUTION,
            pygame.DOUBLEBUF
            | pygame.FULLSCREEN
            | pygame.SCALED,
            vsync=1,
        )
        self.paused_display = Paused()

    def populate(self) -> None:
        """
        Add actors to the world
        """
        self.actors.extend((
            StarsBackground(),
            FoeSpawner(),
            PowerUpSpawner(),
            MeteorSpawner(),
            FpsDisplay(),
            Score(self),
            Player(),
            Lives(self),
        ))

    async def check_collisions(self) -> Iterable[Action]:
        """
        Instantiate all collision objects
        """
        colliders: list[Collider] = [
            actor for actor in self.actors
            if isinstance(actor, Collider)
        ]
        if len(colliders) < 2:
            return []

        futures: list[Coroutine[None, None, Action | None]] = [
            actor1._process_collision(actor2)
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
        if not self.paused:
            actions: list[Action | None] = await asyncio.gather(*(
                actor.update(delta)
                for actor in self.actors
            ))
            actions.extend(await self.check_collisions())
            await asyncio.gather(*(
                self.process(action)
                for action in actions
                if action
            ))

    async def process(self, action: Action) -> None:
        """
        Process all collected actions
        """
        if Action.isActionSet(action):
            await asyncio.gather(*(self.process(a) for a in action.actions))
            return

        if Action.isAddActor(action):
            self.actors.insert(0, action.actor)
            return

        if Action.isDecreaseLives(action):
            self.lives -= 1
            return

        if Action.isPlayerHit(action):
            if self.lives <= 1:
                self.lives -= 1
                self.actors.append(GameOver())
                self.game_over = True
            else:
                self.actors.append(Reload())
            return

        if Action.isIncrScore(action):
            self.score += action.value
            return

        if Action.isRemoveActor(action):
            try:
                self.actors.remove(action.actor)
            except ValueError:
                print(sys.stderr, f'{action.actor} was supposed to be in the actors list')
            return

        if Action.isRemoveIf(action):
            actors: list[Actor] = []
            for actor in self.actors:
                if not action.check(actor):
                    actors.append(actor)
            self.actors = actors

    async def draw(self) -> None:
        """
        Draw actors on overlapped layers by z-axis
        """
        self.screen.fill(BACKGROUND)
        layers: dict[int, Surface] = DefaultDict(lambda: Surface(RESOLUTION, pygame.SRCALPHA))
        # Asynchronous drawing
        await asyncio.gather(*(actor.draw(layers[actor.z]) for actor in self.actors))
        # Synchronous drawing
        for _, layer in sorted((pair for pair in layers.items()), key=lambda pair: pair[0]):
            self.screen.blit(layer, (0, 0))
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
            elif self.game_over and event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
                self.reset = True
            elif (not self.game_over) and event.type == pygame.KEYUP and event.key in [pygame.K_p, pygame.K_PAUSE]:
                self.paused = not self.paused
                if self.paused:
                    self.actors.append(self.paused_display)
                else:
                    self.actors.remove(self.paused_display)
        await asyncio.gather(*(actor.react(events) for actor in self.actors))

    async def start(self) -> NoReturn:
        while True:
            self.clock = Clock()
            self.score: int = 0
            self.actors: list[Actor] = []
            self.lives: int = 3
            self.reset: bool = False
            self.game_over: bool = False
            self.paused: bool = False
            self.populate()

            while not self.reset:
                await self.events()
                await self.update()
                await self.draw()
