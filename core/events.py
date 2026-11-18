"""Custom Pygame events, published by gameplay and consumed by observers."""

import pygame

FIRE_OUT = pygame.USEREVENT + 1
PERSON_SAVED = pygame.USEREVENT + 2
PLAYER_HIT = pygame.USEREVENT + 3
SURVIVAL_BONUS = pygame.USEREVENT + 4

def announce(event_type, **data):
    """Post a fact to Pygame's event queue, without changing score directly."""
    pygame.event.post(pygame.event.Event(event_type, data))
