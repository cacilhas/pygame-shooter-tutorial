from typing import Optional
import pygame
from pygame.surface import Surface
from action import Action, Collider
from sounds import AudioBag


class FoeForceField(Collider):

    def __init__(self, pos: tuple[float, float], speed: float) -> None:
        self.x, self.y = pos
        self.size = 12
        self.speed = speed
        self.facet = Surface((1, 1), pygame.SRCALPHA)

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def radius(self) -> float:
        return self.size

    async def draw(self, surface: Surface) -> None:
        return self.blit(dest=surface, src=self.facet)

    async def update(self, delta: float) -> Optional[Action]:
        self.size += self.size * 5 * delta
        self.x -= self.speed * delta

        if self.size > 120:
            return Action.remove(self)

        facet = self.facet = Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.arc(facet, 'yellow', facet.get_rect(), 0.0, 360.0, width=4)

    async def on_collision(self, other: Collider) -> Optional[Action]:
        from shield import Shield
        if isinstance(other, Shield):
            return Action.set(
                Action.remove(self),
                Action.play_audio(AudioBag.explosions[0]),
            )
