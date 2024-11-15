
import pygame
from pygame.mixer import Sound


class AudioBag:

    bullet: Sound
    explosions: list[Sound]

    @classmethod
    def init(cls) -> None:
        pygame.mixer.init()
        cls.bullet = Sound('assets/missile.wav')
        cls.explosions = [
            Sound('assets/explosion1.wav'),
            Sound('assets/explosion2.wav'),
        ]
