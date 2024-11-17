from math import isinf
from random import randint, random

from pygame import Surface
import pygame
from pygame.font import Font
from pygame.mixer import Sound
from action import Action, Actor, Collider
from consts import RESOLUTION
from player import Player
from sounds import AudioBag


class PowerUp(Collider):

    facets: list[Surface] = []

    @classmethod
    def load_assets(cls) -> None:
        font = Font('assets/digital-7.ttf', 48)
        for i, color in enumerate(colors):
            facet = Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(facet, color[0], (24, 24), 24)
            text = font.render(str(i), True, color[1])
            facet.blit(text, (text.get_width()/2, 4))
            cls.facets.append(facet)

    def __init__(self, y: float, speed: float) -> None:
        if not self.facets:
            self.load_assets()

        power: int = 0
        match randint(0, 11):
            case 0:
                power = 0
            case 1 | 2 | 3 | 4:
                power = 1
            case 5 | 6 | 7:
                power = 2
            case 8 | 9:
                power = 3
            case 10:
                power = 4
            case 11:
                power = 5

        self.facet = self.facets[power]
        self.power = power

        self.x = RESOLUTION[0] + self.facet.get_width() / 2
        self.y = y
        self.speed = speed

    @property
    def xy(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def radius(self) -> float:
        return 24

    async def update(self, delta: float) -> Action | None:
        self.x -= self.speed * delta
        if self.x < -self.facet.get_width():
            return Action.remove(self)

    async def draw(self, surface: Surface) -> None:
        return self.blit(dest=surface, src=self.facet)

    async def on_collision(self, other: Collider) -> Action | None:
        if isinstance(other, Player):
            player: Player = other
            audio: Sound

            if player.power < self.power and self.power != 5:
                audio = AudioBag.power_up
            elif player.power > self.power:
                audio = AudioBag.power_down
            elif self.power == 5:
                audio = AudioBag.explosions[1]
            else:
                audio = AudioBag.catch

            actions: list[Action] = [
                Action.remove(self),
                Action.play_audio(audio),
            ]

            score_up = 100 if self.power == 0 else 20 + self.power * 10
            actions.append(Action.incr_score(score_up))

            if self.power == 5:
                from fire import Fire
                from foe import Foe
                from meteor import Meteor
                def scoreit(actor: Actor) -> Action | None:
                    if isinstance(actor, (Foe, Meteor)):
                        return Action.set(
                            Action.incr_score(10),
                            Action.remove(actor),
                        )
                actions.extend([
                    Action.for_each(scoreit),
                    Action.register(Fire(self.pos, 0, power=5)),
                ])

            else:
                player.power = self.power

            return Action.set(*actions)


colors = [
    ('#222222', 'white'),
    ('orange', 'black'),
    ('red', 'black'),
    ('#ff4466', 'black'),
    ('#00aaff', 'black'),
    ('#ff44ff', 'black'),
]
