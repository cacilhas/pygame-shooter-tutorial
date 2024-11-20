import pygame
from pygame.mixer import Sound


class AudioBag:
    bullet: Sound
    explosions: list[Sound]

    @classmethod
    def init(cls) -> None:
        pygame.mixer.init()
        cls.bullet = Sound("assets/missile.wav")
        cls.catch = Sound("assets/catch.wav")
        cls.explosions = [
            Sound("assets/explosion1.wav"),
            Sound("assets/explosion2.wav"),
        ]
        cls.laser = Sound("assets/laser.wav")
        cls.power_down = Sound("assets/power-down.wav")
        cls.power_up = Sound("assets/power-up.wav")
