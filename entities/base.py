"""Abstract sprite contract (SF211 Week 10 and 11)."""

import pygame
from abc import ABC, abstractmethod


class GameObject(pygame.sprite.Sprite, ABC):
    """Every concrete sprite must update its behavior and draw its pixels."""

    def __init__(self, size, center):
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)

    @abstractmethod
    def update(self, dt):
        """Advance one simulation step. Called by all_sprites.update(dt)."""

    @abstractmethod
    def draw(self):
        """Refresh self.image so that all_sprites.draw(screen) can display it."""
