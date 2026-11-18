"""Firefighter player sprite with encapsulated lives."""

import pygame
from config import ROWS, COLS, ROOM_X, ROOM_Y, GOLD, FIRE, BLUE
from entities.base import GameObject


class Firefighter(GameObject):
    def __init__(self):
        self.col, self.row = 2, ROWS - 1
        self.x = float(ROOM_X[self.col])
        self.feet_y = float(ROOM_Y[self.row] + 25)
        super().__init__((40, 56), (round(self.x), round(self.feet_y - 19)))
        self._lives = 3
        self.invincible = 1.5
        self.action = False
        self.action_progress = 0.0
        self.clock = 0.0
        self.old_hitbox = self.hitbox
        self.draw()

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        """Encapsulation keeps health between zero and three hearts."""
        self._lives = max(0, min(3, int(value)))

    @property
    def hitbox(self):
        # Tight hitbox around head/body/boots, not the transparent sprite edges.
        return pygame.Rect(round(self.x)-11, round(self.feet_y)-42, 23, 48)

    @property
    def swept_hitbox(self):
        return self.old_hitbox.union(self.hitbox)

    @property
    def arrived(self):
        return (abs(ROOM_X[self.col]-self.x) < 3
                and abs(ROOM_Y[self.row]+25-self.feet_y) < 3)

    def move(self, dc, dr):
        self.col = max(0, min(COLS-1, self.col+dc))
        self.row = max(0, min(ROWS-1, self.row+dr))
        self.action_progress = 0.0

    def take_damage(self):
        if self.invincible > 0:
            return False
        self.lives -= 1
        self.invincible = 2.0
        return True

    def update(self, dt):
        self.old_hitbox = self.hitbox
        self.clock += dt
        self.invincible = max(0, self.invincible - dt)
        speed = min(1, dt*17)
        self.x += (ROOM_X[self.col]-self.x)*speed
        self.feet_y += (ROOM_Y[self.row]+25-self.feet_y)*speed
        self.rect.center = (round(self.x), round(self.feet_y-19))
        self.draw()

    def draw(self):
        s = self.image
        s.fill((0, 0, 0, 0))
        if self.invincible > 0 and int(self.clock * 12) % 2 == 0:
            return
        # Sprite 40x56, feet at local y=49.
        r = pygame.draw.rect
        r(s, (39, 47, 79), (12, 39, 7, 10))
        r(s, (39, 47, 79), (23, 39, 7, 10))
        r(s, GOLD, (12, 46, 7, 3))
        r(s, GOLD, (23, 46, 7, 3))
        r(s, (28, 31, 49), (10, 49, 10, 4))
        r(s, (28, 31, 49), (22, 49, 10, 4))
        r(s, (121, 161, 176), (7, 23, 7, 17))
        r(s, BLUE, (8, 26, 4, 10))
        r(s, (216, 65, 58), (10, 23, 20, 17))
        r(s, GOLD, (10, 30, 20, 4))
        r(s, GOLD, (18, 23, 4, 15))
        r(s, (238, 169, 118), (13, 12, 15, 13))
        r(s, (38, 42, 62), (21, 17, 6, 3))
        r(s, (249, 223, 134), (8, 7, 24, 6))
        r(s, (240, 190, 79), (11, 3, 18, 9))
        r(s, FIRE, (15, 4, 10, 4))
        r(s, (238, 160, 115), (7, 26, 4, 11))
        r(s, (238, 160, 115), (30, 26, 4, 11))
        r(s, (155, 173, 177), (29, 29, 11, 4))
        if self.action:
            for i in range(4):
                r(s, BLUE, (30-i*5, 22-i*3, 3, 3))
        if self.action_progress > 0:
            r(s, (10, 19, 35), (3, 0, 34, 5))
            r(s, BLUE, (4, 1, int(32*self.action_progress), 3))
