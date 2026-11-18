"""Small temporary sprites for visual effects."""

import pygame
from entities.base import GameObject


class Particle(GameObject):
    def __init__(self, x, y, vx, vy, life, color):
        super().__init__((3, 3), (round(x), round(y)))
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.life = life
        self.color = color
        self.draw()

    def update(self, dt):
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.vy += 45*dt
        self.life -= dt
        self.rect.center = (round(self.x), round(self.y))
        if self.life <= 0:
            self.kill()  # Sprite Groups remove dead particles automatically.
        else:
            self.draw()

    def draw(self):
        self.image.fill(self.color)
