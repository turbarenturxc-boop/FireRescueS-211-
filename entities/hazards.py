"""Debris and fireballs: inheritance and motion overriding."""

import math
import pygame
from config import FIRE, ORANGE, GOLD
from entities.base import GameObject


class Hazard(GameObject):
    """Shared collision sweep; subclasses define their own motion and art."""

    def __init__(self, size, x, y):
        super().__init__(size, (round(x), round(y)))
        self.x = float(x)
        self.y = float(y)
        self.old_hitbox = self.hitbox
        self.landed = False

    @property
    def hitbox(self):
        return pygame.Rect(round(self.x)-8, round(self.y)-8, 16, 16)

    @property
    def swept_hitbox(self):
        # Union checks all positions between the old and new positions in a frame.
        return self.old_hitbox.union(self.hitbox)

    def remember_position(self):
        self.old_hitbox = self.hitbox


class Debris(Hazard):
    """A falling chunk of masonry. It can hit the firefighter MID-FALL."""

    def __init__(self, x, speed):
        super().__init__((22, 22), x, 101)
        self.speed = speed
        self.clock = 0.0
        self.draw()

    def update(self, dt):
        self.remember_position()
        self.y += self.speed * dt
        self.clock += dt
        self.rect.center = (round(self.x), round(self.y))
        self.landed = self.y > 435
        self.draw()

    def draw(self):
        s = self.image
        s.fill((0, 0, 0, 0))
        pygame.draw.rect(s, (32, 28, 48), (2, 3, 18, 17))
        pygame.draw.rect(s, (104, 104, 117), (3, 4, 15, 14))
        shift = 1 if math.sin(self.clock*11) >= 0 else -1
        pygame.draw.rect(s, (175, 156, 145), (6+shift, 5, 8, 4))
        pygame.draw.rect(s, (73, 77, 92), (7, 12, 9, 5))
        pygame.draw.rect(s, GOLD, (14, 9, 3, 3))


class Fireball(Hazard):
    """Fire demon's projectile: moves towards one room and sets it on fire."""

    def __init__(self, start_x, target_room, duration=1.5):
        super().__init__((24, 28), start_x, 79)
        self.start_x = start_x
        self.start_y = 79.0
        self.target_room = target_room
        self.duration = max(0.4, duration)
        self.age = 0.0
        self.draw()

    def update(self, dt):
        self.remember_position()
        self.age = min(self.duration, self.age + dt)
        p = self.age/self.duration
        self.x = (self.start_x + (self.target_room.x-self.start_x)*p
                  + math.sin(p*math.pi)*7)
        self.y = (self.start_y + (self.target_room.y+9-self.start_y)*p
                  - math.sin(p*math.pi)*15)
        self.rect.center = (round(self.x), round(self.y))
        self.landed = p >= 1
        self.draw()

    def draw(self):
        s = self.image
        s.fill((0, 0, 0, 0))
        pygame.draw.rect(s, (123, 35, 58), (4, 8, 16, 16))
        pygame.draw.rect(s, FIRE, (5, 5, 14, 19))
        pygame.draw.polygon(s, FIRE, [(9, 8), (12, 0), (15, 8)])
        pygame.draw.polygon(s, ORANGE, [(7, 18), (11, 6), (17, 20)])
        pygame.draw.rect(s, GOLD, (10, 15, 5, 7))
