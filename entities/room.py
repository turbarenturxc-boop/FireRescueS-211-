"""Room and its separate fire/person component classes."""

import math
import pygame
from config import ROOM_X, ROOM_Y, FIRE, ORANGE, GOLD, MINT, DARK, INK
from entities.base import GameObject


class RoomFire:
    """One room's fire: intensity, ignition, extinguishing and flame art."""

    def __init__(self):
        self._intensity = 0.0

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = max(0.0, min(1.7, float(value)))

    def ignite(self, strength=0.75):
        self.intensity += strength

    def spray(self, dt):
        if self.intensity <= 0:
            return False
        self.intensity -= 1.25 * dt
        if self.intensity <= 0.01:
            self.intensity = 0
            return True
        return False

    def draw(self, surface, clock):
        # Draw flames and smoke inside an already-drawn room window.
        for i in range(4):
            x = 12 + 6 * i
            wave = int(math.sin(clock * 13 + i * 2) * 3)
            top = 41 - min(10, int(self.intensity * 6)) + wave
            pygame.draw.polygon(surface, FIRE, [(x, 52), (x+6, 52), (x+3, top)])
            pygame.draw.polygon(surface, ORANGE,
                                [(x+2, 51), (x+5, 51), (x+3, top+6)])
        pygame.draw.rect(surface, GOLD, (18, 45, 8, 6))
        for k in range(2):
            smoke_y = 20 - int((clock * 10 + k * 9) % 18)
            pygame.draw.rect(surface, (83, 83, 101),
                             (17+k*7, smoke_y, 6, 4))


class Victim:
    """A person in a room: rescue progress and character art."""

    def __init__(self):
        self.rescued = False
        self.rescue_progress = 0.0

    def rescue(self, dt):
        if self.rescued:
            return False
        self.rescue_progress += dt
        if self.rescue_progress >= 0.85:
            self.rescued = True
            self.rescue_progress = 0.0
            return True
        return False

    def draw(self, surface, clock, col, font):
        wave = int(math.sin(clock * 9 + col) * 3)
        pygame.draw.rect(surface, MINT, (16, 40, 14, 13))
        pygame.draw.rect(surface, (235, 173, 123), (17, 28, 10, 10))
        pygame.draw.rect(surface, DARK, (17, 28, 10, 3))
        pygame.draw.rect(surface, INK, (23, 33, 2, 2))
        pygame.draw.line(surface, (235, 173, 123),
                         (29, 43), (35, 32+wave), 3)
        tag = font.render("HELP!", False, FIRE)
        pygame.draw.rect(surface, (247, 239, 204), (7, 1, 30, 12))
        surface.blit(tag, tag.get_rect(center=(22, 7)))


class Room(GameObject):
    """Room visual and location; COMPOSES a RoomFire and optional Victim."""

    def __init__(self, col, row):
        self.col = col
        self.row = row
        super().__init__((44, 68), (ROOM_X[col], ROOM_Y[row] - 6))
        self.flame = RoomFire()
        self.victim = None  # Victim object, or None if there is nobody here
        self.clock = 0.0
        self.flash = 0.0
        self.font = pygame.font.SysFont("consolas", 10, bold=True)
        self.draw()

    @property
    def fire(self):
        # Keep old Room API so the rest of the game does NOT need to change.
        return self.flame.intensity

    @fire.setter
    def fire(self, value):
        self.flame.intensity = value

    @property
    def needs_rescue(self):
        return self.victim is not None and not self.victim.rescued

    @property
    def rescue_progress(self):
        return self.victim.rescue_progress if self.victim else 0.0

    @rescue_progress.setter
    def rescue_progress(self, value):
        if self.victim is not None and not self.victim.rescued:
            self.victim.rescue_progress = max(0.0, float(value))

    @property
    def x(self):
        return ROOM_X[self.col]

    @property
    def y(self):
        return ROOM_Y[self.row]

    def ignite(self, strength=0.75):
        self.flame.ignite(strength)
        self.flash = 0.30

    def add_victim(self):
        self.victim = Victim()

    def spray(self, dt):
        if self.flame.spray(dt):
            self.flash = 0.30
            return True
        return False

    def rescue(self, dt):
        # Room imposes the rule: extinguish the fire BEFORE saving someone.
        if self.fire > 0 or not self.needs_rescue:
            return False
        if self.victim.rescue(dt):
            self.flash = 0.40
            return True
        return False

    def update(self, dt):
        self.clock += dt
        self.flash = max(0.0, self.flash - dt)
        self.draw()

    def draw(self):
        s = self.image
        s.fill((0, 0, 0, 0))
        # Room background and window.
        pygame.draw.rect(s, (67, 40, 55), (5, 15, 35, 46))
        pygame.draw.rect(s, (237, 190, 128), (7, 15, 30, 42))
        pygame.draw.rect(s, (26, 32, 59), (10, 18, 24, 36))
        if self.fire <= 0:
            pygame.draw.rect(s, (54, 98, 120), (12, 21, 20, 30))
            pygame.draw.rect(s, (87, 146, 159), (12, 21, 7, 27))
        else:
            pygame.draw.rect(s, (109, 48, 47), (11, 20, 22, 32))
            self.flame.draw(s, self.clock)
        if self.needs_rescue:
            self.victim.draw(s, self.clock, self.col, self.font)
        # Keep the window framing ON TOP of fire/person graphics.
        pygame.draw.rect(s, (251, 212, 157), (20, 18, 4, 35))
        pygame.draw.rect(s, (253, 220, 167), (8, 35, 28, 3))
        pygame.draw.rect(s, (89, 49, 59), (5, 56, 35, 5))
        pygame.draw.rect(s, (243, 194, 133), (4, 54, 36, 3))
        if self.flash > 0:
            pygame.draw.rect(s, GOLD, (7, 15, 30, 42), 2)
