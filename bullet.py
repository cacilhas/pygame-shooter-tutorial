
import math
from pygame import Surface
import pygame
from pygame.mixer import Sound
from actor import Action, Actor
from consts import RESOLUTION


class Bullet(Actor):

    facet: Surface|None = None
    sound: Sound|None = None

    @classmethod
    def load_texture(cls) -> None:
        cls.facet = pygame.transform.scale(
            pygame.image.load('assets/bullet.png').convert_alpha(),
            (12, 12),
        )
        cls.sound = Sound('assets/missile.wav')

    def __init__(self, pos: tuple[float, float], angle: float) -> None:
        self.x, self.y = pos
        self.angle = angle
        self.speed = 1200.0

        if Bullet.facet is None:
            Bullet.load_texture()
        assert Bullet.sound
        Bullet.sound.play()

    @property
    def pos(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    async def draw(self, surface: Surface) -> None:
        facet = Bullet.facet
        assert facet
        x = int(self.x - facet.get_width() / 2)
        y = int(self.y - facet.get_height() / 2)
        surface.blit(facet, (x, y))

    async def update(self, delta: float) -> Action:
        facet = Bullet.facet
        assert facet
        width, height = facet.get_size()
        speed = self.speed * delta
        dx, dy = math.cos(self.angle) * speed, math.sin(self.angle) * speed
        self.x += dx
        self.y += dy

        if not -width / 2 < self.x < RESOLUTION[0] + width / 2:
            return Action.remove(self)
        if not -height / 2 < self.y < RESOLUTION[1] + height / 2:
            return Action.remove(self)
        return Action.noAction
