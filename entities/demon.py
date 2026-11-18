"""Moving fire demon and projectile creation."""

import math
import pygame
from config import FIRE, ORANGE, GOLD
from entities.base import GameObject
from entities.hazards import Fireball


class FireDemon(GameObject):
    def __init__(self):
        super().__init__((52, 58), (160, 74))
        self.time = 0.0
        self.attack_flash = 0.0
        self.draw()

    @property
    def x(self):
        return self.rect.centerx

    def throw_fire(self, room, threat):
        """Factory Method: create the appropriate projectile for the target."""
        self.attack_flash = 0.35
        duration = max(0.80, 1.65 - 0.075*(threat-1))
        return Fireball(self.x, room, duration)

    def update(self, dt):
        self.time += dt
        self.attack_flash = max(0, self.attack_flash - dt)
        self.rect.center = (round(160+61*math.sin(self.time*1.35)),
                            round(74+2*math.sin(self.time*5)))
        self.draw()

    def draw(self):
        s = self.image
        s.fill((0, 0, 0, 0))
        r = pygame.draw.rect
        r(s, (40, 23, 46), (8, 39, 36, 5))
        r(s, (111, 36, 60), (15, 25, 22, 17))
        r(s, FIRE, (16, 24, 20, 15))
        r(s, ORANGE, (14, 10, 24, 19))
        r(s, FIRE, (15, 2, 6, 14))
        r(s, FIRE, (31, 2, 6, 14))
        r(s, GOLD, (17, 16, 6, 6))
        r(s, GOLD, (29, 16, 6, 6))
        r(s, (27, 23, 48), (20, 18, 3, 3))
        r(s, (27, 23, 48), (30, 18, 3, 3))
        r(s, (61, 25, 48), (22, 28, 8, 3))
        r(s, ORANGE, (12, 32, 7, 8))
        r(s, ORANGE, (34, 30 if self.attack_flash else 33, 8, 8))
        if self.attack_flash:
            r(s, GOLD, (40, 22, 9, 9))
